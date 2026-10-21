"""Serve a small open model (Qwen3.5-9B) on Modal with vLLM's OpenAI-compatible API, for
BeliefGraph's `modal` provider.

    export BELIEFGRAPH_VLLM_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
    uv run --group modal modal deploy deploy/modal_qwen.py
    export BELIEFGRAPH_VLLM_URL=https://<workspace>--beliefgraph-qwen35-9b-server.modal.run/v1
    beliefgraph revise snapshot.json --provider modal --model qwen3.5-9b

Cost control: one GPU container at most, scaled to zero after 5 idle minutes. The
endpoint is reachable on the internet but vLLM rejects any request without
BELIEFGRAPH_VLLM_KEY, which is read on your machine at deploy time and never committed.
Stop everything with `modal app stop beliefgraph-qwen35-9b`.
"""

import os
import subprocess

import modal

MODEL = "Qwen/Qwen3.5-9B"  # Apache-2.0; 262k native context; thinking + non-thinking modes
SERVED_NAME = "qwen3.5-9b"
PORT = 8000
MINUTES = 60
MAX_MODEL_LEN = 131072  # enough for the full 301-memory store (~45k tokens) with room to think

image = (
    modal.Image.from_registry("nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12")
    .entrypoint([])
    .uv_pip_install("vllm==0.21.0")
    .env({"HF_XET_HIGH_PERFORMANCE": "1"})
)
hf_cache = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
vllm_cache = modal.Volume.from_name("vllm-cache", create_if_missing=True)

_key = os.environ.get("BELIEFGRAPH_VLLM_KEY")
if modal.is_local() and not _key:
    raise SystemExit("set BELIEFGRAPH_VLLM_KEY before deploying (the server must not run without a key)")
secrets = [modal.Secret.from_dict({"VLLM_API_KEY": _key})] if _key else []

app = modal.App("beliefgraph-qwen35-9b")


@app.server(
    image=image,
    gpu="L40S",  # 48 GB: 9B weights in BF16 plus KV cache for long stores
    port=PORT,
    volumes={"/root/.cache/huggingface": hf_cache, "/root/.cache/vllm": vllm_cache},
    secrets=secrets,
    max_containers=1,
    scaledown_window=5 * MINUTES,
    startup_timeout=20 * MINUTES,
    unauthenticated=True,  # reachable without Modal auth; vLLM itself requires the API key
)
class Server:
    @modal.enter()
    def start(self):
        self.proc = subprocess.Popen([
            "vllm", "serve", MODEL,
            "--served-model-name", SERVED_NAME,
            "--host", "0.0.0.0", "--port", str(PORT),
            "--max-model-len", str(MAX_MODEL_LEN),
            "--reasoning-parser", "qwen3",  # thinking goes to reasoning_content, the answer to content
            "--language-model-only",
        ])

    @modal.exit()
    def stop(self):
        self.proc.terminate()
