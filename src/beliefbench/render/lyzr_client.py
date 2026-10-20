"""Renderer client over Lyzr ADK agents, with a hard spend guard.

Spend controls:
- one Lyzr agent per run (created lazily, deleted on close); no memory, reflection,
  judge or stored messages, which would add billed calls or tokens;
- a fresh session id per call, so no conversation history is resent;
- a SpendGuard that refuses a call unless the *worst case* cost of that call still fits
  the budget, plus a hard cap on the number of calls;
- the caller caches raw responses on disk, so nothing is re-billed (scripts/render_run.py).

Lyzr's AgentResponse carries no token usage, so cost is a conservative estimate from
character counts (chars / 4) with a worst-case thinking allowance. Whatever metadata
Lyzr returns is recorded alongside the estimate.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from beliefbench.render.prompt import PROMPT_VERSION, PROMPTS

# USD per 1M tokens (input, output), Google's official Gemini pricing page, updated
# 2026-10-16. Lyzr bills in its own credits; these drive the conservative spend guard.
MODEL_PRICES: dict[str, tuple[float, float]] = {
    # Lyzr's best Google model (live catalogue 2026-10-18: intelligence index 33, the
    # highest Google entry). Not on Google's pricing page under this name, so priced as
    # gemini-3.8-flash at its post-intro list price, a conservative proxy.
    "gemini-3.5-flash": (1.50, 7.50),
    "gemini-3.1-pro-preview": (2.00, 12.00),
    "gemini-2.5-flash": (0.30, 2.50),  # outdated (index 13); kept so smoke test 1 stays reproducible
}
DEFAULT_MODEL = "gemini-3.5-flash"
# Prices not verified against a published price for that exact model get this multiplier
# in the spend guard, so the cap holds even if the proxy is somewhat low.
PRICE_VERIFIED = {"gemini-3.5-flash": False, "gemini-3.1-pro-preview": True, "gemini-2.5-flash": True}
UNVERIFIED_SAFETY = 1.5
CATALOGUE_URL = "https://agent-prod.studio.lyzr.ai/v3/providers/type"


def lyzr_catalogue(api_key: str) -> dict[str, dict]:
    """Lyzr's live hosted-model catalogue ({"gemini/gemini-3.5-flash": {...}, ...}). Free call;
    needs the providers:read permission."""
    import httpx

    r = httpx.get(CATALOGUE_URL, params={"provider_type": "lyzr-llm"}, headers={"x-api-key": api_key}, timeout=20)
    r.raise_for_status()
    return {m["name"]: {**m, "provider": p["provider_id"], "credential_id": (p.get("meta_data") or {}).get("credential_id")}
            for p in r.json() for m in (p.get("meta_data") or {}).get("models") or []}


def register_gemini_model(model: str, context_window: int = 1_000_000) -> None:
    """lyzr-adk 0.1.12's local registry predates current Gemini models and rejects them.
    Add the model so ``provider="gemini/<model>"`` resolves to provider_id Google with
    credential lyzr_google (the same mapping the SDK uses for gemini-2.5-flash)."""
    from lyzr.providers import _PROVIDERS_DATA, ModelInfo, ProviderName

    models = _PROVIDERS_DATA[ProviderName.GOOGLE].models
    if model not in models:
        models[model] = ModelInfo(name=model, capability_score=5, speed_score=4,
                                  context_window=context_window, model_type="Reasoning")
THINKING_ALLOWANCE = 8_000  # worst-case reasoning tokens per call, billed as output
MAX_VISIBLE_OUTPUT = 4_000  # worst-case visible output tokens per call (texts are capped at 40 words)


def est_tokens(chars: int) -> int:
    return (chars + 3) // 4


@dataclass
class SpendGuard:
    budget_usd: float
    max_calls: int
    model: str = DEFAULT_MODEL
    calls: int = 0
    spent_usd: float = 0.0  # conservative estimate of what has been billed
    log: list[dict] = field(default_factory=list)

    @property
    def prices(self) -> tuple[float, float]:
        pin, pout = MODEL_PRICES[self.model]
        k = 1.0 if PRICE_VERIFIED.get(self.model, False) else UNVERIFIED_SAFETY
        return pin * k, pout * k

    def worst_case(self, prompt_chars: int) -> float:
        pin, pout = self.prices
        return (est_tokens(prompt_chars) * pin + (MAX_VISIBLE_OUTPUT + THINKING_ALLOWANCE) * pout) / 1e6

    def check(self, prompt_chars: int) -> None:
        if self.calls >= self.max_calls:
            raise BudgetExceeded(f"call cap reached ({self.max_calls})")
        if self.spent_usd + self.worst_case(prompt_chars) > self.budget_usd:
            raise BudgetExceeded(
                f"next call could exceed budget: spent≈${self.spent_usd:.4f} + worst case "
                f"${self.worst_case(prompt_chars):.4f} > ${self.budget_usd:.2f}"
            )

    def charge(self, prompt_chars: int, response_chars: int, note: str = "",
               usage: dict | None = None) -> float:
        """Record a completed call. With reported token usage, charge that (output
        includes reasoning tokens when reported); otherwise a conservative estimate from
        actual chars plus the full thinking allowance."""
        pin, pout = self.prices
        if usage and usage.get("input_tokens") is not None and usage.get("output_tokens") is not None:
            cost = (usage["input_tokens"] * pin + usage["output_tokens"] * pout) / 1e6
            basis = "reported_usage"
        else:
            cost = (est_tokens(prompt_chars) * pin + (est_tokens(response_chars) + THINKING_ALLOWANCE) * pout) / 1e6
            basis = "conservative_estimate"
        self.calls += 1
        self.spent_usd += cost
        self.log.append({"call": self.calls, "note": note, "prompt_chars": prompt_chars,
                         "response_chars": response_chars, "usage": usage, "basis": basis,
                         "est_usd": round(cost, 6)})
        return cost


class BudgetExceeded(RuntimeError):
    pass


_IN_KEYS = ("prompt_tokens", "input_tokens", "prompt_token_count", "promptTokenCount")
_OUT_KEYS = ("completion_tokens", "output_tokens", "candidates_token_count", "candidatesTokenCount")
_THINK_KEYS = ("reasoning_tokens", "thoughts_token_count", "thoughtsTokenCount")


def find_usage(raw) -> dict | None:
    """Search a raw API response for token counts under any common naming. Returns
    {"input_tokens", "output_tokens" (incl. reasoning), "reasoning_tokens", "raw"} or None."""
    found: dict = {}

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    for name, keys in (("in", _IN_KEYS), ("out", _OUT_KEYS), ("think", _THINK_KEYS)):
                        if k in keys and name not in found:
                            found[name] = (k, int(v))
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(raw)
    if "in" not in found or "out" not in found:
        return None
    think = found.get("think", (None, 0))[1]
    # Some APIs include reasoning in completion tokens, some report it separately.
    out = found["out"][1] + (think if found["out"][0] in ("candidates_token_count", "candidatesTokenCount") else 0)
    return {"input_tokens": found["in"][1], "output_tokens": out, "reasoning_tokens": think,
            "raw": {v[0]: v[1] for v in found.values()}}


class LyzrRenderer:
    """Thin wrapper: one Lyzr agent whose instructions are the renderer system prompt."""

    def __init__(self, guard: SpendGuard, studio: Any = None, temperature: float = 0.9,
                 prompt_version: str = PROMPT_VERSION, system_prompt: str | None = None):
        if guard.model not in MODEL_PRICES:
            raise ValueError(f"model {guard.model!r} has no price entry; add one before using it")
        self.guard = guard
        self._studio = studio
        self._agent = None
        self.temperature = temperature
        self.prompt_version = prompt_version
        # A version not in PROMPTS (e.g. "repair-v1") must bring its own pinned prompt.
        self.system_prompt = system_prompt if system_prompt is not None else PROMPTS[prompt_version]

    @property
    def agent(self):
        if self._agent is None:
            if self._studio is None:
                from lyzr import Studio  # imported lazily: tests and dry runs need no key

                self._studio = Studio(log="warning")
            register_gemini_model(self.guard.model)
            self._agent = self._studio.create_agent(
                name=f"beliefbench-renderer-{self.prompt_version}",
                provider=f"gemini/{self.guard.model}",
                role="Benchmark scenario writer",
                goal="Render abstract dependency graphs as realistic natural-language scenarios as strict JSON.",
                instructions=self.system_prompt,
                temperature=self.temperature,
                top_p=0.95,
                store_messages=False,
                llm_credential_id="lyzr_google",
            )
        return self._agent

    def call(self, message: str, note: str = "") -> tuple[str, dict]:
        """One billed call. Raises BudgetExceeded *before* calling if it might not fit."""
        prompt_chars = len(self.system_prompt) + len(message)
        self.guard.check(prompt_chars)
        resp = self.agent.run(message, session_id=f"render-{uuid.uuid4().hex[:12]}")
        text = getattr(resp, "response", None) or str(resp)
        meta = dict(getattr(resp, "metadata", None) or {})
        raw = getattr(resp, "raw_response", None) or {}
        usage = find_usage(raw)
        meta["raw_response_keys"] = sorted(raw) if isinstance(raw, dict) else []
        meta["usage"] = usage
        meta["est_usd"] = self.guard.charge(prompt_chars, len(text), note, usage=usage)
        meta["model"] = self.guard.model
        meta["agent_id"] = getattr(self.agent, "id", None)
        return text, meta

    def close(self) -> None:
        if self._agent is not None:
            try:
                self._agent.delete()
            finally:
                self._agent = None
