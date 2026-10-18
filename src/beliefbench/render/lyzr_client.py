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

from beliefbench.render.prompt import PROMPT_VERSION, SYSTEM_PROMPT

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
        return MODEL_PRICES[self.model]

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

    def charge(self, prompt_chars: int, response_chars: int, note: str = "") -> float:
        """Record a completed call at a conservative cost: actual chars, plus the full
        thinking allowance (actual thinking usage is not reported)."""
        pin, pout = self.prices
        cost = (est_tokens(prompt_chars) * pin + (est_tokens(response_chars) + THINKING_ALLOWANCE) * pout) / 1e6
        self.calls += 1
        self.spent_usd += cost
        self.log.append({"call": self.calls, "note": note, "prompt_chars": prompt_chars,
                         "response_chars": response_chars, "est_usd": round(cost, 6)})
        return cost


class BudgetExceeded(RuntimeError):
    pass


class LyzrRenderer:
    """Thin wrapper: one Lyzr agent whose instructions are the renderer system prompt."""

    def __init__(self, guard: SpendGuard, studio: Any = None, temperature: float = 0.9):
        if guard.model not in MODEL_PRICES:
            raise ValueError(f"model {guard.model!r} has no price entry; add one before using it")
        self.guard = guard
        self._studio = studio
        self._agent = None
        self.temperature = temperature

    @property
    def agent(self):
        if self._agent is None:
            if self._studio is None:
                from lyzr import Studio  # imported lazily: tests and dry runs need no key

                self._studio = Studio(log="warning")
            register_gemini_model(self.guard.model)
            self._agent = self._studio.create_agent(
                name=f"beliefbench-renderer-{PROMPT_VERSION}",
                provider=f"gemini/{self.guard.model}",
                role="Benchmark scenario writer",
                goal="Render abstract dependency graphs as realistic natural-language scenarios as strict JSON.",
                instructions=SYSTEM_PROMPT,
                temperature=self.temperature,
                top_p=0.95,
                store_messages=False,
                llm_credential_id="lyzr_google",
            )
        return self._agent

    def call(self, message: str, note: str = "") -> tuple[str, dict]:
        """One billed call. Raises BudgetExceeded *before* calling if it might not fit."""
        prompt_chars = len(SYSTEM_PROMPT) + len(message)
        self.guard.check(prompt_chars)
        resp = self.agent.run(message, session_id=f"render-{uuid.uuid4().hex[:12]}")
        text = getattr(resp, "response", None) or str(resp)
        meta = dict(getattr(resp, "metadata", None) or {})
        meta["est_usd"] = self.guard.charge(prompt_chars, len(text), note)
        meta["model"] = self.guard.model
        meta["agent_id"] = getattr(self.agent, "id", None)
        return text, meta

    def close(self) -> None:
        if self._agent is not None:
            try:
                self._agent.delete()
            finally:
                self._agent = None
