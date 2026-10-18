"""Deterministic gold labeller: three-valued, JTMS-style label propagation.

Every node gets a status from a total order

    OUT < UNK < STALE < IN

- An AND-justification takes the *minimum* status of its premises.
- A derived node takes the *maximum* status over its justifications.

So a node stays IN as long as one justification is fully IN (independent support
is preserved). It is STALE (must be re-derived) when its best support rests on a
premise whose value changed. It is UNK when its best support rests on doubtful
evidence. It is OUT when every justification has lost a premise outright.

The same propagation runs on *predicted* justifications. That lets extraction
quality be scored separately from revision quality (see metrics.py).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from enum import IntEnum

from beliefbench.schema import RELIABILITY, Action, Justifications, Relation, Scenario, Update


class Status(IntEnum):
    OUT = 0
    UNK = 1
    STALE = 2
    IN = 3


_STATUS_TO_ACTION = {
    Status.IN: Action.KEEP,
    Status.STALE: Action.RECOMPUTE,
    Status.UNK: Action.UNCERTAIN,
    Status.OUT: Action.WITHDRAW,
}

_TARGET_ACTION = {
    Status.OUT: Action.WITHDRAW,
    Status.STALE: Action.SUPERSEDE,
    Status.UNK: Action.UNCERTAIN,
}


def topo_order(node_ids: Iterable[str], justifications: Mapping[str, Justifications]) -> list[str]:
    """Order nodes so that premises come before conclusions. Raise ValueError on a cycle."""
    ids = list(node_ids)
    known = set(ids)
    parents = {
        n: {p for j in justifications.get(n, []) for p in j if p in known and p != n} for n in ids
    }
    children: dict[str, list[str]] = {n: [] for n in ids}
    for n, ps in parents.items():
        for p in ps:
            children[p].append(n)
    indeg = {n: len(ps) for n, ps in parents.items()}
    ready = [n for n in ids if indeg[n] == 0]
    order: list[str] = []
    while ready:
        n = ready.pop(0)
        order.append(n)
        for c in children[n]:
            indeg[c] -= 1
            if indeg[c] == 0:
                ready.append(c)
    if len(order) != len(ids):
        raise ValueError(f"dependency cycle among {sorted(set(ids) - set(order))}")
    return order


def update_effect(update: Update, target_t: int, target_reliability: str) -> Status | None:
    """Status an update imposes on its target evidence, or None if the update is ignored.

    - Older than the evidence it targets (valid time): outdated, no effect.
    - Hedged, or less reliable than the target: doubt, not refutation -> UNK.
    - Otherwise: RETRACTS -> OUT, SUPERSEDES -> STALE.
    """
    if update.t < target_t:
        return None
    if update.relation is Relation.HEDGES or RELIABILITY[update.reliability] < RELIABILITY[target_reliability]:
        return Status.UNK
    return Status.OUT if update.relation is Relation.RETRACTS else Status.STALE


def evidence_effects(scenario: Scenario) -> dict[str, Status]:
    """Effective status per targeted evidence node. Several updates combine by minimum."""
    effects: dict[str, Status] = {}
    for u in scenario.updates:
        target = scenario.node(u.target)
        eff = update_effect(u, target.t, target.reliability)
        if eff is not None:
            effects[u.target] = min(eff, effects.get(u.target, Status.IN))
    return effects


def propagate(
    scenario: Scenario, justifications: Mapping[str, Justifications] | None = None
) -> dict[str, Status]:
    """Post-update status of every node.

    ``justifications`` defaults to the scenario's gold ones. When predicted ones are
    passed, a derived node with no predicted justification is treated as
    self-standing (IN). Premises that refer to unknown ids are ignored.
    """
    justs = scenario.justifications() if justifications is None else justifications
    effects = evidence_effects(scenario)
    ids = [n.id for n in scenario.nodes]
    known = set(ids)
    status: dict[str, Status] = {}
    for nid in topo_order(ids, justs):
        node = scenario.node(nid)
        if node.is_evidence:
            status[nid] = effects.get(nid, Status.IN)
            continue
        sets = [[p for p in j if p in known and p != nid] for j in justs.get(nid, [])]
        sets = [j for j in sets if j]
        status[nid] = max((min(status[p] for p in j) for j in sets), default=Status.IN)
    return status


def gold_actions(
    scenario: Scenario, justifications: Mapping[str, Justifications] | None = None
) -> dict[str, Action]:
    """Revision action per pre-existing node. With predicted justifications, these are
    the actions those justifications *imply* under correct propagation."""
    status = propagate(scenario, justifications)
    effects = evidence_effects(scenario)
    return {
        nid: _TARGET_ACTION[effects[nid]] if nid in effects else _STATUS_TO_ACTION[st]
        for nid, st in status.items()
    }


def descendants(scenario: Scenario, roots: Iterable[str]) -> set[str]:
    """All nodes reachable from ``roots`` along any justification edge."""
    children: dict[str, set[str]] = {}
    for nid, justs in scenario.justifications().items():
        for j in justs:
            for p in j:
                children.setdefault(p, set()).add(nid)
    seen: set[str] = set()
    stack = list(roots)
    while stack:
        for c in children.get(stack.pop(), ()):
            if c not in seen:
                seen.add(c)
                stack.append(c)
    return seen
