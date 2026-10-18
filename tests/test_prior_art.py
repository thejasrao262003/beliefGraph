"""Conformance tests: keep S5 / S7 pinned to the published behaviour."""

import pytest

from beliefbench.prior_art import (
    ATLAS_STRATEGIC_FLOOR,
    AtlasProposal,
    AtlasWeights,
    PacmiState,
    atlas_actions_native,
    atlas_decay_factor,
    atlas_heuristic_llm_delta,
    atlas_impacted,
    atlas_proposals,
    atlas_reassess,
    pacmi_actions,
    pacmi_states,
)
from beliefbench.schema import Action, Kind, Node, Relation, Scenario, Update


def ev(nid, t=1):
    return Node(nid, Kind.EVIDENCE, t=t)


def der(nid, *justs, decision=False):
    return Node(nid, Kind.DECISION if decision else Kind.BELIEF, justifications=[list(j) for j in justs])


def scenario(nodes, *updates):
    s = Scenario("t", "test", "test", nodes, list(updates))
    s.validate()
    return s


# ── PACMI ──


def test_pacmi_canonical_two_hop_chain():
    # PACMI's benchmark topology: M1 -supports-> M2 -used-by-> M3, M1 updated.
    s = scenario([ev("M1"), der("M2", ["M1"]), der("M3", ["M2"], decision=True)],
                 Update("U1", 5, "M1", Relation.SUPERSEDES))
    assert pacmi_states(s) == {
        "M1": PacmiState.SUPERSEDED, "M2": PacmiState.NEEDS_VERIFICATION, "M3": PacmiState.HISTORICAL_ONLY,
    }


def test_pacmi_unreached_nodes_stay_active():
    s = scenario([ev("E1"), ev("E2"), der("B1", ["E1"]), der("B2", ["E2"])], Update("U1", 5, "E1", Relation.RETRACTS))
    assert pacmi_states(s)["B2"] is PacmiState.ACTIVE


def test_pacmi_stronger_state_wins_on_multiple_paths():
    # D1 reached via supports-path (needs-verification) and used-by edge (historical-only).
    s = scenario([ev("E1"), der("B1", ["E1"]), der("D1", ["B1", "E1"], decision=True)],
                 Update("U1", 5, "E1", Relation.RETRACTS))
    assert pacmi_states(s)["D1"] is PacmiState.HISTORICAL_ONLY


def test_pacmi_has_no_alternative_support_reasoning():
    # Faithful: B1 still has E2, but PACMI flags it anyway.
    s = scenario([ev("E1"), ev("E2"), der("B1", ["E1"], ["E2"])], Update("U1", 5, "E1", Relation.RETRACTS))
    assert pacmi_states(s)["B1"] is PacmiState.NEEDS_VERIFICATION
    assert pacmi_actions(s)["B1"] is Action.RECOMPUTE
    assert pacmi_actions(s, needs_verification_as=Action.UNCERTAIN)["B1"] is Action.UNCERTAIN


# ── Atlas: values pinned to atlas tests/unit/test_reassess.py ──


def test_atlas_default_weights_match_spec():
    w = AtlasWeights()
    assert (w.alpha, w.beta, w.gamma, w.delta) == (0.50, 0.30, 0.15, 0.05)
    assert ATLAS_STRATEGIC_FLOOR == 0.15


def test_atlas_decay_factor():
    assert atlas_decay_factor(0) == pytest.approx(1.0)
    assert atlas_decay_factor(90) == pytest.approx(0.5)
    assert atlas_decay_factor(180) == pytest.approx(0.25)
    assert atlas_decay_factor(None) == 0.5


def test_atlas_heuristic_reassessor_bounds():
    assert atlas_heuristic_llm_delta(0.3) == pytest.approx(0.3)
    assert atlas_heuristic_llm_delta(1.0) == 0.5
    assert atlas_heuristic_llm_delta(-1.0) == -0.5


def test_atlas_formula():
    # Hand-computed from reassess.py: 0.7 + 0.5*(0.3*1*(-0.5) + 0.15*(-0.5) + 0.05*0)
    assert atlas_reassess(0.7, 0.4 - 0.9) == pytest.approx(0.7 + 0.5 * (-0.15 - 0.075))
    assert atlas_reassess(0.5, 0.95 - 0.4) > 0.5  # upstream rise raises dependent
    assert atlas_reassess(0.99, 1.0) <= 1.0 and atlas_reassess(0.05, -1.0) >= 0.0
    assert atlas_reassess(0.7, -0.6, strength=1.0) < atlas_reassess(0.7, -0.6, strength=0.3)
    assert atlas_reassess(0.6, 0.0) == pytest.approx(0.6)  # no-perturbation invariant


def test_atlas_bfs_order_and_uniform_origin_delta():
    s = scenario([ev("A"), der("B", ["A"]), der("C", ["B"])], Update("U1", 5, "A", Relation.RETRACTS))
    assert atlas_impacted(s, "A") == [("B", 1), ("C", 2)]
    props = atlas_proposals(s, c0=0.8)
    assert [p.target for p in props] == ["B", "C"]
    # Every dependent is reassessed against the origin's delta, regardless of depth.
    assert props[0].new == pytest.approx(props[1].new)


def test_atlas_routing_and_no_alternative_support():
    s = scenario([ev("E1"), ev("E2"), der("B1", ["E1"], ["E2"])], Update("U1", 5, "E1", Relation.RETRACTS))
    (p,) = atlas_proposals(s, c0=0.8)
    assert p.strategic  # |Δ| = 0.1575 >= 0.15
    assert atlas_actions_native(s)["B1"] is Action.WITHDRAW
    assert not AtlasProposal("x", "y", 0.8, 0.70).strategic


def test_atlas_hedge_falls_below_strategic_floor():
    s = scenario([ev("E1"), der("B1", ["E1"])], Update("U1", 5, "E1", Relation.HEDGES))
    assert atlas_actions_native(s)["B1"] is Action.KEEP
