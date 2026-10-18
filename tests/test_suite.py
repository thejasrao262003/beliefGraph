import json
import random

from beliefbench.baselines import direct_only, naive_cascade, oracle_jtms, perturb_justifications
from beliefbench.cli import main
from beliefbench.generate import generate_suite
from beliefbench.labeler import gold_actions
from beliefbench.metrics import ExtractionScore, RevisionScore
from beliefbench.schema import Action, Scenario


def score(suite, system):
    s = RevisionScore()
    for sc in suite:
        s.add(sc.gold, system(sc))
    return s.summary()


def test_generation_is_deterministic_and_valid():
    a = generate_suite(10, seed=3)
    b = generate_suite(10, seed=3)
    assert [s.to_dict() for s in a] == [s.to_dict() for s in b]
    assert len(a) == 40
    for s in a:
        s.validate()
        assert s.gold == gold_actions(s)


def test_roundtrip_through_json():
    for s in generate_suite(3, seed=1):
        back = Scenario.from_dict(json.loads(json.dumps(s.to_dict())))
        assert back == s


def test_f2_preserves_belief_when_a_support_survives():
    for s in generate_suite(20, seed=0, families=["F2"]):
        belief = next(n for n in s.nodes if len(n.justifications) > 1)
        expected = Action.KEEP if s.meta["preserved"] else Action.WITHDRAW
        if s.meta["relation"] == "supersedes" and not s.meta["preserved"]:
            expected = Action.RECOMPUTE
        assert s.gold[belief.id] is expected


def test_baselines_fail_in_opposite_directions():
    suite = generate_suite(20, seed=0)
    assert score(suite, oracle_jtms)["accuracy"] == 1.0
    direct, cascade = score(suite, direct_only), score(suite, naive_cascade)
    assert direct["stale_rate"] > 0.5 and direct["over_invalidation_rate"] == 0.0
    assert cascade["stale_rate"] == 0.0 and cascade["over_invalidation_rate"] > 0.0


def test_extraction_score_is_perfect_on_gold_and_drops_with_errors():
    suite = generate_suite(10, seed=0)
    perfect, noisy = ExtractionScore(), ExtractionScore()
    rng = random.Random(0)
    for s in suite:
        gold = s.justifications()
        perfect.add(gold, gold)
        noisy.add(gold, perturb_justifications(gold, rng, 0.5))
    assert all(v == 1.0 for v in perfect.summary().values())
    assert noisy.summary()["justification_set_f1"] < 0.9


def test_cli_generate_and_evaluate(tmp_path, capsys):
    out = tmp_path / "pilot.jsonl"
    main(["generate", "--n-per-family", "2", "--out", str(out)])
    main(["evaluate", str(out), "--by-family"])
    printed = capsys.readouterr().out
    assert "naive_cascade" in printed and "== F2" in printed
