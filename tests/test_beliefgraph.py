"""BeliefGraph (the tool): parsing, revision, providers and the evaluation harness.
Model-free: every provider is exercised with a fake client."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from beliefbench.beliefgraph_eval import gold_inputs, load_accepted, memory_gold, score
from beliefbench.schema import Action
from beliefgraph.core import BeliefGraph, UpdateReading, parse_graph, parse_readings, revise
from beliefgraph.llm import OPENAI_COMPATIBLE, PROVIDERS, RefusalError, make_llm

RENDERED = Path(__file__).resolve().parents[1] / "data" / "rendered"
ALL_RUNS = ("pilot40-render-v10", "validate-v11", "validate-v11-f3-retry", "validate-v12")

VIEW = {
    "scenario": "s_demo", "domain": "d",
    "evidence": [{"id": "e_1", "observed": "2026-01-01", "source": "Official registry", "text": "Acme has 15 trucks."},
                 {"id": "e_2", "observed": "2026-01-02", "source": "ISO registry", "text": "Acme holds ISO 9001."},
                 {"id": "e_3", "observed": "2026-01-03", "source": "Signed audit", "text": "Acme logged 0 incidents."}],
    "memories": [{"id": "m_1", "text": "Acme is an approved carrier."},
                 {"id": "m_2", "text": "Give Acme the contract."}],
    "policies": [{"id": "p_1", "text": "Approved carriers have 10+ trucks or ISO 9001."},
                 {"id": "p_2", "text": "Contracts go to approved carriers with zero incidents."}],
    "updates": [{"id": "u_1", "observed": "2026-01-04", "source": "Official registry update",
                 "text": "Acme now has 6 trucks."}],
}
GRAPH = {"justifications": {"m_1": [["e_1"], ["e_2"]], "m_2": [["m_1", "e_3"]]},
         "reliability": {"e_1": "high", "e_2": "high", "e_3": "high"}}
READ = {"updates": {"u_1": {"target": "e_1", "relation": "supersedes", "reliability": "high"}}}


def _fake_llm(build=GRAPH, read=READ):
    def llm(system, message, note=""):
        return json.dumps(build if "AND sets" in system else read)
    return llm


# ── the tool ──


def test_or_alternative_keeps_the_conclusion_and_its_dependent():
    bg = BeliefGraph(_fake_llm())
    graph = bg.build(VIEW)
    readings, errors = bg.read_updates(VIEW)
    actions = revise(VIEW, graph.justifications, graph.reliability, readings)
    assert errors == [] and graph.errors == []
    assert actions["m_1"] is Action.KEEP and actions["m_2"] is Action.KEEP  # ISO 9001 still supports m_1
    assert actions["e_1"] is Action.SUPERSEDE


def test_losing_the_only_support_recomputes_the_chain():
    graph = {"justifications": {"m_1": [["e_1"]], "m_2": [["m_1", "e_3"]]}, "reliability": GRAPH["reliability"]}
    bg = BeliefGraph(_fake_llm(build=graph))
    g = bg.build(VIEW)
    actions = revise(VIEW, g.justifications, g.reliability, bg.read_updates(VIEW)[0])
    assert actions["m_1"] is Action.RECOMPUTE and actions["m_2"] is Action.RECOMPUTE


def test_weak_source_retraction_of_the_only_support_is_uncertain():
    graph = {"justifications": {"m_1": [["e_1"]], "m_2": [["m_1", "e_3"]]}, "reliability": GRAPH["reliability"]}
    read = {"updates": {"u_1": {"target": "e_1", "relation": "retracts", "reliability": "low"}}}
    bg = BeliefGraph(_fake_llm(build=graph, read=read))
    g = bg.build(VIEW)
    actions = revise(VIEW, g.justifications, g.reliability, bg.read_updates(VIEW)[0])
    assert actions["m_1"] is Action.UNCERTAIN and actions["m_2"] is Action.UNCERTAIN


def test_parse_graph_drops_unknown_and_self_ids_and_breaks_cycles():
    raw = json.dumps({"justifications": {"m_1": [["e_1", "e_99"], ["m_1"], ["m_2"]], "m_2": [["m_1"]]},
                      "reliability": {"e_1": "high", "e_2": "maybe"}})
    g = parse_graph(raw, VIEW)
    assert any("cycle" in e for e in g.errors) and g.justifications == {"m_1": [], "m_2": []}
    assert g.reliability["e_2"] == "high" and g.reliability["e_3"] == "high"
    assert parse_graph("not json", VIEW).errors[0].startswith("invalid JSON")


def test_parse_readings_ignores_unknown_targets_and_defaults_bad_labels():
    raw = json.dumps({"updates": {"u_1": {"target": "e_404", "relation": "retracts", "reliability": "high"}}})
    readings, errors = parse_readings(raw, VIEW)
    assert readings == {} and "unknown target" in errors[0]
    raw = json.dumps({"updates": {"u_1": {"target": "e_1", "relation": "deletes", "reliability": "?"}}})
    readings, _ = parse_readings(raw, VIEW)
    assert readings["u_1"] == UpdateReading("e_1", "hedges", "medium")


def test_build_never_shows_the_updates_to_the_llm():
    seen = []
    bg = BeliefGraph(lambda system, message, note="": seen.append(message) or json.dumps(GRAPH))
    bg.build(VIEW)
    assert "Acme now has 6 trucks" not in seen[0] and "Give Acme the contract" in seen[0]


# ── providers ──


def _anthropic_client(stop="end_turn"):
    resp = SimpleNamespace(stop_reason=stop, stop_details=None, model="claude-opus-5-5",
                           content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text="{}")],
                           usage=SimpleNamespace(input_tokens=10, output_tokens=5))
    calls = []
    create = lambda **kw: calls.append(kw) or resp  # noqa: E731
    return SimpleNamespace(messages=SimpleNamespace(create=create),
                           beta=SimpleNamespace(messages=SimpleNamespace(create=create))), calls


def test_anthropic_provider_uses_fallbacks_and_effort_and_records_usage():
    client, calls = _anthropic_client()
    llm = make_llm("anthropic", client=client)
    assert llm("sys", "msg", "n") == "{}"
    kw = calls[0]
    assert kw["model"] == "claude-opus-5-5" and kw["fallbacks"] == "default" and kw["output_config"] == {"effort": "high"}
    assert "temperature" not in kw and llm.usage[0]["input_tokens"] == 10


def test_anthropic_refusal_raises():
    client, _ = _anthropic_client(stop="refusal")
    with pytest.raises(RefusalError):
        make_llm("anthropic", client=client)("s", "m")


def test_openai_provider_uses_responses_api():
    resp = SimpleNamespace(output_text="{}", usage=SimpleNamespace(input_tokens=3, output_tokens=4))
    calls = []
    client = SimpleNamespace(responses=SimpleNamespace(create=lambda **kw: calls.append(kw) or resp))
    llm = make_llm("openai", model="some-model", client=client)
    assert llm("sys", "msg") == "{}" and calls[0]["instructions"] == "sys" and calls[0]["input"] == "msg"


@pytest.mark.parametrize("provider", sorted(OPENAI_COMPATIBLE))
def test_openai_compatible_providers_use_chat_completions(provider):
    resp = SimpleNamespace(choices=[SimpleNamespace(finish_reason="stop", message=SimpleNamespace(content="{}"))],
                           usage=SimpleNamespace(prompt_tokens=7, completion_tokens=2))
    calls = []
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kw: calls.append(kw) or resp)))
    llm = make_llm(provider, model="some-model", client=client)
    assert llm("sys", "msg") == "{}"
    assert calls[0]["messages"][0] == {"role": "system", "content": "sys"} and llm.usage[0]["output_tokens"] == 2


def test_gemini_provider_passes_system_instruction():
    pytest.importorskip("google.genai")
    resp = SimpleNamespace(text="{}", usage_metadata=SimpleNamespace(prompt_token_count=5, candidates_token_count=1,
                                                                    thoughts_token_count=2))
    calls = []
    client = SimpleNamespace(models=SimpleNamespace(generate_content=lambda **kw: calls.append(kw) or resp))
    llm = make_llm("gemini", model="some-gemini", client=client)
    assert llm("sys", "msg") == "{}" and calls[0]["config"].system_instruction == "sys"
    assert llm.usage[0]["output_tokens"] == 3


def test_provider_list_covers_the_major_apis_and_requires_models_where_needed():
    assert {"anthropic", "openai", "gemini", "xai", "deepseek", "mistral", "groq", "openrouter", "ollama"} <= set(PROVIDERS)
    with pytest.raises(ValueError):
        make_llm("xai", client=object())  # no default model for catalogues that change
    with pytest.raises(ValueError):
        make_llm("not-a-provider")


# ── evaluation harness ──


def test_oracle_graph_and_readings_reproduce_gold_on_every_accepted_scenario():
    n = 0
    for run in ALL_RUNS:
        for sv, ev, seed in load_accepted(RENDERED / run):
            gj, grel, gread = gold_inputs(sv, ev, seed)
            got = {k: v for k, v in revise(sv, gj, grel, gread).items() if k.startswith("m_")}
            assert got == memory_gold(ev), (run, ev["source_scenario"])
            n += 1
    assert n == 63


def test_score_with_perfect_predictions_is_perfect_and_cascade_over_invalidates():
    items = []
    for sv, ev, seed in load_accepted(RENDERED / "pilot40-render-v10"):
        gj, grel, gread = gold_inputs(sv, ev, seed)
        items.append({"sv": sv, "ev": ev, "seed": seed, "graph": {"justifications": gj, "reliability": grel},
                      "readings": gread})
    res = score(items)
    assert res["revision"]["P"]["accuracy"] == 1.0 and res["graph_extraction"]["justification_set_f1"] == 1.0
    assert res["update_reading_exact"] == 1.0 and res["source_reliability_accuracy"] == 1.0
    assert res["revision"]["naive-cascade"]["over_invalidation_rate"] > 0
