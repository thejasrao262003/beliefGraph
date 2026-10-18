"""Model-free tests for the renderer pipeline (render-v2), using hand-written renderings."""

import copy
import json

import pytest

from beliefbench.generate import generate_suite
from beliefbench.labeler import gold_actions
from beliefbench.render import leakcheck
from beliefbench.render.prompt import (
    PROMPT_VERSION,
    SYSTEM_PROMPT,
    parse_response,
    renderer_payload,
    user_message,
)
from beliefbench.render.review import CHECKLIST, read_decisions, review_sheet, write_csv_template
from beliefbench.render.views import SYSTEM_VIEW_KEYS, build_views, timeline
from beliefbench.schema import Kind, Node, Relation, Scenario, Update


V2_SHA256 = "3c5920c2487ba6147ec71679ee789a152d8f6d2f145109787c81d083f1828d3e"


def spec_example() -> Scenario:
    # RESEARCH_SPEC.md 4.1, plus one unrelated distractor (B3 <= E4).
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
        "E1": {"text": "The current product catalogue lists the Horizon Saver account for Thai residents.",
               "source": "Bank product catalogue"},
        "E2": {"text": "Nok Phairot, a Bangkok resident, is 34 years old.", "source": "Customer onboarding record"},
        "E3": {"text": "Bangkok branches are actively opening Horizon Saver accounts this quarter.",
               "source": "Regional operations dashboard"},
        "E4": {"text": "Lanna Logistics moves its Chiang Mai office to Nimman Road next month.",
               "source": "Facilities memo"},
        "B1": {"text": "Horizon Saver can be opened in Thailand."},
        "B2": {"text": "Nok can hold a Horizon Saver account."},
        "D1": {"text": "Offer Nok the Horizon Saver account at the next review call."},
        "B3": {"text": "Meetings with Lanna Logistics take place on Nimman Road."},
    },
    "updates": {"U1": {"text": "The newest catalogue no longer lists Horizon Saver for Thai residents.",
                       "source": "Bank product catalogue, revised edition"}},
    "policies": {
        "B1": "A product counts as available in a country if the current catalogue lists it there, or if local "
              "offices are currently signing up holders for it.",
        "B2": "A resident of a country where an account is available may hold it if they are between 18 and 60.",
        "D1": "Offer an account to any customer who may hold it.",
        "B3": "Client meetings take place at a partner's current office address.",
    },
    "decoy_policies": ["A fixed-term deposit may be renewed early if the holder has kept it for at least half its term."],
    "after_updates": {"B1": "holds", "B2": "holds", "D1": "holds", "B3": "holds"},
    "rationale": {
        "B1": ["The catalogue listing makes it available.", "Branches opening accounts shows it is available."],
        "B2": ["Availability plus age eligibility make Nok eligible."],
        "D1": ["An eligible customer should be offered the product."],
        "B3": ["The relocation moves meetings."],
    },
}


def views(resp=GOOD, s=None, seed=0):
    s = s or spec_example()
    return build_views(s, parse_response(s, json.dumps(resp)), seed=seed)


def fake_response(s):
    return {"world": "w", "nodes": {n.id: {"text": f"Text number {i}.", "source": "Registry office"}
                                    for i, n in enumerate(s.nodes)},
            "updates": {u.id: {"text": "A later notice changed this.", "source": "Registry office"} for u in s.updates},
            "policies": {n.id: f"Rule {i} applies." for i, n in enumerate(s.nodes) if not n.is_evidence},
            "decoy_policies": ["An unrelated rule applies elsewhere."],
            "after_updates": {n.id: "holds" for n in s.nodes if not n.is_evidence},
            "rationale": {n.id: ["r"] * len(n.justifications) for n in s.nodes if not n.is_evidence}}


# ── prompt, payload, parsing ──


def test_payload_carries_dates_but_no_gold_or_family():
    s = spec_example()
    payload = renderer_payload(s, seed=0)
    blob = json.dumps(payload)
    assert "gold" not in blob and "F2" not in blob
    groups = {d["id"]: d["group"] for d in payload["derived"]}
    assert groups["B3"] != groups["B1"]
    obs = {e["id"]: e["observed"] for e in payload["evidence"]} | {u["id"]: u["observed"] for u in payload["updates"]}
    assert obs == timeline(s, 0)
    assert PROMPT_VERSION == "render-v6" and "DECOY POLICIES" in SYSTEM_PROMPT and "never shown" in SYSTEM_PROMPT
    assert "justification_sets" in user_message(s)


