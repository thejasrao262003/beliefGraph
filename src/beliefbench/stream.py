"""Large memory stores with sequential updates.

Accepted scenarios are merged into one store (ids re-namespaced per scenario so nothing
reveals where an item came from); their updates arrive one at a time, in a seeded
interleaved order that keeps each scenario's own updates in order. Gold after every step is
exact: the gold graph and readings of the updates applied so far, through the same
propagation that reproduces gold on every accepted scenario.
"""

from __future__ import annotations

import datetime as dt
import random
import re

from beliefbench.beliefgraph_eval import gold_inputs
from beliefbench.schema import Action
from beliefgraph.core import UpdateReading, revise

_ID = re.compile(r"\b([empu])_([0-9a-f]{4})\b")


def _ns(k: int, oid: str) -> str:
    kind, rest = oid.split("_", 1)
    return f"{kind}_{k:02d}{rest}"


def merge(items: list[tuple[dict, dict, int]], seed: int = 0) -> tuple[dict, list[dict]]:
    """``items``: (system view, eval view, generator seed) per scenario. Returns the merged
    store (a view whose ``updates`` is the full stream, in arrival order) and one component
    record per scenario (its views, seed and id map from merged ids to its own)."""
    rng = random.Random(seed)
    store = {"scenario": f"store{len(items)}_{seed}", "domain": "product eligibility",
             "evidence": [], "memories": [], "policies": [], "updates": []}
    comps, queues = [], []
    for k, (sv, ev, gseed) in enumerate(items):
        back = {}
        for sec in ("evidence", "memories", "policies"):
            for x in sv.get(sec, []):
                y = dict(x, id=_ns(k, x["id"]))
                back[y["id"]] = x["id"]
                store[sec].append(y)
        q = []
        for u in sorted(sv["updates"], key=lambda u: (u["observed"], u["id"])):
            y = dict(u, id=_ns(k, u["id"]))
            back[y["id"]] = u["id"]
            q.append(y)
        comps.append({"k": k, "sv": sv, "ev": ev, "seed": gseed, "back": back})
        queues.append(q)
    for sec in ("evidence", "memories", "policies"):
        rng.shuffle(store[sec])
    store["evidence"].sort(key=lambda e: e["observed"])
    start = dt.date(2026, 3, 1)  # every update arrives after all evidence, one day apart
    while any(queues):
        q = rng.choice([q for q in queues if q])
        u = q.pop(0)
        store["updates"].append(dict(u, observed=(start + dt.timedelta(days=len(store["updates"]))).isoformat()))
    return store, comps


def step_view(store: dict, n: int, only_last: bool = False) -> dict:
    """The store after the first ``n`` updates (or with only update ``n`` when ``only_last``)."""
    ups = store["updates"][n - 1 : n] if only_last else store["updates"][:n]
    return dict(store, updates=ups)


def gold_after(store: dict, comps: list[dict], n: int) -> dict[str, Action]:
    """Gold action for every memory of the store after the first ``n`` updates."""
    applied = {u["id"] for u in store["updates"][:n]}
    out: dict[str, Action] = {}
    for c in comps:
        sv, ev, back = c["sv"], c["ev"], c["back"]
        gj, grel, gread = gold_inputs(sv, ev, c["seed"])
        mine = {back[u] for u in applied if u in back}
        part = dict(sv, updates=[u for u in sv["updates"] if u["id"] in mine])
        actions = revise(part, gj, grel, {u: r for u, r in gread.items() if u in mine})
        fwd = {v: k for k, v in back.items()}
        out.update({fwd[m]: a for m, a in actions.items() if m.startswith("m_")})
    return out


def touched(store: dict, comps: list[dict], n: int) -> set[str]:
    """Memories of every scenario that has received at least one update so far."""
    applied = {u["id"] for u in store["updates"][:n]}
    out = set()
    for c in comps:
        if any(u in c["back"] for u in applied):
            out |= {m for m in c["back"] if m.startswith("m_")}
    return out


def readings_to_store(readings: dict[str, UpdateReading]) -> dict[str, UpdateReading]:
    return dict(readings)
