"""Differential check of ``labeler.gold_actions`` against Veritas-TMS (v0.16.0).

Shared semantic subset: every update *retracts* evidence, from a source at least as
reliable as the target, and is not older than it. On this subset our labels are only
keep / withdraw, and Veritas's well-founded Horn-clause retraction should give the same
final state. Outside it the two systems represent different things (Veritas has no
STALE / UNK, and handles reliability through entrenchment at assert time), so they are
not compared.

Veritas is an optional dependency (``uv sync --group audit``).
"""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import replace

from beliefbench.labeler import gold_actions, topo_order
from beliefbench.schema import RELIABILITY, Action, Kind, Node, Relation, Scenario, Update


def in_shared_subset(s: Scenario) -> bool:
    for u in s.updates:
        target = s.node(u.target)
        if u.relation is not Relation.RETRACTS or u.t < target.t:
            return False
        if RELIABILITY[u.reliability] < RELIABILITY[target.reliability]:
            return False
    return bool(s.updates)


def veritas_actions(s: Scenario) -> dict[str, Action]:
    """Replay the scenario in a Veritas BeliefStore and read the final states."""
    from veritas.store import BeliefStore

    # No contradiction detection: the graph is given; only retraction is under test.
    store = BeliefStore(contradiction_fn=lambda a, b: False)
    ids = [n.id for n in s.nodes]
    vid: dict[str, str] = {}
    for nid in topo_order(ids, s.justifications()):
        node = s.node(nid)
        just = None if node.is_evidence else [[vid[p] for p in j] for j in node.justifications]
        b = store.assert_belief(f"node {nid} holds", ground=node.is_evidence, justifications=just)
        if b is None:
            raise RuntimeError(f"{s.id}: Veritas rejected {nid}")
        vid[nid] = b.id
    if len(store.all_beliefs()) != len(ids):
        raise RuntimeError(f"{s.id}: Veritas merged beliefs (corroboration linking)")
    for u in s.updates:
        store.retract_belief(vid[u.target], reason=u.id)
    return {nid: Action.KEEP if store.get(vid[nid]).is_active else Action.WITHDRAW for nid in ids}


def disagreements(s: Scenario, other: Callable[[Scenario], dict[str, Action]] = veritas_actions) -> dict:
    ours, theirs = gold_actions(s), other(s)
    return {nid: (ours[nid], theirs[nid]) for nid in ours if ours[nid] is not theirs[nid]}


# ────────────────────────────── fuzzing ──────────────────────────────


def random_retraction_scenario(rng: random.Random, sid: str) -> Scenario:
    """Random DAG in the shared subset: diamonds, OR fan-in, AND sets, several
    retractions, and disconnected parts all arise."""
    n_ev, n_der = rng.randint(2, 7), rng.randint(1, 9)
    nodes = [Node(f"E{i + 1}", Kind.EVIDENCE, t=i + 1) for i in range(n_ev)]
    for i in range(n_der):
        pool = [n.id for n in nodes]
        weights = [1 + k for k in range(len(pool))]  # bias toward recent nodes -> depth
        justs: list[list[str]] = []
        for _ in range(rng.choices([1, 2, 3], [5, 3, 2])[0]):
            size = rng.choices([1, 2, 3], [5, 3, 2])[0]
            j = sorted(set(rng.choices(pool, weights, k=size)))
            if j not in justs:
                justs.append(j)
        nodes.append(Node(f"B{i + 1}", Kind.BELIEF, justifications=justs))
    evidence = [n.id for n in nodes if n.is_evidence]
    targets = rng.sample(evidence, rng.randint(1, min(3, len(evidence))))
    updates = [Update(f"U{k + 1}", n_ev + 1 + k, t, Relation.RETRACTS) for k, t in enumerate(targets)]
    s = Scenario(sid, "fuzz", "none", nodes, updates)
    s.validate()
    s.gold = gold_actions(s)
    return s


