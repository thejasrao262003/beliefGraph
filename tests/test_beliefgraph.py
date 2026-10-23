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
    # m_1 keeps its fact-only set (e_1, the unknown e_99 dropped) and gives up the set that
    # closes the cycle; m_2 keeps its support on m_1
    assert any("cycle" in e for e in g.errors) and g.justifications == {"m_1": [["e_1"]], "m_2": [["m_1"]]}
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


def test_llm_direct_baseline_parses_and_defaults_missing_to_keep():
    from beliefbench.llm_baselines import DIRECT_PROMPT, direct_message, llm_direct

    seen = []

    def llm(system, message, note=""):
        seen.append((system, message))
        return json.dumps({"actions": {"m_1": "keep", "m_2": "bogus"}})

    actions, errors = llm_direct(llm, VIEW)
    assert actions == {"m_1": Action.KEEP, "m_2": Action.KEEP} and "bogus" in errors[0]
    assert seen[0][0] == DIRECT_PROMPT and "Acme now has 6 trucks" in direct_message(VIEW)  # it sees the updates


def test_score_includes_llm_direct_when_present():
    items = []
    for sv, ev, seed in load_accepted(RENDERED / "validate-v12")[:3]:
        gj, grel, gread = gold_inputs(sv, ev, seed)
        items.append({"sv": sv, "ev": ev, "seed": seed, "graph": {"justifications": gj, "reliability": grel},
                      "readings": gread, "direct": {m: Action.KEEP for m in memory_gold(ev)}})
    res = score(items)
    assert res["revision"]["LLM-direct"]["n"] > 0 and res["revision"]["P"]["accuracy"] == 1.0


# ── v0.1: unsupported-memory retry; paired statistics; cost by method ──


def test_unsupported_memory_is_asked_about_once_more_and_then_reported():
    first = {"justifications": {"m_1": [["e_1"], ["e_2"]], "m_2": []}, "reliability": GRAPH["reliability"]}
    retry = {"justifications": {"m_2": [["m_1", "e_3"]]}, "reliability": GRAPH["reliability"]}
    calls = []

    def llm(system, message, note=""):
        calls.append(note)
        return json.dumps(retry if note.endswith("retry") else first)

    g = BeliefGraph(llm).build(VIEW)
    assert calls == ["s_demo build", "s_demo retry"] and g.justifications["m_2"] == [["e_3", "m_1"]]
    assert g.unsupported == []

    g2 = BeliefGraph(lambda s, m, n="": json.dumps(first)).build(VIEW)
    assert g2.unsupported == ["m_2"]  # still empty after the retry: reported, not hidden
    assert BeliefGraph(lambda s, m, n="": json.dumps(GRAPH)).build(VIEW).unsupported == []


def test_retry_message_names_only_the_unsupported_memories():
    seen = {}

    def llm(system, message, note=""):
        seen[note] = message
        return json.dumps({"justifications": {"m_1": [["e_1"]], "m_2": []}, "reliability": GRAPH["reliability"]})

    BeliefGraph(llm).build(VIEW)
    retry = json.loads(seen["s_demo retry"].split("\n\n")[0])
    assert retry["unsupported"] == ["m_2"]


def test_paired_statistics():
    from beliefbench.beliefgraph_eval import paired

    K, W = Action.KEEP, Action.WITHDRAW
    items = [{"gold": {"m_1": K, "m_2": W}, "pred_P": {"m_1": K, "m_2": W}, "direct": {"m_1": K, "m_2": K}}
             for _ in range(5)]
    res = paired(items, resamples=200)
    assert res["P_right_direct_wrong"] == 5 and res["direct_right_P_wrong"] == 0
    assert res["accuracy_diff"] == 0.5 and res["mcnemar_exact_p"] == pytest.approx(0.0625)
    assert res["ci95"][0] <= 0.5 <= res["ci95"][1]


