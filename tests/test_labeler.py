import pytest

from beliefbench.labeler import Status, gold_actions, propagate
from beliefbench.schema import Action, Kind, Node, Relation, Scenario, Update

A = Action


def ev(nid, t=1, reliability="high"):
    return Node(nid, Kind.EVIDENCE, t=t, reliability=reliability)


def der(nid, *justs, decision=False):
    return Node(nid, Kind.DECISION if decision else Kind.BELIEF, justifications=[list(j) for j in justs])


def scenario(nodes, *updates):
    s = Scenario("t", "test", "test", nodes, list(updates))
    s.validate()
    return s


def test_spec_example_independent_support_preserved():
    # RESEARCH_SPEC.md 4.1: E1 retracted, but B1 still rests on E4.
    s = scenario(
        [ev("E1", 1), ev("E2", 2), ev("E4", 3), der("B1", ["E1"], ["E4"]), der("B2", ["B1", "E2"]),
         der("D1", ["B2"], decision=True)],
        Update("U1", 4, "E1", Relation.RETRACTS),
    )
    assert gold_actions(s) == {"E1": A.WITHDRAW, "E2": A.KEEP, "E4": A.KEEP, "B1": A.KEEP, "B2": A.KEEP, "D1": A.KEEP}


def test_losing_an_and_premise_withdraws_the_chain():
    s = scenario([ev("E1"), ev("E2"), der("B1", ["E1", "E2"]), der("D1", ["B1"])],
                 Update("U1", 5, "E1", Relation.RETRACTS))
    assert gold_actions(s) == {"E1": A.WITHDRAW, "E2": A.KEEP, "B1": A.WITHDRAW, "D1": A.WITHDRAW}


def test_superseded_premise_means_recompute_downstream():
    s = scenario([ev("E1"), ev("E2"), der("B1", ["E1", "E2"]), der("D1", ["B1"])],
                 Update("U1", 5, "E1", Relation.SUPERSEDES))
    assert gold_actions(s) == {"E1": A.SUPERSEDE, "E2": A.KEEP, "B1": A.RECOMPUTE, "D1": A.RECOMPUTE}


def test_out_dominates_stale_inside_an_and():
    s = scenario([ev("E1"), ev("E2"), der("B1", ["E1", "E2"])],
                 Update("U1", 5, "E1", Relation.SUPERSEDES), Update("U2", 6, "E2", Relation.RETRACTS))
    assert gold_actions(s)["B1"] is A.WITHDRAW


def test_or_prefers_recompute_over_uncertain():
    s = scenario([ev("E1"), ev("E2"), der("B1", ["E1"], ["E2"])],
                 Update("U1", 5, "E1", Relation.SUPERSEDES), Update("U2", 6, "E2", Relation.HEDGES))
    assert propagate(s)["B1"] is Status.STALE


@pytest.mark.parametrize("update", [
    Update("U1", 5, "E1", Relation.HEDGES),
    Update("U1", 5, "E1", Relation.RETRACTS, reliability="low"),
])
def test_doubtful_updates_give_uncertain(update):
    s = scenario([ev("E1"), der("B1", ["E1"])], update)
    assert gold_actions(s) == {"E1": A.UNCERTAIN, "B1": A.UNCERTAIN}


def test_outdated_update_is_ignored():
    s = scenario([ev("E1", t=5), der("B1", ["E1"])], Update("U1", 3, "E1", Relation.RETRACTS))
    assert gold_actions(s) == {"E1": A.KEEP, "B1": A.KEEP}


def test_predicted_justifications_change_implied_actions():
    s = scenario([ev("E1"), ev("E2"), der("B1", ["E1"], ["E2"])], Update("U1", 5, "E1", Relation.RETRACTS))
    assert gold_actions(s)["B1"] is A.KEEP
    # Misreading the alternatives as a conjunction over-invalidates.
    assert gold_actions(s, {"B1": [["E1", "E2"]]})["B1"] is A.WITHDRAW
    # Extracting no justification at all leaves the node untouched.
    assert gold_actions(s, {"B1": []})["B1"] is A.KEEP


def test_cycles_are_rejected():
    with pytest.raises(ValueError, match="cycle"):
        scenario([ev("E1"), der("B1", ["E1", "B2"]), der("B2", ["B1"])])


def test_updates_must_target_evidence():
    with pytest.raises(ValueError, match="evidence"):
        scenario([ev("E1"), der("B1", ["E1"])], Update("U1", 5, "B1", Relation.RETRACTS))
