"""Model-free tests for the renderer pipeline, using a hand-written rendering."""

import json

import pytest

from beliefbench.generate import generate_suite
from beliefbench.labeler import gold_actions
from beliefbench.render import leakcheck
from beliefbench.render.prompt import SYSTEM_PROMPT, parse_response, renderer_payload, user_message
from beliefbench.render.review import CHECKLIST, read_decisions, review_sheet, write_csv_template
from beliefbench.render.views import SYSTEM_VIEW_KEYS, build_views
from beliefbench.schema import Kind, Node, Relation, Scenario, Update


def spec_example() -> Scenario:
    # RESEARCH_SPEC.md 4.1, plus one unrelated distractor.
    s = Scenario("F2-900", "F2", "product_eligibility", [
        Node("E1", Kind.EVIDENCE, t=1), Node("E2", Kind.EVIDENCE, t=2), Node("E3", Kind.EVIDENCE, t=3),
        Node("E4", Kind.EVIDENCE, t=4),
        Node("B1", Kind.BELIEF, justifications=[["E1"], ["E3"]]),
        Node("B2", Kind.BELIEF, justifications=[["B1", "E2"]]),
        Node("D1", Kind.DECISION, justifications=[["B2"]]),
        Node("B3", Kind.BELIEF, justifications=[["E4"]]),
    ], [Update("U1", 5, "E1", Relation.RETRACTS)])
    s.validate()
    s.gold = gold_actions(s)
    return s


GOOD = {
    "world": "A bank decides which savings product to offer a customer in Thailand.",
    "nodes": {
        "E1": {"text": "The Q1 2026 product catalogue lists the Horizon Saver account for Thai residents.",
               "source": "Bank product catalogue, Q1 2026"},
        "E2": {"text": "Nok Phairot, a Bangkok resident, is 34 and meets Horizon Saver's age band of 18 to 60.",
               "source": "Customer onboarding record"},
        "E3": {"text": "The Bangkok branch network is actively opening Horizon Saver accounts this quarter.",
               "source": "Regional operations dashboard"},
        "E4": {"text": "The Chiang Mai office relocates to Nimman Road in March.", "source": "Facilities memo"},
        "B1": {"text": "Horizon Saver can be opened in Thailand."},
        "B2": {"text": "Nok qualifies for a Horizon Saver account."},
        "D1": {"text": "Offer Nok the Horizon Saver account at the next review call."},
        "B3": {"text": "Client meetings in Chiang Mai move to the new Nimman Road site."},
    },
    "updates": {"U1": {"text": "The Q3 2026 catalogue no longer lists Horizon Saver for Thai residents.",
                       "source": "Bank product catalogue, Q3 2026"}},
    "rationale": {
        "B1": ["The catalogue listing makes it available.", "Branches opening accounts shows it is available."],
        "B2": ["Availability plus age eligibility make Nok eligible."],
        "D1": ["An eligible customer should be offered the product."],
        "B3": ["The relocation moves meetings."],
    },
}


def test_payload_and_prompt_carry_no_gold_or_family():
    s = spec_example()
    payload = renderer_payload(s)
    assert "gold" not in json.dumps(payload) and "F2" not in json.dumps(payload)
    groups = {d["id"]: d["group"] for d in payload["derived"]}
    assert groups["B3"] != groups["B1"]  # distractor is its own component
    assert "justification_sets" in user_message(s)
    assert "never shown to the system under test" in SYSTEM_PROMPT


def test_parse_response_validates_structure():
    s = spec_example()
    assert parse_response(s, json.dumps(GOOD)).ok
    bad = json.loads(json.dumps(GOOD))
    del bad["nodes"]["B2"]
    bad["rationale"]["B1"] = ["only one"]
    bad["nodes"]["X9"] = {"text": "stray"}
    errs = parse_response(s, json.dumps(bad)).errors
    assert any("B2: missing text" in e for e in errs)
    assert any("B1: expected 2 rationale" in e for e in errs)
    assert any("unknown ids" in e for e in errs)
    assert parse_response(s, "not json").errors[0].startswith("invalid JSON")


def test_system_view_hides_structure_and_eval_view_keeps_it():
    s = spec_example()
    system, evaluation = build_views(s, parse_response(s, json.dumps(GOOD)), seed=0)
    assert set(system) == SYSTEM_VIEW_KEYS
    blob = json.dumps(system)
    for forbidden in ("justification", "gold", "rationale", "F2", "E1", "B1", "keep", "withdraw", "family"):
        assert forbidden not in blob, forbidden
    # Eval view maps back to the original gold exactly.
    inv = {v: k for k, v in evaluation["idmap"].items()}
    assert {inv[k]: v for k, v in evaluation["gold"].items()} == {k: v.value for k, v in s.gold.items()}
    # Updates come after all evidence.
    assert max(e["observed"] for e in system["evidence"]) < system["updates"][0]["observed"]