def test_cost_by_method_splits_graph_and_direct_calls(tmp_path):
    import importlib.util

    spec = importlib.util.spec_from_file_location("run_bg", Path(__file__).parents[1] / "scripts" / "run_beliefgraph.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for note, usd in (("s_a build", 0.01), ("s_a read", 0.02), ("s_a direct", 0.05), ("s_b direct", 9.0)):
        (tmp_path / f"{note.replace(' ', '.')}.json").write_text(json.dumps(
            {"note": note, "usage": {"input_tokens": 10, "output_tokens": 1, "est_usd": usd}}))
    cost = mod.cost_by_method(tmp_path, {"s_a"})
    assert cost["BeliefGraph"]["calls"] == 2 and cost["BeliefGraph"]["est_usd"] == 0.03
    assert cost["LLM-direct"]["calls"] == 1 and cost["LLM-direct"]["est_usd"] == 0.05


# ── large stores with sequential updates ──


def _pool():
    return [x for r in ALL_RUNS for x in load_accepted(RENDERED / r)]


def test_merged_store_gold_matches_each_scenario_and_oracle_at_every_step():
    from beliefbench.stream import gold_after, merge, step_view

    items = _pool()[:8]
    store, comps = merge(items, seed=1)
    ids = [x["id"] for sec in ("evidence", "memories", "updates") for x in store[sec]]
    assert len(ids) == len(set(ids))  # re-namespacing keeps ids unique across scenarios
    dates = [u["observed"] for u in store["updates"]]
    assert dates == sorted(dates) and min(dates) > max(e["observed"] for e in store["evidence"])
    # each scenario's own updates keep their order inside the stream
    for c in comps:
        mine = [u["id"] for u in store["updates"] if u["id"] in c["back"]]
        own = [c["back"][u] for u in mine]
        assert own == [u["id"] for u in sorted(c["sv"]["updates"], key=lambda u: (u["observed"], u["id"]))]
    # after the full stream, store gold == every scenario's own gold
    union = {}
    for c in comps:
        fwd = {v: k for k, v in c["back"].items()}
        union.update({fwd[m]: a for m, a in memory_gold(c["ev"]).items()})
    assert gold_after(store, comps, len(store["updates"])) == union
    # before any update nothing changes
    assert set(gold_after(store, comps, 0).values()) == {Action.KEEP}
    assert step_view(store, 2, only_last=True)["updates"] == store["updates"][1:2]


def test_stream_step_score():
    import importlib.util

    spec = importlib.util.spec_from_file_location("run_stream", Path(__file__).parents[1] / "scripts" / "run_stream.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    K, W = Action.KEEP, Action.WITHDRAW
    gold = {"m_1": K, "m_2": W, "m_3": K}
    s = mod.step_score(gold, {"m_1": K, "m_2": K, "m_3": W}, {"m_1", "m_2"})
    assert s["acc_all"] == 1 / 3 and s["acc_touched"] == 0.5 and s["stale"] == 1.0 and s["over_invalidation"] == 0.5


def test_batched_build_asks_only_for_each_batch_and_keeps_every_candidate():
    seen = []

    def llm(system, message, note=""):
        body = json.loads(message.split("\n\n")[0])
        seen.append(body)
        js = {m: ([["e_1"]] if m == "m_1" else [["m_1", "e_3"]]) for m in body.get("build_for", [])}
        return json.dumps({"justifications": js, "reliability": GRAPH["reliability"]})

    g = BeliefGraph(llm).build(VIEW, batch_size=1)
    assert [b["build_for"] for b in seen] == [["m_1"], ["m_2"]]
    assert all(len(b["memories"]) == 2 and len(b["facts"]) == 3 for b in seen)  # every candidate visible
    assert g.justifications == {"m_1": [["e_1"]], "m_2": [["e_3", "m_1"]]} and g.unsupported == []


def test_direct_store_baseline_lists_only_changes():
    from beliefbench.llm_baselines import DIRECT_STORE_PROMPT, llm_direct_store

    out, errors = llm_direct_store(lambda s, m, n="": json.dumps({"changes": {"m_2": "withdraw", "m_9": "keep"}}), VIEW)
    assert out == {"m_1": Action.KEEP, "m_2": Action.WITHDRAW} and "unknown memory" in errors[0]
    assert '"changes"' in DIRECT_STORE_PROMPT


def test_parse_graph_ignores_non_string_items_from_small_models():
    raw = json.dumps({"justifications": {"m_1": [["e_1", {"id": "e_2"}], [{"x": 1}]], "m_2": [["m_1", "e_3"]]},
                      "reliability": GRAPH["reliability"]})
    g = parse_graph(raw, VIEW)
    assert g.justifications["m_1"] == [["e_1"]] and g.justifications["m_2"] == [["e_3", "m_1"]]


# ── v0.2: policy-anchored decomposition ──


@pytest.fixture
def tfidf(monkeypatch):
    monkeypatch.setenv("BELIEFGRAPH_RETRIEVAL", "tfidf")  # offline: no embedding model download


def _v02_llm(calls):
    from beliefgraph.prompts import GROUND_PROMPT, RELIABILITY_PROMPT, ROUTE_PROMPT
    from beliefgraph.prompts import ROUTE_OUTCOME_PROMPT

    ROUTERS = (ROUTE_PROMPT, ROUTE_OUTCOME_PROMPT)

    def llm(system, message, note=""):
        calls.append(note)
        body = json.loads(message)
        if system in ROUTERS:
            target = "trucks" if "approved carrier" in body["memory"] else "zero incidents"
            n = next(k for k, t in body["policies"].items() if target.split()[0] in str(t) or "Contracts" in str(t) and target == "zero incidents")
            return json.dumps({"policy": int(n)})
        if system == GROUND_PROMPT:
            ids = {c["text"]: c["id"] for c in body["candidates"]}
            if "approved carrier" in body["memory"]:
                return json.dumps({"groups": [{"all_of": [{"condition": "10+ trucks", "item": ids["Acme has 15 trucks."]}]},
                                              {"all_of": [{"condition": "ISO 9001", "item": ids["Acme holds ISO 9001."]}]}]})
            return json.dumps({"groups": [{"all_of": [
                {"condition": "approved carrier", "item": ids["Acme is an approved carrier."]},
                {"condition": "zero incidents", "item": ids["Acme logged 0 incidents."]}]}]})
        if system == RELIABILITY_PROMPT:
            return json.dumps({"reliability": {e["id"]: "high" for e in body}})
        return json.dumps(READ)
    return llm


def test_v02_builds_the_graph_from_routing_and_grounding(tfidf):
    from beliefgraph.core import DecomposedBeliefGraph

    calls = []
    bg = DecomposedBeliefGraph(_v02_llm(calls), workers=2, samples=1)
    g = bg.build(VIEW)
    assert g.justifications == {"m_1": [["e_1"], ["e_2"]], "m_2": [["e_3", "m_1"]]} and g.unsupported == []
    assert g.reliability == {"e_1": "high", "e_2": "high", "e_3": "high"}
    readings, _ = bg.read_updates(VIEW)
    assert revise(VIEW, g.justifications, g.reliability, readings)["m_1"] is Action.KEEP
    assert sum(c.startswith("s_demo route") for c in calls) == 2 and sum(c.startswith("s_demo ground") for c in calls) == 2


def test_v02_drops_alternatives_with_an_unmet_condition_and_reports_unsupported(tfidf):
    from beliefgraph.core import DecomposedBeliefGraph
    from beliefgraph.prompts import GROUND_PROMPT, ROUTE_PROMPT
    from beliefgraph.prompts import ROUTE_OUTCOME_PROMPT

    ROUTERS = (ROUTE_PROMPT, ROUTE_OUTCOME_PROMPT)

    def llm(system, message, note=""):
        if system in ROUTERS:
            return json.dumps({"policy": 1})
        if system == GROUND_PROMPT:
            return json.dumps({"groups": [{"all_of": [{"condition": "c", "item": None}]},
                                          {"all_of": [{"condition": "c", "item": "e_not_a_candidate"}]}]})
        return json.dumps({"reliability": {}})

    g = DecomposedBeliefGraph(llm, workers=1).build(VIEW)
    assert g.justifications == {"m_1": [], "m_2": []} and g.unsupported == ["m_1", "m_2"]


def test_v02_routes_to_a_wider_tier_when_none_fits(tfidf):
    from beliefgraph.core import DecomposedBeliefGraph
    from beliefgraph.prompts import ROUTE_PROMPT
    from beliefgraph.prompts import ROUTE_OUTCOME_PROMPT

    ROUTERS = (ROUTE_PROMPT, ROUTE_OUTCOME_PROMPT)

    seen = []

    def llm(system, message, note=""):
        if system in ROUTERS:
            seen.append(note)
            return json.dumps({"policy": None})
        return json.dumps({"reliability": {}, "groups": []})

    DecomposedBeliefGraph(llm, k_policies=1, workers=1).build(VIEW)
    assert any("route0" in n for n in seen) and any("route1" in n for n in seen)


def test_v02_reads_each_update_against_its_nearest_facts(tfidf):
    from beliefgraph.core import DecomposedBeliefGraph

    seen = []

    def llm(system, message, note=""):
        seen.append(json.loads(message))
        return json.dumps(READ)

    readings, _ = DecomposedBeliefGraph(llm, k_read=1, workers=1).read_updates(VIEW)
    assert readings["u_1"].target == "e_1" and [f["id"] for f in seen[0]["facts"]] == ["e_1"]


def test_v021_reroutes_when_the_chosen_policy_cannot_be_grounded(tfidf):
    from beliefgraph.core import DecomposedBeliefGraph
    from beliefgraph.prompts import GROUND_PROMPT, ROUTE_PROMPT
    from beliefgraph.prompts import ROUTE_OUTCOME_PROMPT

    ROUTERS = (ROUTE_PROMPT, ROUTE_OUTCOME_PROMPT)

    routes, grounded = [], set()

    def llm(system, message, note=""):
        body = json.loads(message)
        if system in ROUTERS:
            routes.append(note)
            return json.dumps({"policy": 1})  # always the first remaining candidate
        if system == GROUND_PROMPT:
            if note.rsplit(".", 1)[1] in grounded:  # every memory's second grounding finds its premise
                ids = [c["id"] for c in body["candidates"] if c["id"].startswith("e_")]
                return json.dumps({"groups": [[{"condition": "c", "item": ids[0]}]]})  # bare-list group shape
            grounded.add(note.rsplit(".", 1)[1])
            return json.dumps({"groups": [{"all_of": [{"condition": "c", "item": None}]}]})  # a decoy-like miss
        return json.dumps({"reliability": {}})

    g = DecomposedBeliefGraph(llm, workers=1).build(VIEW)
    assert all(g.justifications[m] for m in ("m_1", "m_2")) and g.unsupported == []
    assert any(".r1" in n or "r1" in n.split(" ")[1] for n in routes)  # at least one re-route happened
    assert any("re-routing" in e for e in g.errors)


def test_cycle_breaking_drops_only_the_closing_set():
    from beliefgraph.core import break_cycles

    justs = {"m_1": [["m_2"], ["e_1"]], "m_2": [["m_1"]], "m_3": [["m_2", "e_2"]]}
    errors = []
    break_cycles(justs, errors)
    assert justs == {"m_1": [["e_1"]], "m_2": [["m_1"]], "m_3": [["m_2", "e_2"]]}
    assert len(errors) == 1 and "m_1" in errors[0]


def test_v03_routes_on_what_each_policy_gives(tfidf):
    from beliefgraph.core import DecomposedBeliefGraph
    from beliefgraph.prompts import GROUND_PROMPT, OUTCOME_PROMPT, ROUTE_OUTCOME_PROMPT

    shown = []

    def llm(system, message, note=""):
        body = json.loads(message)
        if system == OUTCOME_PROMPT:  # splits only the trucks policy; the other keeps its full text
            return json.dumps({"policies": {pid: {"gives": "approved carrier", "requires": "10+ trucks or ISO 9001"}
                                            for pid, text in body.items() if "trucks" in text}})
        if system == ROUTE_OUTCOME_PROMPT:
            shown.append(body["policies"])
            return json.dumps({"policy": 1})
        if system == GROUND_PROMPT:
            return json.dumps({"groups": [[body["candidates"][0]["id"]]]})
        return json.dumps({"reliability": {}})

    g = DecomposedBeliefGraph(llm, workers=1, outcome_batch=1, outcome_routing=True).build(VIEW)
    gives = {p["gives"] for pols in shown for p in pols.values()}
    assert "approved carrier" in gives and any("zero incidents" in x for x in gives)
    assert all(set(p) == {"gives", "requires"} for pols in shown for p in pols.values())
    assert any("no outcome split" in e for e in g.errors)


def test_v04_votes_on_routing_and_keeps_majority_sets(tfidf):
    from beliefgraph.core import DecomposedBeliefGraph
    from beliefgraph.prompts import GROUND_PROMPT, ROUTE_PROMPT

    def llm(system, message, note=""):
        body = json.loads(message)
        if system == ROUTE_PROMPT:
            want = "trucks" if "approved carrier" in body["memory"] else "zero incidents"
            right = next(int(k) for k, t in body["policies"].items() if want in t)
            return json.dumps({"policy": right if not note.endswith("~s2") else 3 - right})  # one sample disagrees
        if system == GROUND_PROMPT:
            ids = {c["text"]: c["id"] for c in body["candidates"]}
            if "trucks" in body["policy"]:
                noisy = "~s1" in note  # one sample adds a spurious alternative
                return json.dumps({"groups": [[ids["Acme has 15 trucks."]], [ids["Acme holds ISO 9001."]]]
                                   + ([[ids["Acme logged 0 incidents."]]] if noisy else [])})
            return json.dumps({"groups": [[ids["Acme logged 0 incidents."], next(c["id"] for c in body["candidates"]
                                                                                  if c["id"].startswith("m_"))]]})
        return json.dumps({"reliability": {}})

    g = DecomposedBeliefGraph(llm, workers=1, samples=3).build(VIEW)
    m1 = next(m["id"] for m in VIEW["memories"] if "approved carrier" in m["text"])
    assert len(g.justifications[m1]) == 2  # the 1-of-3 spurious set is voted out
    assert g.confidence[m1] == 2 / 3


def test_v04_conflict_reroutes_the_lower_voted_memory():
    from beliefgraph.core import DecomposedBeliefGraph

    out = {"m_a": {"policy": "p_1", "share": 1.0, "sets": [["e_1"]]},
           "m_b": {"policy": "p_1", "share": 2 / 3, "sets": [["e_1", "e_2"]]},
           "m_c": {"policy": "p_1", "share": 1 / 3, "sets": [["e_9"]]},  # same rule, other facts: no conflict
           "m_d": {"policy": "p_2", "share": 1.0, "sets": [["m_e"]]},
           "m_e": {"policy": "p_2", "share": 1.0, "sets": [["e_3"]]}}  # m_d rests on m_e: m_d loses
    mems = {m: {"text": m} for m in out}
    pols = {"p_1": {"text": "x"}, "p_2": {"text": "y"}}
    assert DecomposedBeliefGraph._conflict_losers(out, mems, pols) == ["m_b", "m_d"]


def test_v04_adjudicates_split_votes_with_grounded_candidates(tfidf):
    from beliefgraph.core import DecomposedBeliefGraph
    from beliefgraph.prompts import ADJUDICATE_PROMPT, GROUND_PROMPT, ROUTE_PROMPT

    shown = []

    def llm(system, message, note=""):
        body = json.loads(message)
        if system == ROUTE_PROMPT:
            if "contract" not in body["memory"]:
                return json.dumps({"policy": next(int(k) for k, t in body["policies"].items() if "trucks" in t)})
            wrong = next(int(k) for k, t in body["policies"].items() if "trucks" in t)  # 2 of 3 samples err
            return json.dumps({"policy": 3 - wrong if note.endswith("~s2") else wrong})
        if system == GROUND_PROMPT:
            return json.dumps({"groups": [[c["id"]] for c in body["candidates"] if c["id"] == "e_1"]})
        if system == ADJUDICATE_PROMPT:
            shown.append(body["policies"])
            return json.dumps({"policy": next(int(k) for k, v in body["policies"].items() if "Contracts" in v["policy"])})
        return json.dumps({"reliability": {}})

    g = DecomposedBeliefGraph(llm, workers=1).build(VIEW)
    assert shown and all("premises" in v for v in shown[0].values())
    assert any("adjudicated" in e for e in g.errors) and g.confidence["m_2"] == 1.0
