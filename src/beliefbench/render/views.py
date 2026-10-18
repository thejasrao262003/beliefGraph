"""Split a rendered scenario into the two files that must never be mixed.

- **System view**: what the evaluated system receives. Opaque ids, memories in random
  order, evidence timestamps re-permuted (generation order would leak structure). No
  gold, justifications, rationale, family or meta.
- **Eval view**: gold labels and justifications keyed by the same opaque ids, plus the
  id map and rationale, for scoring and human review.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import random
from dataclasses import replace

from beliefbench.labeler import gold_actions
from beliefbench.render.prompt import Rendering
from beliefbench.schema import Scenario

BASE_DATE = dt.date(2026, 1, 5)
SYSTEM_VIEW_KEYS = {"scenario", "domain", "evidence", "memories", "updates"}


def _opaque(rng: random.Random, prefix: str, used: set[str]) -> str:
    while True:
        oid = f"{prefix}_{rng.getrandbits(16):04x}"
        if oid not in used:
            used.add(oid)
            return oid


def permuted_scenario(s: Scenario, rng: random.Random) -> Scenario:
    """Re-time the scenario for display: evidence gets a random order (generation order
    leaks structure, and the generator adds distractors after the updates), and all
    updates follow all evidence in their original order. Gold is re-checked; this raises
    for a scenario whose labels depend on an update being older than its target."""
    ev = [n for n in s.nodes if n.is_evidence]
    times = list(range(1, len(ev) + 1))
    rng.shuffle(times)
    new_t = dict(zip((n.id for n in ev), times))
    nodes = [replace(n, t=new_t[n.id]) if n.is_evidence else n for n in s.nodes]
    updates = [replace(u, t=len(ev) + 1 + k) for k, u in enumerate(s.updates)]
    out = Scenario(s.id, s.family, s.domain, nodes, updates, meta=s.meta)
    if gold_actions(out) != (s.gold or gold_actions(s)):
        raise ValueError(f"{s.id}: timestamp permutation changed gold labels")
    return out


def _date(t: int) -> str:
    return (BASE_DATE + dt.timedelta(days=3 * t)).isoformat()


def build_views(s: Scenario, r: Rendering, seed: int = 0) -> tuple[dict, dict]:
    if not r.ok:
        raise ValueError(f"{s.id}: rendering has errors: {r.errors}")
    rng = random.Random(f"{seed}:{s.id}:view")
    ps = permuted_scenario(s, rng)
    used: set[str] = set()
    idmap = {}
    for n in ps.nodes:
        idmap[n.id] = _opaque(rng, "e" if n.is_evidence else "m", used)
    for u in ps.updates:
        idmap[u.id] = _opaque(rng, "u", used)
    sid = "s_" + hashlib.sha256(f"{seed}:{s.id}".encode()).hexdigest()[:10]

    evidence = sorted(
        ({"id": idmap[n.id], "observed": _date(n.t), "source": r.sources[n.id], "text": r.texts[n.id]}
         for n in ps.nodes if n.is_evidence),
        key=lambda e: (e["observed"], e["id"]),
    )
    memories = [{"id": idmap[n.id], "text": r.texts[n.id]} for n in ps.nodes if not n.is_evidence]
    rng.shuffle(memories)
    updates = [
        {"id": idmap[u.id], "observed": _date(u.t), "source": r.sources[u.id], "text": r.update_texts[u.id]}
        for u in ps.updates
    ]
    system = {"scenario": sid, "domain": s.domain.replace("_", " "), "evidence": evidence,
              "memories": memories, "updates": updates}

    gold = ps.gold or gold_actions(ps)
    evaluation = {
        "scenario": sid,
        "source_scenario": s.id,
        "family": s.family,
        "meta": s.meta,
        "idmap": idmap,
        "gold": {idmap[k]: v.value for k, v in gold.items()},
        "justifications": {idmap[k]: [[idmap[p] for p in j] for j in js] for k, js in ps.justifications().items()},
        "update_targets": {idmap[u.id]: {"target": idmap[u.target], "relation": u.relation.value,
                                         "reliability": u.reliability} for u in ps.updates},
        "world": r.world,
        "rationale": {idmap[k]: v for k, v in r.rationale.items() if k in idmap},
    }
    return system, evaluation
