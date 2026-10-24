"""Seeded scenario generator for the pilot families (F1, F2, F3, F6).

The graph is sampled first and gold labels come from the deterministic labeller.
Natural-language rendering is a separate, later step: node ``text`` is left empty
here, so this module never calls a model.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence

from beliefbench.labeler import gold_actions
from beliefbench.schema import Justifications, Kind, Node, Relation, Scenario, Update

PILOT_DOMAINS = ("product_eligibility", "travel_logistics")
# Long scenarios (F7) span more of what an assistant remembers.
LONG_DOMAINS = ("personal_assistant", "healthcare_compliance", "hr_onboarding", "vendor_procurement",
                "travel_logistics", "finance_kyc")


class _Builder:
    def __init__(self, rng: random.Random):
        self.rng = rng
        self.nodes: list[Node] = []
        self.updates: list[Update] = []
        self._counts = {"E": 0, "B": 0, "D": 0, "U": 0}
        self._t = 0

    def _next_id(self, prefix: str) -> str:
        self._counts[prefix] += 1
        return f"{prefix}{self._counts[prefix]}"

    def evidence(self, reliability: str = "high") -> str:
        self._t += 1
        nid = self._next_id("E")
        self.nodes.append(
            Node(nid, Kind.EVIDENCE, t=self._t, source=f"source_{nid.lower()}", reliability=reliability)
        )
        return nid

    def derived(self, justifications: Justifications, decision: bool = False) -> str:
        nid = self._next_id("D" if decision else "B")
        kind = Kind.DECISION if decision else Kind.BELIEF
        self.nodes.append(Node(nid, kind, justifications=[list(j) for j in justifications]))
        return nid

    def chain(self, root: str, depth: int, co_premise_p: float = 0.5) -> str:
        """``depth`` derived nodes below ``root``, each with one justification. Each step
        may AND in an unaffected co-premise. The last node is a decision."""
        prev = root
        for i in range(depth):
            just = [prev]
            if self.rng.random() < co_premise_p:
                just.append(self.evidence())
            prev = self.derived([just], decision=i == depth - 1)
        return prev

    def distractors(self, k: int) -> None:
        for _ in range(k):
            self.derived([[self.evidence()]])

    def update(self, target: str, relation: Relation, reliability: str = "high", outdated: bool = False) -> None:
        target_t = next(n.t for n in self.nodes if n.id == target)
        t = target_t - 1 if outdated else self._t + 1 + len(self.updates)
        self.updates.append(Update(self._next_id("U"), t, target, relation, reliability=reliability))

    def build(self, sid: str, family: str, domain: str, meta: dict) -> Scenario:
        s = Scenario(sid, family, domain, self.nodes, self.updates, meta=meta)
        s.validate()
        s.gold = gold_actions(s)
        return s


def _revising_relation(rng: random.Random) -> Relation:
    return rng.choice([Relation.RETRACTS, Relation.SUPERSEDES])


def f1_chain(rng: random.Random) -> tuple[_Builder, dict]:
    """Single-support chain of depth 1-5; the root evidence is revised."""
    b = _Builder(rng)
    root = b.evidence()
    depth = rng.randint(1, 5)
    b.chain(root, depth)
    rel = _revising_relation(rng)
    b.update(root, rel)
    b.distractors(rng.randint(1, 3))
    return b, {"depth": depth, "relation": rel.value}


def f2_independent_support(rng: random.Random) -> tuple[_Builder, dict]:
    """A belief with 2-4 alternative supports; 1..k of them are revised.
    Retracting fewer than all must preserve the belief and everything below it."""
    b = _Builder(rng)
    k = rng.randint(2, 4)
    supports = [b.evidence() for _ in range(k)]
    belief = b.derived([[s] for s in supports])
    depth = rng.randint(1, 3)
    b.chain(belief, depth)
    m = k if rng.random() < 0.25 else rng.randint(1, k - 1)
    rel = _revising_relation(rng)
    for target in rng.sample(supports, m):
        b.update(target, rel)
    b.distractors(rng.randint(1, 3))
    return b, {"fan_in": k, "revised_supports": m, "preserved": m < k, "depth": depth, "relation": rel.value}


def f3_conjunctive(rng: random.Random) -> tuple[_Builder, dict]:
    """A belief resting on an AND of 2-4 premises; one premise is revised.
    Half the time the belief also has an independent alternative support."""
    b = _Builder(rng)
    k = rng.randint(2, 4)
    premises = [b.evidence() for _ in range(k)]
    justs: Justifications = [premises]
    has_alt = rng.random() < 0.5
    if has_alt:
        justs.append([b.evidence()])
    belief = b.derived(justs)
    depth = rng.randint(1, 2)
    b.chain(belief, depth)
    rel = _revising_relation(rng)
    b.update(rng.choice(premises), rel)
    b.distractors(rng.randint(1, 3))
    return b, {"conj_size": k, "has_alternative": has_alt, "depth": depth, "relation": rel.value}


def f6_ambiguous(rng: random.Random) -> tuple[_Builder, dict]:
    """The update is hedged, or comes from a less reliable source than the evidence
    it contradicts: gold is ``uncertain``, unless an alternative support holds."""
    b = _Builder(rng)
    root = b.evidence()
    has_alt = rng.random() < 0.4
    justs: Justifications = [[root], [b.evidence()]] if has_alt else [[root]]
    belief = b.derived(justs)
    depth = rng.randint(1, 2)
    b.chain(belief, depth)
    variant = rng.choice(["hedge", "low_reliability"])
    if variant == "hedge":
        b.update(root, Relation.HEDGES)
    else:
        b.update(root, Relation.RETRACTS, reliability="low")
    b.distractors(rng.randint(1, 3))
    return b, {"variant": variant, "has_alternative": has_alt, "depth": depth}


def f7_dossier(rng: random.Random, motifs: tuple[int, int] = (4, 7), updates: tuple[int, int] = (4, 8)) -> tuple[_Builder, dict]:
    """A long case: 4-7 motifs (chain, alternative supports, conjunction, weak-source chain)
    composed into one dependency DAG about the same few entities, with shared facts (one fact
    feeding several conclusions), cross-motif links (a conclusion building on an earlier one)
    and decisions on top; then 4-8 updates over time mixing retractions, new values, hedges,
    weak-source denials, repeated hits on one fact and updates nothing depends on. Gold after
    each update comes from the same labeller (several updates on a fact combine by minimum)."""
    b = _Builder(rng)
    pool: list[str] = []  # evidence that later motifs may share
    tops: list[str] = []
    shapes = []

    def ev(share_p: float = 0.3) -> str:
        if pool and rng.random() < share_p:
            return rng.choice(pool)
        e = b.evidence(reliability=rng.choice(["high", "high", "medium"]))
        pool.append(e)
        return e

    for _ in range(rng.randint(*motifs)):
        shape = rng.choice(["chain", "alternatives", "conjunction", "conjunction_alt"])
        shapes.append(shape)
        if shape == "chain":
            justs: Justifications = [[ev()]]
        elif shape == "alternatives":
            justs = [[x] for x in dict.fromkeys(ev() for _ in range(rng.randint(2, 3)))]
        else:
            premises = list(dict.fromkeys(ev() for _ in range(rng.randint(2, 3))))
            justs = [premises] + ([[ev(0.0)]] if shape == "conjunction_alt" else [])
        belief = b.derived(justs)
        if tops and rng.random() < 0.4:  # build on an earlier conclusion
            belief = b.derived([[belief, rng.choice(tops)]])
        depth = rng.randint(0, 2)
        tops.append(b.chain(belief, depth) if depth else belief)
    b.distractors(rng.randint(2, 4))
    loose = [n.id for n in b.nodes if n.is_evidence and n.id not in pool]  # distractor evidence
    hits = []
    for _ in range(rng.randint(*updates)):
        r = rng.random()
        target = rng.choice(loose) if loose and r < 0.1 else rng.choice(hits) if hits and r < 0.2 else rng.choice(pool)
        kind = rng.random()
        if kind < 0.35:
            b.update(target, Relation.RETRACTS)
        elif kind < 0.65:
            b.update(target, Relation.SUPERSEDES)
        elif kind < 0.82:
            b.update(target, Relation.HEDGES)
        else:
            b.update(target, Relation.RETRACTS, reliability="low")
        hits.append(target)
    return b, {"motifs": shapes, "derived": sum(not n.is_evidence for n in b.nodes),
               "evidence": sum(n.is_evidence for n in b.nodes), "updates": len(b.updates),
               "shared_facts": sum(1 for e in pool if sum(e in j for n in b.nodes for j in n.justifications) > 1)}


FAMILIES: dict[str, Callable[[random.Random], tuple[_Builder, dict]]] = {
    "F1": f1_chain,
    "F2": f2_independent_support,
    "F3": f3_conjunctive,
    "F6": f6_ambiguous,
}
# Long families: not in the default suite (existing suites and runs are unchanged).
LONG_FAMILIES: dict[str, Callable[[random.Random], tuple[_Builder, dict]]] = {
    "F7": f7_dossier,
}


def generate_suite(
    n_per_family: int,
    seed: int = 0,
    families: Sequence[str] = tuple(FAMILIES),
    domains: Sequence[str] = PILOT_DOMAINS,
) -> list[Scenario]:
    """Deterministic for a given seed. Each scenario has its own RNG stream, so adding
    families or scenarios does not change existing ones."""
    suite = []
    for fam in families:
        for i in range(n_per_family):
            rng = random.Random(f"{seed}:{fam}:{i}")
            builder, meta = {**FAMILIES, **LONG_FAMILIES}[fam](rng)
            suite.append(builder.build(f"{fam}-{i:03d}", fam, domains[i % len(domains)], meta))
    return suite
