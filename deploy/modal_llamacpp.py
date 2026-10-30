"""Serve a GGUF model with llama.cpp's OpenAI-compatible llama-server on Modal (the edge-device
runtime), for the quantization study. Same protocol, API key and provider (`modal`) as
deploy/modal_qwen.py. Built from upstream ggml-org/llama.cpp (KV cache types f16, q8_0, q4_0, ...).
BG_LLAMA_REPO/BG_LLAMA_REF build another tree instead, e.g. a TurboQuant fork with turbo3/turbo4.

    BG_GGUF=gemma-4-12b-it-Q4_K_M.gguf uv run --group modal modal deploy deploy/modal_llamacpp.py
    # -> app beliefgraph-gguf-gemma-4-12b-it-q4-k-m, served model name gguf-gemma-4-12b-it-q4_k_m
    BG_GGUF=gemma-4-12b-it-Q4_K_M.gguf BG_CTK=q4_0 BG_CTV=q4_0 uv run --group modal modal deploy deploy/modal_llamacpp.py
    # -> ...-q4_k_m-kv-q4_0-q4_0

One GPU container at most, scaled to zero after 5 idle minutes; llama-server rejects requests
without BELIEFGRAPH_VLLM_KEY (Modal secret `beliefgraph-vllm`).
"""

import os
import re
import subprocess

import modal

REPO = os.environ.get("BG_GGUF_REPO", "unsloth/gemma-4-12b-it-GGUF")
GGUF = os.environ.get("BG_GGUF", "gemma-4-12b-it-Q4_K_M.gguf")
CTK = os.environ.get("BG_CTK", "f16")  # KV cache types: f16, q8_0, q4_0, ...
CTV = os.environ.get("BG_CTV", "f16")
CTX = int(os.environ.get("BG_CTX", 131072))  # one KV cache shared by all slots (--kv-unified)
SLOTS = int(os.environ.get("BG_SLOTS", 16))
SERVED_NAME = "gguf-" + GGUF.removesuffix(".gguf").lower() + ("" if (CTK, CTV) == ("f16", "f16") else f"-kv-{CTK}-{CTV}")
SLUG = re.sub(r"[^a-z0-9]+", "-", SERVED_NAME).strip("-")
LLAMA_REPO = os.environ.get("BG_LLAMA_REPO", "https://github.com/ggml-org/llama.cpp")
LLAMA_REF = os.environ.get("BG_LLAMA_REF", "master")
PORT = 8000
MINUTES = 60

image = (
    modal.Image.from_registry("nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12")
    .entrypoint([])
    .apt_install("git", "cmake", "build-essential", "libcurl4-openssl-dev")
    .run_commands(
        f"git clone --depth 1 --branch {LLAMA_REF} {LLAMA_REPO} /llama.cpp",
        # 8.9 = L40S; the CUDA driver stub lets the build link without a GPU
        "cd /llama.cpp && cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=89 -DLLAMA_CURL=OFF "
        "-DCMAKE_EXE_LINKER_FLAGS=-Wl,--allow-shlib-undefined && cmake --build build --config Release -j 16 --target llama-server",
    )
    .uv_pip_install("huggingface_hub[hf_xet]")
    .env({"HF_XET_HIGH_PERFORMANCE": "1", "BG_GGUF_REPO": REPO, "BG_GGUF": GGUF, "BG_CTK": CTK, "BG_CTV": CTV,
          "BG_CTX": str(CTX), "BG_SLOTS": str(SLOTS)})
)
hf_cache = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
secrets = [modal.Secret.from_name("beliefgraph-vllm", required_keys=["VLLM_API_KEY"])]

app = modal.App(f"beliefgraph-{SLUG}")


@app.server(
    image=image,
    gpu="L40S",
    port=PORT,
    volumes={"/root/.cache/huggingface": hf_cache},
    secrets=secrets,
    max_containers=1,
    scaledown_window=5 * MINUTES,
    startup_timeout=20 * MINUTES,
    unauthenticated=True,  # reachable without Modal auth; llama-server itself requires the API key
)
class Server:
    @modal.enter()
    def start(self):
        from huggingface_hub import hf_hub_download

        path = hf_hub_download(REPO, GGUF)
        self.proc = subprocess.Popen([
            "/llama.cpp/build/bin/llama-server", "-m", path,
            "--alias", SERVED_NAME,
            "--host", "0.0.0.0", "--port", str(PORT),
            "--api-key", os.environ["VLLM_API_KEY"],
            "--jinja",  # the model's own chat template (as vLLM uses)
            "-ngl", "999", "-fa", "on",
            "-c", str(CTX), "-np", str(SLOTS), "--kv-unified",
            "--cache-type-k", CTK, "--cache-type-v", CTV,
            # vLLM serves Gemma 4 without thinking unless asked; llama.cpp's template default thinks
            "--chat-template-kwargs", '{"enable_thinking": false}',
        ])

    @modal.exit()
    def stop(self):
        self.proc.terminate()
