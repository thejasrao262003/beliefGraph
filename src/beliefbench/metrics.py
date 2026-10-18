"""Scoring. Revision quality and justification-extraction quality are kept separate.

- ``RevisionScore`` compares predicted per-node actions to gold actions (end to end).
- ``ExtractionScore`` compares predicted justification structure to gold, with no
  reference to revision.

For a system that exposes its justifications, the actions those justifications
*imply* (``labeler.gold_actions(s, predicted)``) can also be scored. That splits the
end-to-end error into an extraction part and a revision-logic part.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, field
from itertools import combinations

from beliefbench.schema import Action, Justifications

# Leaving any of these as ``keep`` means acting on a belief that should have changed.
_REVISING = {Action.WITHDRAW, Action.RECOMPUTE, Action.SUPERSEDE, Action.UNCERTAIN}


def _f1(tp: int, fp: int, fn: int) -> float:
    if tp == 0:
        return 1.0 if fp == fn == 0 else 0.0
    return 2 * tp / (2 * tp + fp + fn)


def _ratio(num: int, den: int) -> float | None:
    return num / den if den else None


@dataclass
class RevisionScore:
    confusion: Counter = field(default_factory=Counter)  # (gold, pred) -> count

    def add(self, gold: Mapping[str, Action], pred: Mapping[str, Action]) -> None:
        for nid, g in gold.items():
            self.confusion[(g, pred.get(nid, Action.KEEP))] += 1

    def _count(self, gold=None, pred=None, gold_in=None, pred_not=None) -> int:
        return sum(
            c
            for (g, p), c in self.confusion.items()
            if (gold is None or g is gold)
            and (pred is None or p is pred)
            and (gold_in is None or g in gold_in)
            and (pred_not is None or p is not pred_not)
        )

    def summary(self) -> dict[str, float | None]:
        total = sum(self.confusion.values())
        correct = sum(c for (g, p), c in self.confusion.items() if g is p)
        f1s = []
        for a in Action:
            support = self._count(gold=a)
            if support:
                tp = self._count(gold=a, pred=a)
                f1s.append(_f1(tp, self._count(pred=a) - tp, support - tp))
        unc_tp = self._count(gold=Action.UNCERTAIN, pred=Action.UNCERTAIN)
        return {
            "n": total,
            "accuracy": _ratio(correct, total),
            "macro_f1": sum(f1s) / len(f1s) if f1s else None,
            # Nodes that should have been revised but were left as keep.
            "stale_rate": _ratio(self._count(gold_in=_REVISING, pred=Action.KEEP), self._count(gold_in=_REVISING)),
            # Nodes that should have been kept but were touched.
            "over_invalidation_rate": _ratio(
                self._count(gold=Action.KEEP, pred_not=Action.KEEP), self._count(gold=Action.KEEP)
            ),
            "uncertain_precision": _ratio(unc_tp, self._count(pred=Action.UNCERTAIN)),
            "uncertain_recall": _ratio(unc_tp, self._count(gold=Action.UNCERTAIN)),
        }


def _edges(justs: Mapping[str, Justifications]) -> set[tuple[str, str]]:
    return {(p, n) for n, js in justs.items() for j in js for p in j}


def _sets(justs: Mapping[str, Justifications]) -> set[tuple[str, frozenset[str]]]:
    return {(n, frozenset(j)) for n, js in justs.items() for j in js if j}


@dataclass
class ExtractionScore:
    edge: Counter = field(default_factory=Counter)  # tp / fp / fn over (premise, conclusion)
    jset: Counter = field(default_factory=Counter)  # tp / fp / fn over whole AND-sets
    node_exact: int = 0
    nodes: int = 0
    pair_correct: int = 0  # premise pairs whose AND-vs-OR relation was recovered
    pairs: int = 0  # gold premise pairs where both premises were extracted

    def add(
        self,
        gold: Mapping[str, Justifications],
        pred: Mapping[str, Justifications],
        only: set[str] | None = None,
    ) -> None:
        """``only`` restricts scoring to those conclusion nodes (e.g. the update's affected region)."""
        if only is not None:
            gold = {n: js for n, js in gold.items() if n in only}
            pred = {n: js for n, js in pred.items() if n in only}
        for counter, g, p in (
            (self.edge, _edges(gold), _edges(pred)),
            (self.jset, _sets(gold), _sets(pred)),
        ):
            counter["tp"] += len(g & p)
            counter["fp"] += len(p - g)
            counter["fn"] += len(g - p)
        for nid, gjs in gold.items():
            pjs = pred.get(nid, [])
            self.nodes += 1
            gset = {frozenset(j) for j in gjs}
            pset = {frozenset(j) for j in pjs if j}
            self.node_exact += gset == pset
            pred_premises = {p for j in pset for p in j}
            for a, b in combinations(sorted({p for j in gset for p in j}), 2):
                if a not in pred_premises or b not in pred_premises:
                    continue
                self.pairs += 1
                gold_and = any(a in j and b in j for j in gset)
                pred_and = any(a in j and b in j for j in pset)
                self.pair_correct += gold_and == pred_and

    def summary(self) -> dict[str, float | None]:
        return {
            "edge_f1": _f1(self.edge["tp"], self.edge["fp"], self.edge["fn"]),
            "justification_set_f1": _f1(self.jset["tp"], self.jset["fp"], self.jset["fn"]),
            "node_exact_match": _ratio(self.node_exact, self.nodes),
            "and_or_typing_accuracy": _ratio(self.pair_correct, self.pairs),
        }