def features(s: Scenario) -> set[str]:
    """Structural features present, for coverage reporting."""
    justs = s.justifications()
    feats = set()
    if any(len(js) > 1 for js in justs.values()):
        feats.add("multi_support")
    if any(len(j) > 1 for js in justs.values() for j in js):
        feats.add("conjunctive")
    if len(s.updates) > 1:
        feats.add("multi_retraction")
    gold = s.gold or gold_actions(s)
    targets = {u.target for u in s.updates}
    for nid, js in justs.items():
        hit = [any(p in targets or gold.get(p) is Action.WITHDRAW for p in j) for j in js]
        if len(js) > 1 and any(hit) and not all(hit):
            feats.add("partial_support_loss")  # loses one alternative, keeps another
        if len(js) > 1 and all(hit):
            feats.add("all_supports_lost")
    # Diamond: some node reachable from one ancestor by two distinct paths.
    order = topo_order([n.id for n in s.nodes], justs)
    parents = {n: sorted({p for j in justs.get(n, []) for p in j}) for n in order}
    for src in order:
        paths = {src: 1}
        for n in order:
            if n != src:
                paths[n] = sum(paths.get(p, 0) for p in parents[n])
        if any(c > 1 for c in paths.values()):
            feats.add("diamond")
            break
    reached = set(targets)
    for n in order:
        if any(p in reached for p in parents[n]):
            reached.add(n)
    if len(reached) < len(order):
        feats.add("unaffected_part")
    return feats


# ────────────────────────────── minimisation ──────────────────────────────


def _drop_node(s: Scenario, victim: str) -> Scenario | None:
    """Remove a node; any justification mentioning it is dropped; derived nodes left
    without justifications are removed too (cascading)."""
    remove = {victim}
    while True:
        nodes = []
        for n in s.nodes:
            if n.id in remove:
                continue
            if not n.is_evidence:
                js = [j for j in n.justifications if not set(j) & remove]
                if not js:
                    remove.add(n.id)
                    break
                n = replace(n, justifications=js)
            nodes.append(n)
        else:
            break
    updates = [u for u in s.updates if u.target not in remove]
    if not updates:
        return None
    return Scenario(s.id, s.family, s.domain, nodes, updates, meta=dict(s.meta))


def minimize(s: Scenario, still_fails: Callable[[Scenario], bool]) -> Scenario:
    """Greedy delta debugging: drop nodes, alternative justifications, premises and
    updates while ``still_fails`` holds."""
    changed = True
    while changed:
        changed = False
        candidates: list[Scenario] = []
        for n in s.nodes:
            c = _drop_node(s, n.id)
            if c is not None:
                candidates.append(c)
            if not n.is_evidence:
                for i in range(len(n.justifications)):
                    if len(n.justifications) > 1:
                        js = n.justifications[:i] + n.justifications[i + 1 :]
                        candidates.append(_with_node(s, replace(n, justifications=js)))
                    if len(n.justifications[i]) > 1:
                        for p in n.justifications[i]:
                            js = [list(j) for j in n.justifications]
                            js[i] = [q for q in js[i] if q != p]
                            candidates.append(_with_node(s, replace(n, justifications=js)))
        if len(s.updates) > 1:
            for u in s.updates:
                candidates.append(Scenario(s.id, s.family, s.domain, s.nodes, [v for v in s.updates if v is not u]))
        for c in candidates:
            try:
                c.validate()
            except ValueError:
                continue
            if still_fails(c):
                s, changed = c, True
                break
    return s


def _with_node(s: Scenario, node: Node) -> Scenario:
    return Scenario(s.id, s.family, s.domain, [node if n.id == node.id else n for n in s.nodes], s.updates)


def render(s: Scenario, actions: dict[str, Action] | None = None) -> str:
    """Compact text form of a scenario, e.g. ``B1 <= (E1) | (E2 & E3)``."""
    lines = []
    for n in s.nodes:
        lhs = n.id + (" [decision]" if n.kind is Kind.DECISION else "")
        rhs = " | ".join("(" + " & ".join(j) + ")" for j in n.justifications) if n.justifications else "evidence"
        tag = f"   -> {actions[n.id].value}" if actions else ""
        lines.append(f"  {lhs} <= {rhs}{tag}")
    lines.append("  updates: " + ", ".join(
        f"{u.relation.value} {u.target}" + ("" if u.reliability == "high" else f" ({u.reliability}-reliability source)")
        for u in s.updates
    ))
    return "\n".join(lines)