def test_renderer_dates_match_system_view_dates():
    s = spec_example()
    system, evaluation = views(s=s, seed=7)
    tl = timeline(s, 7)
    inv = {v: k for k, v in evaluation["idmap"].items()}
    for item in system["evidence"] + system["updates"]:
        assert item["observed"] == tl[inv[item["id"]]]


def test_parse_response_requires_policies_and_validates():
    s = spec_example()
    assert parse_response(s, json.dumps(GOOD)).ok
    bad = copy.deepcopy(GOOD)
    del bad["nodes"]["B2"]
    del bad["policies"]["D1"]
    bad["rationale"]["B1"] = ["only one"]
    bad["policies"]["E1"] = "evidence cannot have a policy"
    errs = parse_response(s, json.dumps(bad)).errors
    assert any("B2: missing text" in e for e in errs)
    assert any("D1: missing policy" in e for e in errs)
    assert any("B1: expected 2 rationale" in e for e in errs)
    assert any("unknown ids" in e and "E1" in e for e in errs)
    assert parse_response(s, "not json").errors[0].startswith("invalid JSON")


# ── separation ──


def test_system_view_hides_structure_and_eval_view_keeps_it():
    s = spec_example()
    system, evaluation = views(s=s)
    assert set(system) == SYSTEM_VIEW_KEYS and len(system["policies"]) == 5  # 4 real + 1 decoy
    blob = json.dumps(system)
    for forbidden in ("justification", "gold", "rationale", "groups", "policy_of", "decoy", "after_updates",
                      "final_state", "holds", "F2", "E1", "B1", "keep", "withdraw", "family"):
        assert forbidden not in blob, forbidden
    inv = {v: k for k, v in evaluation["idmap"].items()}
    assert {inv[k]: v for k, v in evaluation["gold"].items()} == {k: v.value for k, v in s.gold.items()}
    assert {inv[m] for m in evaluation["policy_of"].values()} == {"B1", "B2", "D1", "B3"}
    assert max(e["observed"] for e in system["evidence"]) < system["updates"][0]["observed"]


def test_timestamp_permutation_never_changes_gold():
    for s in generate_suite(10, seed=0):
        system, evaluation = build_views(s, parse_response(s, json.dumps(fake_response(s))), seed=3)
        inv = {v: k for k, v in evaluation["idmap"].items()}
        assert {inv[k]: v for k, v in evaluation["gold"].items()} == {k: v.value for k, v in s.gold.items()}


def test_view_refuses_scenarios_whose_gold_depends_on_recency():
    s = Scenario("x", "F7", "travel_logistics", [Node("E1", Kind.EVIDENCE, t=5),
                 Node("B1", Kind.BELIEF, justifications=[["E1"]])], [Update("U1", 3, "E1", Relation.RETRACTS)])
    s.validate()
    s.gold = gold_actions(s)  # outdated update: everything kept
    with pytest.raises(ValueError, match="changed gold"):
        build_views(s, parse_response(s, json.dumps(fake_response(s))))


# ── leak checks: regression tests for smoke-test-1 problems P2-P6 ──


def kinds(flags):
    return {(f.kind, f.hard) for f in flags}


def with_text(item, text, field="text"):
    r = copy.deepcopy(GOOD)
    (r["nodes"] if item in r["nodes"] else r["updates"])[item][field] = text
    return r


def test_clean_rendering_has_no_flags():
    system, evaluation = views()
    assert leakcheck.text_flags(system) == []
    assert leakcheck.group_flags(system, evaluation) == []


def test_gold_detector_positive_and_negative():
    # P3: "Gold" as a card tier is fine; the label phrase is a hard leak.
    system, _ = views(with_text("E2", "Nok Phairot, 34, holds a Gold tier debit card."))
    assert not [f for f in leakcheck.text_flags(system) if f.hard]
    system, _ = views(with_text("B2", "Nok can hold a Horizon Saver account (gold label: keep)."))
    assert ("label_word", True) in kinds(leakcheck.text_flags(system))


