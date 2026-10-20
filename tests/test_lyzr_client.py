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
        "policies": {n.id: f"Rule {i} applies." for i, n in enumerate(s.nodes) if not n.is_evidence},
        "decoy_policies": ["An unrelated rule applies elsewhere."],
        "after_updates": {n.id: "holds" for n in s.nodes if not n.is_evidence},
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
    r, system, evaluation, k = rr.render_one(s, renderer, tmp_path, "gemini-3.5-flash", 3, seed=0, version="render-v8")
    assert k == 2 and len(agent.messages) == 2
    assert "forbidden graph_id" in agent.messages[1][0]  # feedback sent on retry
    # Second run is fully cached: no renderer needed, nothing billed.
    r2, system2, _, k2 = rr.render_one(s, None, tmp_path, "gemini-3.5-flash", 3, seed=0, version="render-v8")
    assert k2 == 2 and system2 == system


def test_render_one_gives_up_after_max_attempts(tmp_path):
    rr = _load_script()
    s = generate_suite(1, seed=0, families=["F1"])[0]
    agent = FakeAgent(["not json"] * 2)
    renderer = LyzrRenderer(SpendGuard(1.0, 10), studio=FakeStudio(agent))
    with pytest.raises(ValueError, match="no valid rendering after 2"):
        rr.render_one(s, renderer, tmp_path, "gemini-3.5-flash", 2, seed=0, version="render-v8")


def test_register_gemini_model_makes_sdk_accept_current_models():
    pytest.importorskip("lyzr")
    from lyzr.providers import ModelResolver

    from beliefbench.render.lyzr_client import register_gemini_model

    register_gemini_model("gemini-3.5-flash")
    provider, model, _ = ModelResolver.parse("gemini/gemini-3.5-flash")
    assert (provider.value, model, ModelResolver.get_credential_id(provider)) == ("Google", "gemini-3.5-flash", "lyzr_google")


def test_find_usage_and_charge_on_reported_tokens():
    from beliefbench.render.lyzr_client import find_usage

    assert find_usage({"response": "x"}) is None
    u = find_usage({"usage": {"prompt_tokens": 1000, "completion_tokens": 500, "reasoning_tokens": 300}})
    assert u["input_tokens"] == 1000 and u["output_tokens"] == 500
    g = find_usage({"usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 20, "thoughtsTokenCount": 5}})
    assert g["output_tokens"] == 25  # Gemini reports thinking separately
    guard = SpendGuard(1.0, 5, model="gemini-2.5-flash")
    cost = guard.charge(4000, 2000, usage=u)
    assert cost == pytest.approx((1000 * 0.30 + 500 * 2.50) / 1e6)
    assert guard.log[-1]["basis"] == "reported_usage"


def test_unverified_price_gets_safety_factor():
    g = SpendGuard(1.0, 5, model="gemini-3.5-flash")
    assert g.prices == pytest.approx((1.50 * 1.5, 7.50 * 1.5))


def test_render_one_repairs_only_the_flagged_field_before_any_rerender(tmp_path):
    rr = _load_script()
    s = generate_suite(1, seed=0, families=["F2"])[0]
    first_mem = next(n.id for n in s.nodes if not n.is_evidence)
    agent = FakeAgent([good_response(s, leak="Per E1 this holds.")])
    fix = json.dumps({"replacements": {f"nodes.{first_mem}.text": "The item holds."}})
    rep_agent = FakeAgent([fix])
    guard = SpendGuard(1.0, 10)
    renderer = LyzrRenderer(guard, studio=FakeStudio(agent))
    repairer = LyzrRenderer(guard, studio=FakeStudio(rep_agent), system_prompt="repair")
    r, system, _, k = rr.render_one(s, renderer, tmp_path, "gemini-3.5-flash", 2, seed=0, version="render-v8",
                                    repairer=repairer, max_repairs=1)
    assert k == 1 and len(agent.messages) == 1 and len(rep_agent.messages) == 1  # no whole re-render
    assert r.texts[first_mem] == "The item holds."
    rec = json.loads(next(tmp_path.glob("*.a1.r1.json")).read_text())
    assert rec["diff"] == [f"nodes.{first_mem}.text"] and rec["merge_errors"] == []


def test_render_one_falls_back_to_a_whole_attempt_when_the_repair_oversteps(tmp_path):
    rr = _load_script()
    s = generate_suite(1, seed=0, families=["F2"])[0]
    first_mem = next(n.id for n in s.nodes if not n.is_evidence)
    agent = FakeAgent([good_response(s, leak="Per E1 this holds."), good_response(s)])
    overstep = json.dumps({"replacements": {f"nodes.{first_mem}.text": "Fine.", "world": "changed"}})
    guard = SpendGuard(1.0, 10)
    renderer = LyzrRenderer(guard, studio=FakeStudio(agent))
    repairer = LyzrRenderer(guard, studio=FakeStudio(FakeAgent([overstep])), system_prompt="repair")
    _, _, _, k = rr.render_one(s, renderer, tmp_path, "gemini-3.5-flash", 2, seed=0, version="render-v8",
                               repairer=repairer, max_repairs=1)
    assert k == 2 and len(agent.messages) == 2


class FlakyAgent(FakeAgent):
    """Raises the given errors first, then answers."""

    def __init__(self, errors, replies):
        super().__init__(replies)
        self.errors = list(errors)

    def run(self, message, session_id=None):
        if self.errors:
            self.messages.append((message, session_id))
            raise self.errors.pop(0)
        return super().run(message, session_id)


def test_provider_error_is_charged_at_worst_case_and_retried_once():
    agent = FlakyAgent([ConnectionError("Server disconnected")], ["ok"])
    guard = SpendGuard(1.0, 10)
    r = LyzrRenderer(guard, studio=FakeStudio(agent), system_prompt="p")
    text, _ = r.call("hello", note="x")
    assert text == "ok" and len(agent.messages) == 2
    failed = [c for c in guard.log if c["basis"] == "failed_call_worst_case"]
    assert len(failed) == 1 and failed[0]["est_usd"] == pytest.approx(guard.worst_case(len("p") + len("hello")), abs=1e-6)


def test_second_provider_error_is_raised_and_both_charged():
    agent = FlakyAgent([ConnectionError("a"), ConnectionError("b")], [])
    guard = SpendGuard(1.0, 10)
    r = LyzrRenderer(guard, studio=FakeStudio(agent), system_prompt="p")
    with pytest.raises(ConnectionError):
        r.call("hello")
    assert sum(c["basis"] == "failed_call_worst_case" for c in guard.log) == 2


def test_provider_retry_never_exceeds_the_cap():
    agent = FlakyAgent([ConnectionError("a")], ["ok"])
    guard = SpendGuard(0.0, 10)
    guard.budget_usd = guard.worst_case(len("p") + len("hello")) * 1.5  # room for one worst case only
    r = LyzrRenderer(guard, studio=FakeStudio(agent), system_prompt="p")
    with pytest.raises(BudgetExceeded):
        r.call("hello")
    assert len(agent.messages) == 1
