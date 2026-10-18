"""Deterministic reproductions of two prior-art revision mechanisms (baselines S5, S7).

S5: PACMI-style validity lattice (Wang et al., arXiv 2610.05732).
S7: Atlas-style Ripple confidence reassessment (github.com/RichSchefren/atlas,
    ``atlas_core/ripple/{analyze_impact,reassess,adjudication}.py``).

Faithful parts reproduce the published behaviour. Adaptations needed to run them on
our graphs are marked ADAPTATION, and assumptions where the source is silent are
marked ASSUMPTION. All of them are listed in RESEARCH_SPEC.md §4.6.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import IntEnum

from beliefbench.schema import Action, Kind, Relation, Scenario


def _children(s: Scenario) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {n.id: set() for n in s.nodes}
    for nid, justs in s.justifications().items():
        for j in justs:
            for p in j:
                out[p].add(nid)
    return out


# ───────────────────────────── S5: PACMI-style lattice ──────────────────────────────


class PacmiState(IntEnum):
    # ASSUMPTION A-P2: the paper's "the stronger state in the lattice wins" uses the
    # order in which it lists the states, from weakest to strongest invalidity.
    ACTIVE = 0
    NEEDS_VERIFICATION = 1
    HISTORICAL_ONLY = 2
    SUPERSEDED = 3


SUPPORTS, USED_BY = "supports", "used-by"

# Faithful: PACMI's fixed transition map by type of the edge entering the node.
_PACMI_TRANSITION = {SUPPORTS: PacmiState.NEEDS_VERIFICATION, USED_BY: PacmiState.HISTORICAL_ONLY}


def pacmi_edge_type(s: Scenario, premise: str, conclusion: str) -> str:
    """ADAPTATION A-P1: PACMI's benchmark annotates edge types. We have none, so an edge
    into a decision is ``used-by`` (a plan that uses the memory) and any other edge is
    ``supports`` (evidential support)."""
    return USED_BY if s.node(conclusion).kind is Kind.DECISION else SUPPORTS


def pacmi_states(s: Scenario) -> dict[str, PacmiState]:
    """Direct targets of an update become SUPERSEDED. Every node reachable from them
    takes the transition of its incoming edge type; on several paths the strongest
    wins. There is no AND/OR reasoning: one invalidated premise is enough (faithful)."""
    # ADAPTATION A-P3: PACMI has no reliability, recency or hedge handling. Its LLM
    # relation classifier would label our updates update/contradict, so every update
    # makes its target SUPERSEDED.
    states = {n.id: PacmiState.ACTIVE for n in s.nodes}
    children = _children(s)
    queue = deque()
    for u in s.updates:
        states[u.target] = PacmiState.SUPERSEDED
        queue.append(u.target)
    seen = set(queue)
    while queue:
        cur = queue.popleft()
        for child in children[cur]:
            cand = _PACMI_TRANSITION[pacmi_edge_type(s, cur, child)]
            if cand > states[child]:
                states[child] = cand
            if child not in seen:
                seen.add(child)
                queue.append(child)
    return states


def pacmi_actions(s: Scenario, needs_verification_as: Action = Action.RECOMPUTE) -> dict[str, Action]:
    """Prespecified state→action mapping (A-P4). needs-verification → recompute by
    default (``uncertain`` is the alternative; SCR/OIR are identical under either)."""
    relation = {u.target: u.relation for u in s.updates}
    out = {}
    for nid, st in pacmi_states(s).items():
        if st is PacmiState.SUPERSEDED:
            out[nid] = Action.SUPERSEDE if relation.get(nid) is Relation.SUPERSEDES else Action.WITHDRAW
        elif st is PacmiState.HISTORICAL_ONLY:
            out[nid] = Action.WITHDRAW
        elif st is PacmiState.NEEDS_VERIFICATION:
            out[nid] = needs_verification_as
        else:
            out[nid] = Action.KEEP
    return out


# ──────────────────────────── S7: Atlas-style Ripple ────────────────────────────────


@dataclass(frozen=True)
class AtlasWeights:
    """Faithful: ``ReassessWeights`` defaults in reassess.py."""

    alpha: float = 0.50
    beta: float = 0.30
    gamma: float = 0.15
    delta: float = 0.05


ATLAS_STRATEGIC_FLOOR = 0.15  # Faithful: adjudication.CONFIDENCE_DELTA_STRATEGIC_FLOOR
ATLAS_MAX_DEPTH = 10  # Faithful: analyze_impact MAX_DEPTH_DEFAULT


def atlas_decay_factor(days: float | None) -> float:
    """Faithful: ``_temporal_decay_factor``."""
    return 0.5 if days is None else 0.5 ** (days / 90.0)


def atlas_heuristic_llm_delta(upstream_delta: float) -> float:
    """Faithful: ``HeuristicReassessor`` (the default, no-LLM reassessor)."""
    return max(-0.5, min(0.5, upstream_delta))


def atlas_reassess(
    current: float, upstream_delta: float, strength: float = 1.0, days: float | None = None,
    w: AtlasWeights = AtlasWeights(),
) -> float:
    """Faithful: ``reassess_dependent`` formula, clipped to [0, 1]."""
    perturbation = (
        w.beta * strength * upstream_delta
        + w.gamma * atlas_heuristic_llm_delta(upstream_delta)
        + w.delta * (atlas_decay_factor(days) - 0.5)
    )
    return max(0.0, min(1.0, current + (1.0 - w.alpha) * perturbation))


def atlas_impacted(s: Scenario, origin: str) -> list[tuple[str, int]]:
    """Faithful: ``analyze_impact``. BFS over dependents, each node visited once, depth-capped."""
    children = _children(s)
    out, seen, queue = [], {origin}, deque([(origin, 0)])
    while queue:
        cur, depth = queue.popleft()
        if depth >= ATLAS_MAX_DEPTH:
            continue
        for child in sorted(children[cur]):
            if child not in seen:
                seen.add(child)
                out.append((child, depth + 1))
                queue.append((child, depth + 1))
    return out


@dataclass(frozen=True)
class AtlasProposal:
    target: str
    origin: str
    old: float
    new: float

    @property
    def strategic(self) -> bool:
        """Faithful routing: |Δ| ≥ 0.15 → STRATEGIC_REVIEW, else AUTO_APPLY (no stakes,
        core convictions or contradictions exist in our graphs)."""
        return abs(self.new - self.old) >= ATLAS_STRATEGIC_FLOOR


# ADAPTATION A-A1: our graphs carry no confidences. Every node starts at C0 (prior
# confidence, cf. the Atlas demo's 0.80-0.88).
# ADAPTATION A-A2: an update sets its target's confidence to 0 for retracts / supersedes,
# and halves it for hedges. Atlas has no reliability or recency handling, so a
# low-reliability or outdated retraction is treated like any other.
ATLAS_C0 = 0.8


def _atlas_upstream_new(c0: float, relation: Relation) -> float:
    return c0 * 0.5 if relation is Relation.HEDGES else 0.0


def atlas_proposals(s: Scenario, c0: float = ATLAS_C0, apply: bool = False) -> list[AtlasProposal]:
    """One Ripple cascade per update, in update order.

    Faithful: every impacted node is reassessed against the *origin's* confidence change,
    with strength 1.0 (the default when the DEPENDS_ON edge has no strength, and the
    coalesce fallback for non-direct dependents). Atlas has no automatic proposal
    consumer, so by default (``apply=False``) confidences are not written back between
    cascades. ``apply=True`` simulates every proposal being accepted.
    """
    conf = {n.id: c0 for n in s.nodes}
    proposals = []
    for u in s.updates:
        old_up = conf[u.target]
        new_up = _atlas_upstream_new(old_up, u.relation)
        conf[u.target] = new_up  # the revision itself goes through AGM revise()
        for nid, _depth in atlas_impacted(s, u.target):
            new = atlas_reassess(conf[nid], new_up - old_up)
            proposals.append(AtlasProposal(nid, u.target, conf[nid], new))
            if apply:
                conf[nid] = new
    return proposals


def _flag_action(relation: Relation) -> Action:
    """A-A3: an Atlas flag is given the gold action class of its cause (the most
    charitable reading, which only affects macro-F1, not SCR/OIR)."""
    return {Relation.RETRACTS: Action.WITHDRAW, Relation.SUPERSEDES: Action.RECOMPUTE}.get(
        relation, Action.UNCERTAIN
    )


def _target_actions(s: Scenario) -> dict[str, Action]:
    lit = {Relation.RETRACTS: Action.WITHDRAW, Relation.SUPERSEDES: Action.SUPERSEDE, Relation.HEDGES: Action.UNCERTAIN}
    return {u.target: lit[u.relation] for u in s.updates}


def atlas_actions_native(s: Scenario, c0: float = ATLAS_C0) -> dict[str, Action]:
    """Prespecified discrete mapping using Atlas's own threshold: a node is revised iff
    some proposal for it was routed to strategic review."""
    relation = {u.target: u.relation for u in s.updates}
    out = {n.id: Action.KEEP for n in s.nodes}
    for p in atlas_proposals(s, c0):
        if p.strategic and out[p.target] is Action.KEEP:
            out[p.target] = _flag_action(relation[p.origin])
    out.update(_target_actions(s))
    return out


def atlas_actions_threshold(s: Scenario, tau: float, c0: float = ATLAS_C0) -> dict[str, Action]:
    """Threshold-sweep mapping: apply all proposals; a node is revised iff its final
    confidence < ``tau``."""
    relation = {u.target: u.relation for u in s.updates}
    final = {n.id: c0 for n in s.nodes}
    cause: dict[str, Relation] = {}
    for p in atlas_proposals(s, c0, apply=True):
        final[p.target] = p.new
        cause.setdefault(p.target, relation[p.origin])
    out = {nid: (_flag_action(cause[nid]) if nid in cause and c < tau else Action.KEEP) for nid, c in final.items()}
    out.update(_target_actions(s))
    return out