@pytest.mark.parametrize("source", ["high", "Site Survey Report, high", "Anonymous forum post (low)",
                                    "Partner email, medium reliability"])
def test_reliability_label_in_source_is_hard(source):
    # P2
    system, _ = views(with_text("E3", source, field="source"))
    assert any(f.hard and f.kind in ("reliability_label", "reliability_word") for f in leakcheck.text_flags(system))


def test_natural_source_words_are_not_flagged():
    system, _ = views(with_text("E3", "High Court registry extract", field="source"))
    assert not [f for f in leakcheck.text_flags(system) if f.hard]


def test_distractor_about_same_customer_is_flagged():
    # P4: the distractor group mentions the main chain's customer.
    r = copy.deepcopy(GOOD)
    r["nodes"]["E4"]["text"] = "Nok Phairot moves her office to Nimman Road next month."
    system, evaluation = views(r)
    assert ("cross_group_entity", False) in kinds(leakcheck.group_flags(system, evaluation))
    r2 = copy.deepcopy(GOOD)
    r2["nodes"]["E2"]["text"] = "The customer is 34 years old."
    r2["nodes"]["E4"]["text"] = "The customer moves the office to Nimman Road."
    system, evaluation = views(r2)
    assert ("unnamed_entity_in_groups", False) in kinds(leakcheck.group_flags(system, evaluation))


def test_distinct_entities_are_not_flagged():
    system, evaluation = views()
    assert not leakcheck.group_flags(system, evaluation)


def test_dates_after_observed_are_hard_and_dates_in_memories_flagged():
    # P5: the view dates evidence in Jan-Feb 2026.
    system, _ = views(with_text("E2", "On October 3, 2026, Nok Phairot turned 34."))
    assert ("date_after_observed", True) in kinds(leakcheck.text_flags(system))
    system, _ = views(with_text("E2", "Since January 2025 Nok Phairot has lived in Bangkok; she is 34."))
    assert not [f for f in leakcheck.text_flags(system) if f.kind == "date_after_observed"]
    system, _ = views(with_text("B2", "Nok can hold a Horizon Saver account from 2025-06-01."))
    assert any(f.kind == "date_in_memory" for f in leakcheck.text_flags(system))
    assert leakcheck.dates_in("on 3 March 2026 and in May 2025") == [
        __import__("datetime").date(2026, 3, 3), __import__("datetime").date(2025, 5, 1)]


def test_order_cues_are_flagged():
    # P6
    system, _ = views(with_text("B2", "Nok passes the preliminary check for Horizon Saver."))
    assert ("order_cue", False) in kinds(leakcheck.text_flags(system))


def test_policy_naming_the_subject_entity_is_flagged_but_terms_are_not():
    r = copy.deepcopy(GOOD)
    r["policies"]["B2"] = "Nok Phairot may hold the account if she is between 18 and 60."
    r["policies"]["B1"] = "A product with ISO 27001 and Tier-1 status counts as available."
    system, _ = views(r)
    flags = [f for f in leakcheck.text_flags(system) if f.kind == "policy_names_subject"]
    assert len(flags) == 1 and "Nok" in flags[0].match
    assert "Nok Phairot" in leakcheck.subject_names(system)
    r["decoy_policies"] = ["Lanna Logistics may renew a lease early."]
    system, _ = views(r)
    assert any("Lanna" in f.match for f in leakcheck.text_flags(system) if f.kind == "policy_names_subject")


def test_lexical_heuristics_and_gate():
    system, evaluation = views()
    summ = leakcheck.check([(system, evaluation)]).summary()
    assert summ["hard_flags"] == 0
    for key in ("lexical_heuristic", "policy_assisted_heuristic"):
        assert 0.0 <= summ[key]["justification_set_f1"] <= 1.0
    assert summ["lexical_gate"]["threshold"] == 0.50
    # Copying premise wording into a conclusion is recovered by word matching.
    copied = with_text("B3", "Lanna Logistics moves its Chiang Mai office to Nimman Road, so meetings move.")
    sys3, ev3 = views(copied)
    assert leakcheck.lexical_justifications(sys3)[ev3["idmap"]["B3"]] == [[ev3["idmap"]["E4"]]]


def test_template_flags():
    systems = [{"scenario": f"s{i}", "memories": [{"text": "It is confirmed that the plan works."}]} for i in range(10)]
    assert any("confirmed that the" in g or "is confirmed that" in g for g, _ in leakcheck.template_flags(systems))


