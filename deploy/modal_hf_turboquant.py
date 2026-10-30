"""Serve Gemma-4-12B with a TurboQuant KV cache (deploy/turboquant.py, written from the paper) on
Hugging Face transformers, behind the same OpenAI-compatible protocol and API key as
deploy/modal_qwen.py. vLLM's own TurboQuant does not run on Gemma 4 (its 512-wide global heads
force the Triton attention backend, which rejects TurboQuant cache types).

    BG_TQ_BITS=3 uv run --group modal modal deploy deploy/modal_hf_turboquant.py
    # -> app beliefgraph-hf-tq3, served model name hf-gemma-4-12b-it-tq3
    BG_TQ_BITS=0 ...    # same server, plain bf16 cache: the reference for this runtime
    BG_TQ_LAYERS=full   # quantize only full-attention layers (as vLLM's TurboQuant does)

transformers serves one request at a time per container, so Modal scales out to BG_CONTAINERS
GPU containers under load; they stop after 5 idle minutes.
"""

import os
import subprocess

import modal

MODEL = os.environ.get("BG_MODEL", "google/gemma-4-12B-it")
BITS = int(os.environ.get("BG_TQ_BITS", "3"))
LAYERS = os.environ.get("BG_TQ_LAYERS", "all")
CONTAINERS = int(os.environ.get("BG_CONTAINERS", "6"))
TAG = (f"tq{BITS}" if BITS else "bf16") + ("-full" if BITS and LAYERS == "full" else "")
SERVED_NAME = f"hf-{MODEL.split('/')[-1].lower()}-{TAG}"
PORT = 8000
MINUTES = 60

image = (
    modal.Image.debian_slim(python_version="3.12")
    .uv_pip_install("torch>=2.9", "transformers==5.22.1", "accelerate", "numpy", "fastapi", "uvicorn",
                    "huggingface_hub[hf_xet]")
    .env({"HF_XET_HIGH_PERFORMANCE": "1", "BG_MODEL": MODEL, "BG_SERVED_NAME": SERVED_NAME,
          "BG_TQ_BITS": str(BITS), "BG_TQ_LAYERS": LAYERS})
    .add_local_file("deploy/turboquant.py", "/srv/turboquant.py")
    .add_local_file("deploy/hf_server.py", "/srv/hf_server.py")
)
hf_cache = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
secrets = [modal.Secret.from_name("beliefgraph-vllm", required_keys=["VLLM_API_KEY"])]

app = modal.App(f"beliefgraph-hf-{TAG}")


@app.server(
    image=image,
    gpu="L40S",
    port=PORT,
    volumes={"/root/.cache/huggingface": hf_cache},
    secrets=secrets,
    target_concurrency=1,  # one request per container; queued requests wait for the next free one
    max_containers=CONTAINERS,
    scaledown_window=5 * MINUTES,
    startup_timeout=20 * MINUTES,
    unauthenticated=True,  # reachable without Modal auth; the server itself requires the API key
)
class Server:
    @modal.enter()
    def start(self):
        self.proc = subprocess.Popen(["uvicorn", "hf_server:app", "--host", "0.0.0.0", "--port", str(PORT),
                                      "--timeout-keep-alive", "1800"], cwd="/srv")

    @modal.exit()
    def stop(self):
        self.proc.terminate()
