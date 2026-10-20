"""LLM providers for BeliefGraph. Each provider is a callable ``(system, message, note) -> text``
that records token usage, so BeliefGraph runs on whichever key you have:

    llm = make_llm("anthropic")                    # ANTHROPIC_API_KEY, default claude-opus-5-5
    llm = make_llm("openai", model="<model id>")   # OPENAI_API_KEY
    llm = make_llm("gemini", model="<model id>")   # GEMINI_API_KEY or GOOGLE_API_KEY
    llm = make_llm("lyzr", model="anthropic/claude-opus-5-5")  # LYZR_API_KEY, with a spend guard
    llm = make_llm("xai", model="<grok model id>")  # any OpenAI-compatible provider below
    llm = make_llm("openai-compatible", model="m", base_url="http://host/v1", api_key=...)

Anthropic, OpenAI and Gemini use their native SDKs. Every other provider in
``OPENAI_COMPATIBLE`` (xAI Grok, DeepSeek, Mistral, Groq, Together, Fireworks, OpenRouter,
Perplexity, local Ollama) speaks the OpenAI Chat Completions protocol and goes through the
OpenAI SDK with that provider's base URL and key. Model ids are always passed explicitly
for these: catalogues change too often to hard-code defaults.

SDKs are optional extras (``beliefbench[anthropic]``, ``[openai]``, ``[gemini]``) and are
imported only when their provider is used. Tests pass a fake ``client``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

DEFAULT_MODELS = {"anthropic": "claude-opus-5-5", "lyzr": "anthropic/claude-opus-5-5"}
# provider -> (base URL, API-key env var or None for keyless local servers)
OPENAI_COMPATIBLE = {
    "xai": ("https://api.x.ai/v1", "XAI_API_KEY"),
    "deepseek": ("https://api.deepseek.com", "DEEPSEEK_API_KEY"),
    "mistral": ("https://api.mistral.ai/v1", "MISTRAL_API_KEY"),
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY"),
    "together": ("https://api.together.xyz/v1", "TOGETHER_API_KEY"),
    "fireworks": ("https://api.fireworks.ai/inference/v1", "FIREWORKS_API_KEY"),
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
    "perplexity": ("https://api.perplexity.ai", "PERPLEXITY_API_KEY"),
    "ollama": ("http://localhost:11434/v1", None),
    "openai-compatible": (None, "OPENAI_COMPATIBLE_API_KEY"),  # any other server: pass base_url
}
KEY_ENV = {"anthropic": ("ANTHROPIC_API_KEY",), "openai": ("OPENAI_API_KEY",),
           "gemini": ("GEMINI_API_KEY", "GOOGLE_API_KEY"), "lyzr": ("LYZR_API_KEY",),
           **{p: ((env,) if env else ()) for p, (_, env) in OPENAI_COMPATIBLE.items()}}
PROVIDERS = sorted(KEY_ENV)
# Claude models on which the server-side refusal fallback ("default" routing) is available.
_FALLBACK_MODELS = {"claude-fable-5-1", "claude-opus-5-5", "claude-opus-5", "claude-sonnet-5-5"}


class RefusalError(RuntimeError):
    """The model declined the request."""


@dataclass
class ProviderLLM:
    provider: str
    model: str
    client: Any = None
    max_output_tokens: int = 16_000
    effort: str | None = "high"  # Anthropic: graph building is reasoning-heavy
    fallbacks: bool = True  # Anthropic: server-side refusal fallback (served model is recorded)
    usage: list[dict] = field(default_factory=list)

    def __call__(self, system: str, message: str, note: str = "") -> str:
        method = "_chat" if self.provider in OPENAI_COMPATIBLE else f"_{self.provider}"
        text, usage = getattr(self, method)(system, message)
        self.usage.append({"note": note, "model": self.model, **usage})
        return text

    def _anthropic(self, system: str, message: str) -> tuple[str, dict]:
        kwargs: dict[str, Any] = {"model": self.model, "max_tokens": self.max_output_tokens, "system": system,
                                  "messages": [{"role": "user", "content": message}]}
        if self.effort:
            kwargs["output_config"] = {"effort": self.effort}
        if self.fallbacks and self.model in _FALLBACK_MODELS:
            resp = self.client.beta.messages.create(betas=["server-side-fallback-2026-07-01"], fallbacks="default",
                                                    **kwargs)
        else:
            resp = self.client.messages.create(**kwargs)
        if resp.stop_reason == "refusal":
            raise RefusalError(f"{self.model} declined: {getattr(resp, 'stop_details', None)}")
        text = "".join(b.text for b in resp.content if b.type == "text")
        return text, {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens,
                      "served_by": getattr(resp, "model", self.model), "stop_reason": resp.stop_reason}

    def _openai(self, system: str, message: str) -> tuple[str, dict]:
        resp = self.client.responses.create(model=self.model, instructions=system, input=message,
                                            max_output_tokens=self.max_output_tokens)
        u = resp.usage
        return resp.output_text, {"input_tokens": getattr(u, "input_tokens", None),
                                  "output_tokens": getattr(u, "output_tokens", None)}

    def _chat(self, system: str, message: str) -> tuple[str, dict]:
        """OpenAI Chat Completions protocol (xAI, DeepSeek, Mistral, Groq, ... , Ollama)."""
        resp = self.client.chat.completions.create(
            model=self.model, max_tokens=self.max_output_tokens,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": message}])
        choice = resp.choices[0]
        if getattr(choice, "finish_reason", None) == "content_filter":
            raise RefusalError(f"{self.provider}/{self.model} filtered the response")
        u = resp.usage
        return choice.message.content or "", {"input_tokens": getattr(u, "prompt_tokens", None),
                                               "output_tokens": getattr(u, "completion_tokens", None)}

    def _gemini(self, system: str, message: str) -> tuple[str, dict]:
        from google.genai import types

        resp = self.client.models.generate_content(
            model=self.model, contents=message,
            config=types.GenerateContentConfig(system_instruction=system, max_output_tokens=self.max_output_tokens))
        u = resp.usage_metadata
        out = (getattr(u, "candidates_token_count", 0) or 0) + (getattr(u, "thoughts_token_count", 0) or 0)
        return resp.text or "", {"input_tokens": getattr(u, "prompt_token_count", None), "output_tokens": out}

    def _lyzr(self, system: str, message: str) -> tuple[str, dict]:
        # One guarded Lyzr agent per system prompt (an agent's instructions are fixed).
        agents = self.client["agents"]
        if system not in agents:
            from beliefbench.render.lyzr_client import LyzrRenderer

            agents[system] = LyzrRenderer(self.client["guard"], temperature=None, prompt_version="beliefgraph",
                                          system_prompt=system, agent_name="beliefgraph", role="Belief graph builder",
                                          goal="Build and revise an assistant's belief dependency graph as strict JSON.")
        text, meta = agents[system].call(message)
        usage = meta.get("usage") or {}
        return text, {"input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens"),
                      "est_usd": meta.get("est_usd")}

    def close(self) -> None:
        if self.provider == "lyzr":
            for agent in self.client["agents"].values():
                agent.close()


def _key(provider: str, api_key: str | None) -> str:
    if api_key:
        return api_key
    if not KEY_ENV[provider]:
        return "not-needed"  # keyless local server (Ollama)
    for name in KEY_ENV[provider]:
        if os.environ.get(name):
            return os.environ[name]
    raise RuntimeError(f"{provider}: set {' or '.join(KEY_ENV[provider])} or pass api_key")


def make_llm(provider: str, model: str | None = None, api_key: str | None = None, client: Any = None,
             budget_usd: float = 5.0, max_calls: int = 200, base_url: str | None = None, **opts) -> ProviderLLM:
    """A BeliefGraph LLM for ``provider`` (see ``PROVIDERS``)."""
    if provider not in KEY_ENV:
        raise ValueError(f"unknown provider {provider!r}; choose from {PROVIDERS}")
    model = model or DEFAULT_MODELS.get(provider)
    if not model:
        raise ValueError(f"{provider}: pass model=<model id>")
    if client is None:
        if provider in OPENAI_COMPATIBLE:
            import openai

            url = base_url or OPENAI_COMPATIBLE[provider][0]
            if not url:
                raise ValueError(f"{provider}: pass base_url=<server URL>")
            client = openai.OpenAI(api_key=_key(provider, api_key), base_url=url)
        elif provider == "anthropic":
            import anthropic

            client = anthropic.Anthropic(api_key=_key(provider, api_key))
        elif provider == "openai":
            import openai

            client = openai.OpenAI(api_key=_key(provider, api_key))
        elif provider == "gemini":
            from google import genai

            client = genai.Client(api_key=_key(provider, api_key))
        else:  # lyzr: the Studio reads LYZR_API_KEY itself; a hard spend cap guards every call
            from beliefbench.render.lyzr_client import SpendGuard

            _key(provider, api_key)
            client = {"guard": SpendGuard(budget_usd=budget_usd, max_calls=max_calls, model=model), "agents": {}}
    return ProviderLLM(provider, model, client, **opts)