# ── review ──


def test_review_sheet_and_decisions(tmp_path):
    system, evaluation = views()
    md = review_sheet(system, evaluation, [])
    assert "System view" in md and "policies:" in md and all(c in md for c, _ in CHECKLIST)
    assert md.index("System view") < md.index("Intended structure")
    assert {"C8_inferable", "C9_no_hidden_needed", "C10_unambiguous", "C11_policy_not_graph", "C12_decoys_inert",
            "C13_final_state"} <= {c for c, _ in CHECKLIST}
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


# ── render-v3 ──


def test_v2_prompt_is_kept_verbatim():
    import hashlib

    from beliefbench.render.prompt import PROMPTS, SYSTEM_PROMPT_V2

    assert hashlib.sha256(SYSTEM_PROMPT_V2.encode()).hexdigest() == V2_SHA256
    assert PROMPTS["render-v3"].startswith(SYSTEM_PROMPT_V2[:200]) and "VOCABULARY SEPARATION" in PROMPTS["render-v3"]


def test_v3_requires_decoys_and_after_updates_but_v2_does_not():
    s = spec_example()
    bad = copy.deepcopy(GOOD)
    del bad["decoy_policies"]
    bad["after_updates"]["B2"] = "maybe"
    errs = parse_response(s, json.dumps(bad)).errors
    assert any("decoy" in e for e in errs) and any("B2: after_updates" in e for e in errs)
    assert parse_response(s, json.dumps(bad), version="render-v2").ok


def test_decoys_are_visible_but_unlinked_and_final_state_is_separate():
    s = spec_example()
    system, evaluation = views(s=s)
    (decoy,) = evaluation["decoy_policies"]
    assert decoy in {p["id"] for p in system["policies"]} and decoy not in evaluation["policy_of"]
    inv = {v: k for k, v in evaluation["idmap"].items()}
    assert {inv[m]: st for m, st in evaluation["final_state"].items()} == {
        "B1": "holds", "B2": "holds", "D1": "holds", "B3": "holds"}


def test_recompute_final_state_comes_from_rederivation():
    from beliefbench.generate import generate_suite

    s = next(sc for sc in generate_suite(10, seed=0, families=["F1"]) if sc.meta["relation"] == "supersedes")
    resp = fake_response(s)
    resp["after_updates"] = {n.id: "fails" for n in s.nodes if not n.is_evidence}
    for n in s.nodes:  # distractors are kept, so they hold
        if not n.is_evidence and s.gold[n.id].value == "keep":
            resp["after_updates"][n.id] = "holds"
    system, evaluation = build_views(s, parse_response(s, json.dumps(resp)))
    inv = {v: k for k, v in evaluation["idmap"].items()}
    for m, st in evaluation["final_state"].items():
        action = s.gold[inv[m]].value
        assert st == ("fails" if action == "recompute" else "holds")
    assert {evaluation["gold"][m] for m in evaluation["final_state"]} >= {"recompute"}  # action stays recompute
    assert leakcheck.consistency_flags(system, evaluation) == []


def test_consistency_flags():
    system, evaluation = views()
    assert leakcheck.consistency_flags(system, evaluation) == []
    r = copy.deepcopy(GOOD)
    r["after_updates"]["B1"] = "fails"  # gold keep: B1 still has the branch support
    system, evaluation = views(r)
    assert [f.kind for f in leakcheck.consistency_flags(system, evaluation)] == ["final_state_mismatch"]


def test_report_has_precision_and_recall():
    summ = leakcheck.check([views()]).summary()
    for key in ("lexical_heuristic", "policy_assisted_heuristic"):
        assert {"edge_precision", "edge_recall", "justification_set_precision", "justification_set_recall"} <= set(summ[key])


# ── render-v4 (external review of smoke test 3) ──

V3_SHA256 = "d20ac3c35ab915586d6283209c5b6f0a91e98ab8f3bea11ee42a3138ca84ee5e"


def test_v3_prompt_is_kept_verbatim_and_v4_extends_it():
    import hashlib

    from beliefbench.render.prompt import PROMPT_VERSION as current, PROMPTS

    assert hashlib.sha256(PROMPTS["render-v3"].encode()).hexdigest() == V3_SHA256
    assert "HARD RULE" in PROMPTS["render-v4"] and "flatly states" in PROMPTS["render-v4"]
    assert current == "render-v6"


