"""Minimal OpenAI-compatible chat server on Hugging Face transformers, with a TurboQuant KV cache
(deploy/turboquant.py). Covers what BeliefGraph and the baselines send: system/user/assistant
messages, max_tokens, temperature, top_p, seed, logprobs/top_logprobs, an assistant prefill
continued with continue_final_message, chat_template_kwargs. One request at a time per process.

Environment: BG_MODEL, BG_SERVED_NAME, BG_TQ_BITS (0 = plain bf16 cache), BG_TQ_LAYERS
(all | full), VLLM_API_KEY.
"""

from __future__ import annotations

import os
import threading
import time
import uuid

import torch
from fastapi import FastAPI, HTTPException, Request
from transformers import AutoModelForImageTextToText, AutoTokenizer, DynamicCache

from turboquant import TurboQuantCache, distortion_check

MODEL = os.environ["BG_MODEL"]
SERVED_NAME = os.environ["BG_SERVED_NAME"]
BITS = int(os.environ.get("BG_TQ_BITS", "0"))
LAYERS = os.environ.get("BG_TQ_LAYERS", "all")
KEY = os.environ["VLLM_API_KEY"]

tok = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForImageTextToText.from_pretrained(MODEL, dtype=torch.bfloat16, device_map="cuda").eval()
lock = threading.Lock()
app = FastAPI()
print(f"{SERVED_NAME}: TurboQuant bits={BITS} layers={LAYERS}; unit-vector distortion "
      f"d=256 {distortion_check(256)}, d=512 {distortion_check(512)}", flush=True)


def _auth(request: Request) -> None:
    if request.headers.get("authorization", "") != f"Bearer {KEY}":
        raise HTTPException(401, "bad api key")


@app.get("/v1/models")
def models(request: Request):
    _auth(request)
    return {"object": "list", "data": [{"id": SERVED_NAME, "object": "model", "owned_by": "beliefgraph"}]}


def _entry(token_id: int, logprobs: torch.Tensor, k: int) -> dict:
    top = torch.topk(logprobs, k)
    return {"token": tok.decode([token_id]), "logprob": float(logprobs[token_id]),
            "top_logprobs": [{"token": tok.decode([int(i)]), "logprob": float(v)}
                             for v, i in zip(top.values, top.indices)]}


@app.post("/v1/chat/completions")
def chat(request: Request, body: dict):
    _auth(request)
    messages = [{"role": m["role"], "content": m["content"]} for m in body["messages"]]
    cont = bool(body.get("continue_final_message")) and messages[-1]["role"] == "assistant"
    enc = tok.apply_chat_template(messages, tokenize=True, return_dict=True, return_tensors="pt",
                                  add_generation_prompt=not cont, continue_final_message=cont,
                                  **(body.get("chat_template_kwargs") or {}))
    ids = enc["input_ids"].to("cuda")
    gen = {"max_new_tokens": int(body.get("max_tokens") or 2048)}
    temperature = body.get("temperature")
    if temperature is not None and float(temperature) == 0:
        gen["do_sample"] = False
    else:  # the model's generation_config defaults otherwise, as vLLM serves them
        if temperature is not None:
            gen["temperature"] = float(temperature)
        if body.get("top_p") is not None:
            gen["top_p"] = float(body["top_p"])
    want_lp = bool(body.get("logprobs"))
    k = int(body.get("top_logprobs") or 1)
    with lock:
        torch.manual_seed(int(body["seed"]) if body.get("seed") is not None else int(time.time_ns() % 2**31))
        cache = TurboQuantCache(model.config, BITS, LAYERS) if BITS else DynamicCache(config=model.config)
        with torch.inference_mode():
            out = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids), past_key_values=cache,
                                 return_dict_in_generate=True, output_logits=want_lp, **gen)
    new = out.sequences[0, ids.shape[1]:].tolist()
    eos = set(model.generation_config.eos_token_id if isinstance(model.generation_config.eos_token_id, list)
              else [model.generation_config.eos_token_id])
    finish = "stop" if new and new[-1] in eos else ("length" if len(new) >= gen["max_new_tokens"] else "stop")
    choice = {"index": 0, "finish_reason": finish,
              "message": {"role": "assistant", "content": tok.decode(new, skip_special_tokens=True)}}
    if want_lp:
        choice["logprobs"] = {"content": [_entry(t, torch.log_softmax(lg[0].float(), -1), k)
                                          for t, lg in zip(new, out.logits)]}
    return {"id": f"chatcmpl-{uuid.uuid4().hex}", "object": "chat.completion", "created": int(time.time()),
            "model": SERVED_NAME, "choices": [choice],
            "usage": {"prompt_tokens": ids.shape[1], "completion_tokens": len(new),
                      "total_tokens": ids.shape[1] + len(new)}}
