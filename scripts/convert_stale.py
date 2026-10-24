"""Convert STALE (2026; HF STALEproj/STALE, CC-BY-4.0) into BeliefGraph stores.

STALE pairs an earlier user observation (M_old) with a later one (M_new) that IMPLICITLY
changes the state M_old implied (T1: direct state change, e.g. a new city; T2: inferred through
common sense, e.g. scorpions and dry heat imply the user no longer lives in Portland). Its
stale-premise probe (dim2_query) is a plan that presupposes M_old.

- fact     = "The user said: <M_old>"
- memory   = the plan in dim2_query, which rests on that fact ("Since <premise>, <request>")
- update   = "The user said: <M_new>" (supersedes the old state; reliable source: the user)
- rule     = one generic rule: a plan for the user holds only while its premise holds
- store    = 12 items; for 4 of them M_new is withheld (their plans should be kept)
- gold     = the BeliefBench labeller: plans resting on a superseded fact -> recompute, else keep

The texts are STALE's own (LLM-generated, expert-validated); the haystack sessions are not used.

    uv run --all-extras python scripts/convert_stale.py --out data/rendered/stale-v1
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import re
from collections import Counter
from pathlib import Path

RULE = ("A plan or recommendation made for the user holds only while the personal circumstances it "
        "was based on still hold.")
DECOYS = ["A reminder the user asked for stays scheduled until the user cancels it.",
          "A preference the user stated applies to every later recommendation of the same kind."]


def plan_text(q: str) -> str | None:
    m = re.match(r"^\s*(?:Since|Given that|Because|As)\s+(.+?),\s*(?:can|could|would|will)\s+you\s+(.+?)\??\s*$", q, re.S)
    if not m:
        return None
    premise, request = m.group(1).strip(), m.group(2).strip().rstrip("?")
    return f"Planned for the user, because {premise}: {request}."


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/external/stale/T1_T2_400_FULL.json")
    ap.add_argument("--out", default="data/rendered/stale-v1")
    ap.add_argument("--per-store", type=int, default=12)
    ap.add_argument("--withheld", type=int, default=4)
    ap.add_argument("--seed", type=int, default=900)
    args = ap.parse_args()
    items = json.loads(Path(args.data).read_text())
    rng = random.Random(args.seed)
    usable = [x for x in items if plan_text(x["probing_queries"]["dim2_query"])]
    rng.shuffle(usable)
    out = Path(args.out)
    for d in ("system", "eval"):
        (out / d).mkdir(parents=True, exist_ok=True)
    from beliefbench.schema import Action
    from beliefgraph.core import UpdateReading, revise

    stats = Counter({"items_total": len(items), "items_usable": len(usable)})
    start = dt.date(2026, 1, 1)
    for s in range(len(usable) // args.per_store):
        group = usable[s * args.per_store : (s + 1) * args.per_store]
        used: set[str] = set()

        def new(prefix):
            while True:
                i = f"{prefix}_{rng.randrange(16 ** 4):04x}"
                if i not in used:
                    used.add(i)
                    return i

        rule_id = new("p")
        policies = [{"id": rule_id, "text": RULE}] + [{"id": new("p"), "text": t} for t in DECOYS]
        evidence, memories, updates, justs, targets, types = [], [], [], {}, {}, {}
        withheld = set(rng.sample(range(len(group)), args.withheld))
        for k, x in enumerate(group):
            f, m = new("e"), new("m")
            evidence.append({"id": f, "observed": (start + dt.timedelta(days=k)).isoformat(), "source": "User conversation",
                             "text": f"The user said: \"{x['M_old'].strip()}\""})
            memories.append({"id": m, "text": plan_text(x["probing_queries"]["dim2_query"])})
            justs[m] = [[f]]
            types[m] = x["type"]
            if k not in withheld:
                u = new("u")
                updates.append({"id": u, "observed": "", "source": "User conversation",
                                "text": f"The user said: \"{x['M_new'].strip()}\""})
                targets[u] = {"target": f, "relation": "supersedes", "reliability": "high"}
        rng.shuffle(updates)
        for n, u in enumerate(updates):
            u["observed"] = (start + dt.timedelta(days=60 + n)).isoformat()
        sid = f"st_{rng.randrange(16 ** 8):08x}"
        sv = {"scenario": sid, "domain": "personal assistant (STALE)", "evidence": evidence, "memories": memories,
              "policies": policies, "updates": updates}
        ev = {"scenario": sid, "source_scenario": f"STALE store {s}", "family": "STALE",
              "meta": {"uids": [x["uid"] for x in group], "types": types}, "idmap": {}, "justifications": justs,
              "reliability": {e["id"]: "high" for e in evidence}, "update_targets": targets, "policy_of": {},
              "memory_policy": {m: rule_id for m in justs}, "gold": {}}
        gold = revise(sv, justs, ev["reliability"], {u: UpdateReading(**t) for u, t in targets.items()})
        ev["gold"] = {k: v.value for k, v in gold.items()}
        (out / "system" / f"{sid}.json").write_text(json.dumps(sv, indent=1))
        (out / "eval" / f"{sid}.json").write_text(json.dumps(ev, indent=1))
        stats["stores"] += 1
        stats["memories"] += len(memories)
        stats["updates"] += len(updates)
        for m in memories:
            stats[f"gold_{gold[m['id']].value}"] += 1
            stats[f"type_{types[m['id']]}"] += 1
    (out / "spend.json").write_text(json.dumps({"provider": "converted", "source": "STALE (STALEproj/STALE, CC-BY-4.0)",
                                                "seed": args.seed, "rendered": stats["stores"], "stats": dict(stats)}, indent=1))
    print(dict(stats))


if __name__ == "__main__":
    main()