def _system(memories, policies, evidence=()):
    return {"scenario": "s_x", "domain": "d", "updates": [],
            "evidence": [{"id": f"e_{i:04x}", "observed": "2026-01-08", "source": "Registry", "text": t}
                         for i, t in enumerate(evidence)],
            "memories": [{"id": f"m_{i:04x}", "text": t} for i, t in enumerate(memories)],
            "policies": [{"id": f"p_{i:04x}", "text": t} for i, t in enumerate(policies)]}


def test_echo_flag_catches_smoke3_f1_and_f2_patterns():
    # F1 (failed review): memory phrase reused in its own and in another memory's policy.
    f1 = _system(["Apex Dynamics meets the operational risk threshold for enterprise status."],
                 ["Preferred Partner Discount prerequisites are fulfilled when an account meets the operational "
                  "risk threshold for enterprise status and retains a designated account executive team."])
    flags = leakcheck.echo_flags(f1)
    assert flags and flags[0].hard and "operational risk threshold" in flags[0].match
    # F2 (accepted by the reviewer, same pattern): flagged too, so the rule is applied uniformly.
    f2 = _system(["Apex Tech Solutions qualifies for standard partner tier standing."],
                 ["A dedicated client specialist is designated for any account possessing standard partner tier standing."])
    assert leakcheck.echo_flags(f2)


def test_echo_flag_allows_proper_names_and_paraphrase():
    ok = _system(["Enroll Apex Dynamics in the Preferred Partner Discount program."],
                 ["Program enrollment for the Preferred Partner Discount is authorized for clients cleared on all "
                  "prerequisite grounds."])
    assert leakcheck.echo_flags(ok) == []
    assert leakcheck.shared_phrases("meets the commercial stability benchmark",
                                    "commercial stability status is attained") == set()


def test_retraction_that_reads_as_hedge_is_flagged():
    s = spec_example()
    r = copy.deepcopy(GOOD)
    r["updates"]["U1"]["text"] = "An anonymous post claims the catalogue no longer lists Horizon Saver."
    system, evaluation = views(r, s=s)
    assert [f.kind for f in leakcheck.relation_flags(system, evaluation)] == ["retraction_reads_as_hedge"]
    system, evaluation = views(s=s)  # flat denial
    assert leakcheck.relation_flags(system, evaluation) == []


# ── render-v5 (v4 re-render: over-paraphrase, decoy closer than the real policy) ──

V4_SHA256 = "dd74235d2fdda437b4a2598438ec991a449485a3607aaaec3c08d83d40fdc9cc"


def test_v4_prompt_is_kept_verbatim_and_v5_extends_it():
    import hashlib

    from beliefbench.render.prompt import PROMPTS

    assert hashlib.sha256(PROMPTS["render-v4"].encode()).hexdigest() == V4_SHA256
    assert "OUTCOME NAMING" in PROMPTS["render-v5"] and "QUANTITY NAMING" in PROMPTS["render-v5"]
    assert "organic" in PROMPTS["render-v5"]


def test_decoy_sharing_a_distinctive_memory_word_is_hard():
    # v4 F6: food-certification decoy shares "organic" with the Dermacool memory.
    s = _system(["Dermacool Gel meets organic cosmetics formulation standards.",
                 "Vendor X receives preferred supplier status."],
                ["Food service products obtain organic retail certification if ingredients come from certified farms.",
                 "A vendor receives expedited renewal status with quarterly volume above 5 million."])
    ev = {"decoy_policies": ["p_0000", "p_0001"]}
    flags = leakcheck.decoy_word_flags(s, ev)
    assert [(f.item, f.match, f.hard) for f in flags] == [("p_0000", "organic", True)]  # generic words and numbers ignored


def test_real_policies_are_not_decoy_checked():
    s = _system(["Dermacool Gel meets organic cosmetics formulation standards."],
                ["Cosmetics earn organic formulation standing when tests show no synthetic preservatives."])
    assert leakcheck.decoy_word_flags(s, {"decoy_policies": []}) == []


