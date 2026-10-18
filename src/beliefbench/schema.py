"""Scenario data model.

A scenario is a belief base before an update: evidence nodes (foundational) and
derived nodes (beliefs / decisions), each derived node carrying its justifications
in OR-of-ANDs form. ``[[E1], [E4]]`` means "E1 alone, or E4 alone";
``[[B1, E2]]`` means "B1 and E2 together".

Updates always target an evidence node (base revision, in Hansson's sense).
Derived nodes change only through propagation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

Justifications = list[list[str]]


class Kind(str, Enum):
    EVIDENCE = "evidence"
    BELIEF = "belief"
    DECISION = "decision"


class Relation(str, Enum):
    RETRACTS = "retracts"  # target is no longer true; nothing replaces it
    SUPERSEDES = "supersedes"  # target's value changed; dependents must be re-derived
    HEDGES = "hedges"  # update casts doubt on target without settling it


class Action(str, Enum):
    KEEP = "keep"
    WITHDRAW = "withdraw"
    RECOMPUTE = "recompute"
    UNCERTAIN = "uncertain"
    SUPERSEDE = "supersede"


RELIABILITY = {"low": 0, "medium": 1, "high": 2}


@dataclass
class Node:
    id: str
    kind: Kind
    text: str = ""
    t: int = 0  # valid time: when the fact was observed to hold
    source: str = ""
    reliability: str = "high"
    justifications: Justifications = field(default_factory=list)

    @property
    def is_evidence(self) -> bool:
        return self.kind is Kind.EVIDENCE


@dataclass
class Update:
    id: str
    t: int
    target: str
    relation: Relation
    source: str = ""
    reliability: str = "high"
    text: str = ""


@dataclass
class Scenario:
    id: str
    family: str
    domain: str
    nodes: list[Node]
    updates: list[Update]
    gold: dict[str, Action] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)

    def node(self, node_id: str) -> Node:
        for n in self.nodes:
            if n.id == node_id:
                return n
        raise KeyError(node_id)

    def justifications(self) -> dict[str, Justifications]:
        return {n.id: n.justifications for n in self.nodes if not n.is_evidence}

    def validate(self) -> None:
        """Raise ValueError if the scenario is malformed."""
        ids = [n.id for n in self.nodes]
        if len(ids) != len(set(ids)):
            raise ValueError(f"{self.id}: duplicate node ids")
        known = set(ids)
        for n in self.nodes:
            if n.reliability not in RELIABILITY:
                raise ValueError(f"{self.id}/{n.id}: unknown reliability {n.reliability!r}")
            if n.is_evidence:
                if n.justifications:
                    raise ValueError(f"{self.id}/{n.id}: evidence cannot have justifications")
                continue
            if not n.justifications or any(not j for j in n.justifications):
                raise ValueError(f"{self.id}/{n.id}: derived node needs non-empty justifications")
            for j in n.justifications:
                missing = set(j) - known
                if missing:
                    raise ValueError(f"{self.id}/{n.id}: unknown premises {sorted(missing)}")
        for u in self.updates:
            if u.id in known:
                raise ValueError(f"{self.id}: update id {u.id} collides with a node id")
            if u.target not in known or not self.node(u.target).is_evidence:
                raise ValueError(f"{self.id}/{u.id}: update must target an evidence node")
        # Raises on cycles.
        from beliefbench.labeler import topo_order

        topo_order(ids, self.justifications())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Scenario:
        return cls(
            id=d["id"],
            family=d["family"],
            domain=d["domain"],
            nodes=[Node(**{**n, "kind": Kind(n["kind"])}) for n in d["nodes"]],
            updates=[Update(**{**u, "relation": Relation(u["relation"])}) for u in d["updates"]],
            gold={k: Action(v) for k, v in d.get("gold", {}).items()},
            meta=d.get("meta", {}),
        )
