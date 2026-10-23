"""Serve a small open model (Qwen3.5-9B) on Modal with vLLM's OpenAI-compatible API, for
BeliefGraph's `modal` provider.

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

MODEL = "Qwen/Qwen3.5-9B"  # Apache-2.0; 262k native context; thinking + non-thinking modes
SERVED_NAME = "qwen3.5-9b"
PORT = 8000
MINUTES = 60
MAX_MODEL_LEN = 131072  # LLM-direct on the full store: ~50k-token prompt + 16k output, with headroom

image = (
    modal.Image.from_registry("nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12")
    .entrypoint([])
    .uv_pip_install("vllm==0.21.0")
    .env({"HF_XET_HIGH_PERFORMANCE": "1"})
)
hf_cache = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
vllm_cache = modal.Volume.from_name("vllm-cache", create_if_missing=True)
flashinfer_cache = modal.Volume.from_name("flashinfer-cache", create_if_missing=True)

# The API key lives in a named Modal secret, referenced unconditionally (objects defined
# under a local-only condition break container hydration). Create it once with:
#   modal secret create beliefgraph-vllm VLLM_API_KEY=$BELIEFGRAPH_VLLM_KEY
secrets = [modal.Secret.from_name("beliefgraph-vllm", required_keys=["VLLM_API_KEY"])]

app = modal.App("beliefgraph-qwen35-9b")


@app.server(
    image=image,
    gpu="H100",  # 80 GB: fast prefill and decoding for long stores and thinking outputs
    port=PORT,
    # Weights, torch.compile artifacts and FlashInfer JIT kernels persist across cold starts.
    volumes={"/root/.cache/huggingface": hf_cache, "/root/.cache/vllm": vllm_cache,
             "/root/.cache/flashinfer": flashinfer_cache},
    secrets=secrets,
    max_containers=1,
    scaledown_window=20 * MINUTES,  # stay warm between experiment calls; idle cost stops after this
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
            # Qwen3.5's Gated-DeltaNet layers otherwise JIT-compile a FlashInfer prefill kernel on
            # every cold start (vLLM's own log suggests this flag to avoid it).
            "--gdn-prefill-backend", "triton",
        ])

    @modal.exit()
    def stop(self):
        self.proc.terminate()