def test_decoy_check_ignores_entity_names_but_not_outcome_terms():
    # v5 F2 false positive: "logistics" only from the entity name "Apex Logistics".
    ev = ["Apex Logistics operates 40 vans with an average age of 3 years."]
    mems = ["Apex Logistics meets the qualification criteria for Tier-1 Freight Coverage."]
    decoys = {"decoy_policies": ["p_0000"]}
    ok = _system(mems, ["A logistics firm secures Executive Vendor Status above 5 million dollars in billing."], ev)
    assert leakcheck.decoy_word_flags(ok, decoys) == []
    # Genuine outcome/programme collision is still rejected.
    bad = _system(mems, ["Tier-2 Freight Coverage is granted to carriers with refrigerated trailers."], ev)
    assert {"freight", "coverage"} <= set(leakcheck.decoy_word_flags(bad, decoys)[0].match.split(","))
    # A word in the entity name AND in the outcome wording still counts.
    both = _system(["Apex Logistics wins the logistics excellence award."],
                   ["A logistics excellence award goes to carriers with zero late deliveries."], ev)
    assert "logistic" in leakcheck.decoy_word_flags(both, decoys)[0].match


def test_prior_spend_makes_the_cap_cumulative():
    from beliefbench.render.lyzr_client import BudgetExceeded, SpendGuard

    g = SpendGuard(budget_usd=0.30, max_calls=5, model="gemini-3.5-flash", spent_usd=0.124)
    with pytest.raises(BudgetExceeded):
        g.check(200_000)  # a huge prompt cannot fit in the remaining 0.176


# ── policy <-> evidence echoes (gap found in v5 F6) ──


def test_policy_echoing_evidence_is_hard_v5_f6_phrases():
    ev = ["Vance Medical Supplies possesses an active state pharmaceutical distribution license.",
          "Oakhaven Farms holds official organic processing certification from the Department of Agriculture."]
    pol = ["Clearance for thermal-sensitive pharmaceuticals requires preferred partner rating alongside a valid "
           "state pharmaceutical distribution license.",
           "ECO-label trade rights are granted to an agricultural producer maintaining official organic processing "
           "certification."]
    flags = [f for f in leakcheck.echo_flags(_system([], pol, ev)) if f.kind == "policy_echoes_evidence"]
    matches = " | ".join(f.match for f in flags)
    assert len(flags) == 2 and all(f.hard for f in flags)
    assert "state pharmaceutical distribution" in matches and "organic processing certification" in matches


def test_unrelated_policy_wording_passes_evidence_echo_check():
    ev = ["Vance Medical Supplies possesses an active state pharmaceutical distribution license."]
    pol = ["Clearance for temperature-controlled medicines requires a partner rating and a current regional "
           "dispensing permit."]
    assert leakcheck.echo_flags(_system([], pol, ev)) == []


def test_standard_names_stay_exempt_documented_f2_case():
    # F2 (v5): "active ISO 22000 certification" in policy vs "active ISO 22000 food safety management
    # certification" in evidence. Standard names are exempt by the documented rule, so the lexical check
    # does not flag it; the AI pre-review failed C7/C11 on it, and that call is left to the human review.
    ev = ["Apex Logistics holds an active ISO 22000 food safety management certification."]
    pol = ["An enterprise is granted approval for Tier-1 Freight Coverage if it maintains active ISO 22000 certification."]
    assert leakcheck.echo_flags(_system([], pol, ev)) == []


def test_quantity_phrases_are_exempt_from_echo_check():
    ev = ["Vance Medical Supplies operates a refrigerated storage facility measuring 2,500 square meters."]
    pol = ["Catalog access requires a cold storage facility of no less than 1,500 square meters."]
    assert leakcheck.echo_flags(_system([], pol, ev)) == []


V5_SHA256 = "d8368d88a2d57a49226e69446089147d5f4c3ca68a0a49dc31de865e8b17e543"


def test_v5_prompt_is_kept_verbatim_and_v6_adds_fact_rule():
    import hashlib

    from beliefbench.render.prompt import PROMPTS

    assert hashlib.sha256(PROMPTS["render-v5"].encode()).hexdigest() == V5_SHA256
    v6 = PROMPTS["render-v6"]
    assert "HARD RULE (facts)" in v6 and "number+unit phrases" in v6 and "Never replace a clear" in v6
