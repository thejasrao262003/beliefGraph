"""Offline tests for the Lyzr renderer client: no key, no network, no spend."""

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from beliefbench.generate import generate_suite
from beliefbench.render.lyzr_client import MODEL_PRICES, BudgetExceeded, LyzrRenderer, SpendGuard


def _load_script():
    path = Path(__file__).parent.parent / "scripts" / "render_run.py"
    spec = importlib.util.spec_from_file_location("render_run", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["render_run"] = mod
    spec.loader.exec_module(mod)
    return mod


def good_response(s, leak: str | None = None) -> str:
    nodes = {n.id: {"text": f"Fact number {i} about item {i * 7}.", "source": "Official registry"}
             for i, n in enumerate(s.nodes)}
    if leak:
        first_mem = next(n.id for n in s.nodes if not n.is_evidence)
        nodes[first_mem]["text"] = leak
    return json.dumps({
        "world": "w", "nodes": nodes,
        "updates": {u.id: {"text": "A later notice changed this.", "source": "Official registry"} for u in s.updates},
        "rationale": {n.id: ["r"] * len(n.justifications) for n in s.nodes if not n.is_evidence},
    })


class FakeAgent:
    def __init__(self, replies):
        self.replies = list(replies)
        self.messages = []
        self.deleted = False
        self.id = "agent-fake"

    def run(self, message, session_id=None):
        self.messages.append((message, session_id))
        return SimpleNamespace(response=self.replies.pop(0), metadata={"usage": "n/a"})

    def delete(self):
        self.deleted = True


class FakeStudio:
    def __init__(self, agent):
        self.agent = agent
        self.create_kwargs = None

    def create_agent(self, **kw):
        self.create_kwargs = kw
        return self.agent


def test_guard_blocks_before_overspending():
    # Worst case for a 5k-char prompt: 1,250 in x $0.30 + 12,000 out x $2.50 per 1M = $0.0304.
    g = SpendGuard(budget_usd=0.01, max_calls=10, model="gemini-2.5-flash")
    assert g.worst_case(5_000) == pytest.approx(0.0304, abs=1e-4)
    with pytest.raises(BudgetExceeded):
        g.check(5_000)
    assert g.calls == 0 and g.spent_usd == 0.0


def test_guard_budget_and_call_cap():
    g = SpendGuard(budget_usd=0.05, max_calls=1, model="gemini-2.5-flash")
    g.check(5_000)
    g.charge(5_000, 2_000)
    with pytest.raises(BudgetExceeded, match="call cap"):
        g.check(5_000)
    g2 = SpendGuard(budget_usd=0.02, max_calls=99)
    with pytest.raises(BudgetExceeded, match="exceed budget"):
        g2.check(5_000)


def test_renderer_creates_one_cheap_agent_and_fresh_sessions():
    agent = FakeAgent(["a", "b"])
    studio = FakeStudio(agent)
    r = LyzrRenderer(SpendGuard(1.0, 10), studio=studio)
    r.call("m1")
    r.call("m2")
    kw = studio.create_kwargs
    assert kw["provider"] == "gemini/gemini-3.5-flash" and kw["store_messages"] is False
    assert not any(k in kw for k in ("memory", "reflection", "llm_judge", "bias_check"))
    sessions = [sid for _, sid in agent.messages]
    assert len(set(sessions)) == 2
    r.close()
    assert agent.deleted
    assert r.guard.calls == 2 and r.guard.spent_usd > 0


def test_unpriced_model_rejected():
    with pytest.raises(ValueError):
        LyzrRenderer(SpendGuard(1.0, 1, model="gpt-4o"), studio=FakeStudio(FakeAgent([])))
    assert "gemini-3.5-flash" in MODEL_PRICES


def test_render_one_retries_on_hard_leak_then_caches(tmp_path):
    rr = _load_script()
    s = generate_suite(1, seed=0, families=["F2"])[0]
    agent = FakeAgent([good_response(s, leak="Per E1 this holds."), good_response(s)])
    renderer = LyzrRenderer(SpendGuard(1.0, 10), studio=FakeStudio(agent))
    r, system, evaluation, k = rr.render_one(s, renderer, tmp_path, "gemini-3.5-flash", 3, seed=0)
    assert k == 2 and len(agent.messages) == 2
    assert "forbidden graph_id" in agent.messages[1][0]  # feedback sent on retry
    # Second run is fully cached: no renderer needed, nothing billed.
    r2, system2, _, k2 = rr.render_one(s, None, tmp_path, "gemini-3.5-flash", 3, seed=0)
    assert k2 == 2 and system2 == system


def test_render_one_gives_up_after_max_attempts(tmp_path):
    rr = _load_script()
    s = generate_suite(1, seed=0, families=["F1"])[0]
    agent = FakeAgent(["not json"] * 2)
    renderer = LyzrRenderer(SpendGuard(1.0, 10), studio=FakeStudio(agent))
    with pytest.raises(ValueError, match="no valid rendering after 2"):
        rr.render_one(s, renderer, tmp_path, "gemini-3.5-flash", 2, seed=0)


def test_register_gemini_model_makes_sdk_accept_current_models():
    pytest.importorskip("lyzr")
    from lyzr.providers import ModelResolver

    from beliefbench.render.lyzr_client import register_gemini_model

    register_gemini_model("gemini-3.5-flash")
    provider, model, _ = ModelResolver.parse("gemini/gemini-3.5-flash")
    assert (provider.value, model, ModelResolver.get_credential_id(provider)) == ("Google", "gemini-3.5-flash", "lyzr_google")