def test_timestamp_permutation_never_changes_gold():
    for s in generate_suite(10, seed=0):
        fake = {"world": "w", "nodes": {n.id: {"text": f"text {i}", "source": "src"} for i, n in enumerate(s.nodes)},
                "updates": {u.id: {"text": "upd", "source": "src"} for u in s.updates},
                "rationale": {n.id: ["r"] * len(n.justifications) for n in s.nodes if not n.is_evidence}}
        system, evaluation = build_views(s, parse_response(s, json.dumps(fake)), seed=3)
        inv = {v: k for k, v in evaluation["idmap"].items()}
        assert {inv[k]: v for k, v in evaluation["gold"].items()} == {k: v.value for k, v in s.gold.items()}


def test_leak_flags():
    s = spec_example()
    system, evaluation = build_views(s, parse_response(s, json.dumps(GOOD)), seed=0)
    assert leakcheck.text_flags(system) == []
    leaky = json.loads(json.dumps(GOOD))
    leaky["nodes"]["B1"]["text"] = "Since both reports agree, Horizon Saver can be opened in Thailand."
    leaky["nodes"]["B2"]["text"] = "Per E2, Nok qualifies (premise check done)."
    system2, _ = build_views(s, parse_response(s, json.dumps(leaky)), seed=0)
    kinds = {(f.kind, f.hard) for f in leakcheck.text_flags(system2)}
    assert ("explains_reason", False) in kinds and ("mentions_sources", False) in kinds
    assert ("graph_id", True) in kinds and ("label_word", True) in kinds
    system2["gold"] = {}
    assert any(f.kind == "unexpected_key" for f in leakcheck.text_flags(system2))


def test_lexical_heuristic_and_auc():
    s = spec_example()
    system, evaluation = build_views(s, parse_response(s, json.dumps(GOOD)), seed=0)
    rep = leakcheck.check([(system, evaluation)])
    summ = rep.summary()
    assert summ["hard_flags"] == 0
    assert 0.0 <= summ["lexical_heuristic"]["justification_set_f1"] <= 1.0
    assert 0.0 <= summ["premise_overlap_auc_mean"] <= 1.0
    # A rendering that copies premise wording into conclusions is recovered by word matching.
    copy = json.loads(json.dumps(GOOD))
    copy["nodes"]["B3"]["text"] = "The Chiang Mai office relocates to Nimman Road in March, so meetings move."
    sys3, ev3 = build_views(s, parse_response(s, json.dumps(copy)), seed=0)
    pred = leakcheck.lexical_justifications(sys3)
    b3 = ev3["idmap"]["B3"]
    assert pred[b3] == [[ev3["idmap"]["E4"]]]


def test_template_flags():
    systems = [{"scenario": f"s{i}", "memories": [{"text": "It is confirmed that the plan works."}]} for i in range(10)]
    assert any("confirmed that the" in g or "is confirmed that" in g for g, _ in leakcheck.template_flags(systems))


def test_review_sheet_and_decisions(tmp_path):
    s = spec_example()
    system, evaluation = build_views(s, parse_response(s, json.dumps(GOOD)), seed=0)
    md = review_sheet(system, evaluation, [])
    assert "System view" in md and all(c in md for c, _ in CHECKLIST)
    assert md.index("System view") < md.index("Intended structure")
    path = tmp_path / "review.csv"
    write_csv_template(path, [system["scenario"]], reviewer="tr")
    with pytest.raises(ValueError):
        read_decisions(path)  # unfilled
    text = path.read_text().splitlines()
    cells = ["pass"] * len(CHECKLIST)
    cells[1] = "fail"
    text[1] = ",".join([system["scenario"], "tr", *cells, "revise", "B2 does not need the age fact"])
    path.write_text("\n".join(text) + "\n")
    assert read_decisions(path)[0]["decision"] == "revise"


def test_view_refuses_scenarios_whose_gold_depends_on_recency():
    s = Scenario("x", "F7", "travel_logistics", [Node("E1", Kind.EVIDENCE, t=5),
                 Node("B1", Kind.BELIEF, justifications=[["E1"]])], [Update("U1", 3, "E1", Relation.RETRACTS)])
    s.validate()
    s.gold = gold_actions(s)  # outdated update: everything kept
    fake = {"world": "w", "nodes": {"E1": {"text": "t", "source": "s"}, "B1": {"text": "b"}},
            "updates": {"U1": {"text": "u", "source": "s"}}, "rationale": {"B1": ["r"]}}
    with pytest.raises(ValueError, match="changed gold"):
        build_views(s, parse_response(s, json.dumps(fake)))
