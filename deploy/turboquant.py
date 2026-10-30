"""TurboQuant-MSE KV cache quantization (Zandieh, Daliri, Hadian, Mirrokni, ICLR 2026,
arXiv 2504.19874, Algorithm 1), written from the paper for Hugging Face transformers.

Each key and value vector x (length d = head dim) is stored as its norm plus b bits per
coordinate: u = x / |x| is rotated by a fixed random orthogonal matrix R, so each coordinate of
R u follows the same known distribution (density proportional to (1 - t^2)^((d - 3) / 2) on
[-1, 1]); every coordinate is quantized to the nearest of 2^b Lloyd-Max centroids of that
distribution. Reconstruction: x ~= |x| * R^T c[idx]. No calibration, no data dependence.

The second stage of the paper (a 1-bit QJL sketch of the residual, for unbiased inner products)
is left out, as in vLLM's ``turboquant_*_nc`` presets: community reproductions found it adds
variance that softmax attention amplifies.

``TurboQuantCache`` stores what attention sees: every key and value entering the cache is
replaced by its reconstruction, so all later attention (prefill included) reads quantized
states. It simulates the accuracy of a b-bit cache; it does not save memory (the reconstruction
is held in bf16).
"""

from __future__ import annotations

import math

import numpy as np
import torch
from transformers import DynamicCache


def lloyd_max(d: int, bits: int, grid: int = 400_001, iters: int = 300) -> np.ndarray:
    """Centroids minimising E[(t - c(t))^2] for one coordinate of a uniform unit vector in R^d."""
    t = np.linspace(-1.0, 1.0, grid)
    logp = 0.5 * (d - 3) * np.log(np.clip(1.0 - t * t, 1e-300, None))
    p = np.exp(logp - logp.max())
    p /= p.sum()
    cdf = np.cumsum(p)
    k = 2**bits
    c = np.interp((np.arange(k) + 0.5) / k, cdf, t)  # start at the quantiles
    for _ in range(iters):
        edges = np.concatenate([[-np.inf], (c[1:] + c[:-1]) / 2, [np.inf]])
        cell = np.searchsorted(edges, t) - 1
        mass = np.bincount(cell, weights=p, minlength=k)
        c = np.bincount(cell, weights=p * t, minlength=k) / np.maximum(mass, 1e-300)
    return np.sort(c)


class TurboQuantMSE:
    """b-bit quantize-dequantize of the last dimension of a tensor (one quantizer per head dim)."""

    def __init__(self, d: int, bits: int, seed: int = 0, device: str | torch.device = "cuda"):
        g = torch.Generator().manual_seed(seed * 1_000_003 + d)
        q, r = torch.linalg.qr(torch.randn(d, d, generator=g, dtype=torch.float64))
        q *= torch.sign(torch.diagonal(r))  # Haar-distributed rotation
        self.rot = q.to(device=device, dtype=torch.float32)
        c = lloyd_max(d, bits)
        self.centroids = torch.tensor(c, device=device, dtype=torch.float32)
        self.edges = torch.tensor((c[1:] + c[:-1]) / 2, device=device, dtype=torch.float32)

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        dtype = x.dtype
        x = x.float()
        norm = x.norm(dim=-1, keepdim=True)
        y = (x / norm.clamp_min(1e-12)) @ self.rot.T
        idx = torch.bucketize(y, self.edges)
        return ((self.centroids[idx] @ self.rot) * norm).to(dtype)


class TurboQuantCache(DynamicCache):
    """A DynamicCache whose stored keys and values are TurboQuant-MSE b-bit reconstructions.

    ``layers="full"`` quantizes only full-attention layers (the sliding-window layers stay bf16,
    as in vLLM's TurboQuant); ``"all"`` quantizes every layer."""

    _quantizers: dict[tuple[int, int, str], TurboQuantMSE] = {}

    def __init__(self, config, bits: int, layers: str = "all", **kwargs):
        super().__init__(config=config, **kwargs)
        self.bits = bits
        text = config.get_text_config(decoder=True)
        self.quantize_layer = [layers == "all" or t == "full_attention" for t in text.layer_types]

    def _q(self, x: torch.Tensor) -> torch.Tensor:
        key = (x.shape[-1], self.bits, str(x.device))
        if key not in self._quantizers:
            self._quantizers[key] = TurboQuantMSE(x.shape[-1], self.bits, device=x.device)
        return self._quantizers[key](x)

    def update(self, key_states, value_states, layer_idx, *args, **kwargs):
        if self.bits and self.quantize_layer[layer_idx]:
            same = key_states is value_states  # Gemma 4 global layers share K and V (attention_k_eq_v)
            key_states = self._q(key_states)
            value_states = key_states if same else self._q(value_states)
        return super().update(key_states, value_states, layer_idx, *args, **kwargs)


def distortion_check(d: int = 256, n: int = 20_000, device: str = "cuda") -> dict[int, float]:
    """Mean ||x - x_hat||^2 for unit vectors, per bit width. The paper's values (Theorem 1 and
    Table): b=1: 0.36, b=2: 0.117, b=3: 0.03, b=4: 0.009."""
    x = torch.randn(n, d, device=device)
    x /= x.norm(dim=-1, keepdim=True)
    out = {}
    for b in (1, 2, 3, 4):
        out[b] = round(float(((x - TurboQuantMSE(d, b, device=device)(x)) ** 2).sum(-1).mean()), 4)
    assert all(math.isfinite(v) for v in out.values())
    return out
