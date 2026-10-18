"""Deterministic (no-LLM) reference systems.

These set the floor and ceiling the LLM systems are compared against, and let the
benchmark be checked before any model calls are paid for.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Mapping

from beliefbench.labeler import descendants, gold_actions
from beliefbench.schema import Action, Justifications, Relation, Scenario

_LITERAL = {
    Relation.RETRACTS: Action.WITHDRAW,
    Relation.SUPERSEDES: Action.SUPERSEDE,
    Relation.HEDGES: Action.UNCERTAIN,
}


def _literal_targets(s: Scenario) -> dict[str, Action]:
    """Apply each update to its target at face value: no recency or reliability check."""
    return {u.target: _LITERAL[u.relation] for u in s.updates}


def direct_only(s: Scenario) -> dict[str, Action]:
    """Revise only the evidence an update names; never propagate. Floor for staleness."""
    actions = {n.id: Action.KEEP for n in s.nodes}
    actions.update(_literal_targets(s))
    return actions


def naive_cascade(s: Scenario) -> dict[str, Action]:
    """Withdraw every descendant of every updated node, ignoring alternative support."""
    actions = direct_only(s)
    for nid in descendants(s, _literal_targets(s)):
        actions[nid] = Action.WITHDRAW
    return actions


def oracle_jtms(s: Scenario) -> dict[str, Action]:
    """Gold justifications plus correct propagation. Equals gold by construction (sanity check)."""
    return gold_actions(s)


BASELINES: dict[str, Callable[[Scenario], dict[str, Action]]] = {
    "direct_only": direct_only,
    "naive_cascade": naive_cascade,
    "oracle_jtms": oracle_jtms,
}


def perturb_justifications(
    justs: Mapping[str, Justifications], rng: random.Random, rate: float
) -> dict[str, Justifications]:
    """Simulate justification-extraction errors. With probability ``rate``, each derived
    node gets one error:

    - drop_premise: miss one premise of an AND-set
    - and_to_or: read an AND-set as alternatives
    - drop_alternative: miss one OR alternative
    - or_to_and: read alternatives as jointly required
    - unlink: extract no justification (the node is then treated as self-standing)
    """
    out: dict[str, Justifications] = {}
    for nid in sorted(justs):
        js = [list(j) for j in justs[nid]]
        if rng.random() < rate:
            ops = ["unlink"]
            if any(len(j) > 1 for j in js):
                ops += ["drop_premise", "and_to_or"]
            if len(js) > 1:
                ops += ["drop_alternative", "or_to_and"]
            op = rng.choice(ops)
            if op == "unlink":
                js = []
            elif op in ("drop_premise", "and_to_or"):
                i = rng.choice([i for i, j in enumerate(js) if len(j) > 1])
                if op == "drop_premise":
                    js[i].pop(rng.randrange(len(js[i])))
                else:
                    js[i : i + 1] = [[p] for p in js[i]]
            elif op == "drop_alternative":
                js.pop(rng.randrange(len(js)))
            else:
                js = [sorted({p for j in js for p in j})]
        out[nid] = js
    return out
