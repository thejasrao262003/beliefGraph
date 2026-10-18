import random

import pytest

from beliefbench.diffcheck import (
    disagreements,
    features,
    in_shared_subset,
    minimize,
    random_retraction_scenario,
)
from beliefbench.generate import generate_suite
from beliefbench.schema import Action

pytest.importorskip("veritas.store")


def test_pilot_shared_subset_agrees_with_veritas():
    suite = [s for s in generate_suite(10, seed=0) if in_shared_subset(s)]
    assert suite, "pilot should contain retraction-only scenarios"
    for s in suite:
        assert set(s.gold.values()) <= {Action.KEEP, Action.WITHDRAW}
        assert disagreements(s) == {}, s.id


def test_fuzzed_dags_agree_with_veritas():
    covered = set()
    for i in range(300):
        s = random_retraction_scenario(random.Random(i), f"fuzz-{i}")
        covered |= features(s)
        assert disagreements(s) == {}, s.id
    assert {"diamond", "multi_support", "conjunctive", "multi_retraction", "partial_support_loss",
            "all_supports_lost", "unaffected_part"} <= covered


def test_minimizer_shrinks_a_planted_disagreement():
    # Plant a fake disagreement: "other system" withdraws every derived node.
    from beliefbench.labeler import gold_actions

    def wrong(s):
        return {n.id: Action.WITHDRAW if not n.is_evidence or n.id in {u.target for u in s.updates} else Action.KEEP
                for n in s.nodes}

    def fails(s):
        return disagreements(s, wrong) != {}

    s = next(sc for i in range(100) if fails(sc := random_retraction_scenario(random.Random(i), "m")))
    small = minimize(s, fails)
    assert fails(small) and len(small.nodes) <= 3
    assert gold_actions(small)  # still a valid scenario
