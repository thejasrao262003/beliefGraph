"""Serve a small open model on Modal with vLLM's OpenAI-compatible API, for BeliefGraph's
`modal` provider. The model is chosen at deploy time (default Qwen3.5-9B); each model gets its
own app, so several can be evaluated at once:

    BG_MODEL=Qwen/Qwen3.5-4B uv run --group modal modal deploy deploy/modal_qwen.py
    # -> app beliefgraph-qwen3-5-4b, served model name qwen3.5-4b

    export BELIEFGRAPH_VLLM_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
    uv run --group modal modal secret create beliefgraph-vllm VLLM_API_KEY=$BELIEFGRAPH_VLLM_KEY
    uv run --group modal modal deploy deploy/modal_qwen.py
    export BELIEFGRAPH_VLLM_URL=https://<workspace>--beliefgraph-qwen35-9b-server.modal.run/v1
    beliefgraph revise snapshot.json --provider modal --model qwen3.5-9b

Cost control: one GPU container at most, scaled to zero after 5 idle minutes. The
endpoint is reachable on the internet but vLLM rejects any request without
BELIEFGRAPH_VLLM_KEY, stored in the Modal secret `beliefgraph-vllm` and never committed.
Stop everything with `modal app stop beliefgraph-qwen35-9b`.
"""

import subprocess

import modal

import os
import re

MODEL = os.environ.get("BG_MODEL", "Qwen/Qwen3.5-9B")  # read at deploy time, baked into the image env
SERVED_NAME = MODEL.split("/")[-1].lower().replace("-instruct", "")
SLUG = re.sub(r"[^a-z0-9]+", "-", SERVED_NAME).strip("-")
QWEN35 = "qwen3.5" in MODEL.lower()  # hybrid Gated-DeltaNet architecture, multimodal checkpoint
PORT = 8000
MINUTES = 60
MAX_MODEL_LEN = int(os.environ.get("BG_MAX_MODEL_LEN", 131072 if QWEN35 else 49152))
GPU = "H100" if MODEL == "Qwen/Qwen3.5-9B" else "L40S"  # up to ~12B in bf16 fits a 48 GB L40S
# Gemma 4 (gemma4_unified) needs a newer vLLM than the one the Qwen runs were made with.
VLLM = "vllm==0.31.0" if MODEL.startswith("google/gemma-4") else "vllm==0.21.0"
# Per-family serving flags (vLLM docs / model cards).
EXTRA = {
    # Served at vLLM defaults like every other model. (The model card recommends temperature <0.1;
    # at 0.05 the router abstained on 87/143 memories and balanced accuracy fell 0.777 -> 0.665.)
    "mistralai/": ["--tokenizer-mode", "mistral", "--config-format", "mistral", "--load-format", "mistral"],
    # Qwen3-Reranker as a cross-encoder scorer (/score, /rerank): P("yes") from the no/yes logits
    "Qwen/Qwen3-Reranker": ["--runner", "pooling", "--hf-overrides",
                            '{"architectures": ["Qwen3ForSequenceClassification"], '
                            '"classifier_from_token": ["no", "yes"], "is_original_qwen3_reranker": true}'],
}

image = (
    modal.Image.from_registry("nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12")
    .entrypoint([])
    .uv_pip_install(VLLM)
    .env({"HF_XET_HIGH_PERFORMANCE": "1", "BG_MODEL": MODEL, "BG_MAX_MODEL_LEN": str(MAX_MODEL_LEN)})
)
hf_cache = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
vllm_cache = modal.Volume.from_name("vllm-cache", create_if_missing=True)
flashinfer_cache = modal.Volume.from_name("flashinfer-cache", create_if_missing=True)

# The API key lives in a named Modal secret, referenced unconditionally (objects defined
# under a local-only condition break container hydration). Create it once with:
#   modal secret create beliefgraph-vllm VLLM_API_KEY=$BELIEFGRAPH_VLLM_KEY
secrets = [modal.Secret.from_name("beliefgraph-vllm", required_keys=["VLLM_API_KEY"])]

app = modal.App("beliefgraph-qwen35-9b" if MODEL == "Qwen/Qwen3.5-9B" else f"beliefgraph-{SLUG}")


@app.server(
    image=image,
    gpu=GPU,
    port=PORT,
    # Weights, torch.compile artifacts and FlashInfer JIT kernels persist across cold starts.
    volumes={"/root/.cache/huggingface": hf_cache, "/root/.cache/vllm": vllm_cache,
             "/root/.cache/flashinfer": flashinfer_cache},
    secrets=secrets,
    max_containers=1,
    scaledown_window=5 * MINUTES,  # idle containers stop after 5 minutes (the user asked to keep idle cost down)
    startup_timeout=20 * MINUTES,
    unauthenticated=True,  # reachable without Modal auth; vLLM itself requires the API key
)
class Server:
    @modal.enter()
    def start(self):
        qwen35 = [
            "--reasoning-parser", "qwen3",  # thinking goes to reasoning_content, the answer to content
            "--language-model-only",
            # Qwen3.5's Gated-DeltaNet layers otherwise JIT-compile a FlashInfer prefill kernel on
            # every cold start (vLLM's own log suggests this flag to avoid it).
            "--gdn-prefill-backend", "triton",
        ]
        self.proc = subprocess.Popen([
            "vllm", "serve", MODEL,
            "--served-model-name", SERVED_NAME,
            "--host", "0.0.0.0", "--port", str(PORT),
            "--max-model-len", str(MAX_MODEL_LEN),
            *(qwen35 if QWEN35 else []),
            *next((v for k, v in EXTRA.items() if MODEL.startswith(k)), []),
        ])

    @modal.exit()
    def stop(self):
        self.proc.terminate()
