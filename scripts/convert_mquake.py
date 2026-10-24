"""Convert MQuAKE-T (Zhong et al. 2023; real temporal Wikidata edits) into BeliefGraph stores.

Each MQuAKE case is a chain of single-hop facts (subject -relation-> object ...) whose composition
is a multi-hop conclusion, and an edit that changes one hop. Cases are grouped into stores so
that cases sharing a fact sit together (one real-world change then hits several memories).

- facts     = single-hop facts, written as MQuAKE's cloze + answer ("The headquarters of TV Land is
              located in the city of New York City."); identical facts are one item
- memories  = composed conclusions, one per prefix of a chain of length >= 2 ("The head of
              government of the headquarters location of TV Land is Bill de Blasio."); a 3-hop
              chain yields an intermediate memory that the final one rests on
- policies  = relation-composition rules, one per (chain so far, next relation), shared across
              cases; rules from other stores are added as decoys
- updates   = the case's real edit, a new value for one hop ("supersedes"); 20% of edits are
              attributed to an unverified source instead (gold: uncertain), to exercise reliability.

    curl -L -o data/external/mquake/MQuAKE-T.json \\
        https://raw.githubusercontent.com/princeton-nlp/MQuAKE/main/datasets/MQuAKE-T.json
    uv run --all-extras python scripts/convert_mquake.py --out data/rendered/mquake-t-v1
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import random
from collections import Counter
from pathlib import Path


def chain_label(rels: list[str]) -> str:
    """['headquarters location', 'head of government'] -> 'head of government of the headquarters location'."""
    out = rels[0]
    for r in rels[1:]:
        out = f"{r} of the {out}"
    return out


def rule_text(prev: list[str], rel: str) -> str:
    left = chain_label(prev)
    return (f"If the {left} of something is X, and the {rel} of X is Y, then the {rel} of the {left} "
            f"of that thing is Y.")


def memory_text(subject: str, rels: list[str], answer: str) -> str:
    return f"The {chain_label(rels)} of {subject} is {answer}."


def build_store(cases: list[dict], rng: random.Random, decoy_rules: list[str], idx: int) -> tuple[dict, dict] | None:
    used: set[str] = set()

    def new(prefix):
        while True:
            i = f"{prefix}_{rng.randrange(16 ** 4):04x}"
            if i not in used:
                used.add(i)
                return i

    facts, mems, rules, justs, mem_rule = {}, {}, {}, {}, {}
    edits = {}
    for c in cases:
        hops = c["single_hops"]
        labeled = c["orig"]["triples_labeled"]
        if len(labeled) != len(hops):
            return None
        fids = []
        for h in hops:
            text = f"{h['cloze'].rstrip()} {h['answer']}."
            if text not in facts:
                facts[text] = new("e")
            fids.append(facts[text])
        subject = labeled[0][0]
        prev_item = fids[0]
        for k in range(1, len(labeled)):
            rels = [t[1] for t in labeled[: k + 1]]
            rt = rule_text([t[1] for t in labeled[:k]], labeled[k][1])
            if rt not in rules:
                rules[rt] = new("p")
            mt = memory_text(subject, rels, labeled[k][2])
            if mt not in mems:
                mems[mt] = new("m")
                justs[mems[mt]] = [sorted([prev_item, fids[k]])]
                mem_rule[mems[mt]] = rules[rt]
            prev_item = mems[mt]
        for k in c["orig"]["edit_triples_idx"]:
            target = fids[k]
            new_hop = c["new_single_hops"][k]
            edits.setdefault(target, f"{new_hop['cloze'].rstrip()} {new_hop['answer']}.")
    for d in rng.sample(decoy_rules, min(len(decoy_rules), max(3, len(rules) // 2))):
        if d not in rules:
            rules[d] = new("p")
    start = dt.date(2026, 1, 1)
    evidence = [{"id": i, "observed": (start + dt.timedelta(days=n % 50)).isoformat(),
                 "source": "Wikidata snapshot", "text": t} for n, (t, i) in enumerate(facts.items())]
    updates, targets = [], {}
    for n, (target, text) in enumerate(sorted(edits.items())):
        u = new("u")
        if rng.random() < 0.2:
            src, rel, text = "Unverified social media post", "low", f"An unverified post claims: {text}"
        else:
            src, rel = "Official records update", "high"
        updates.append({"id": u, "observed": (start + dt.timedelta(days=70 + n)).isoformat(), "source": src, "text": text})
        targets[u] = {"target": target, "relation": "supersedes", "reliability": rel}
    rng.shuffle(updates)
    for n, u in enumerate(updates):  # arrival order is random; dates follow it
        u["observed"] = (start + dt.timedelta(days=70 + n)).isoformat()
    sid = f"mq_{rng.randrange(16 ** 8):08x}"
    system = {"scenario": sid, "domain": "world knowledge (Wikidata)", "evidence": evidence,
              "memories": [{"id": i, "text": t} for t, i in mems.items()],
              "policies": [{"id": i, "text": t} for t, i in rules.items()], "updates": updates}
    evaluation = {"scenario": sid, "source_scenario": f"MQuAKE-T store {idx}", "family": "MQuAKE-T",
                  "meta": {"cases": [c["case_id"] for c in cases]}, "idmap": {}, "justifications": justs,
                  "reliability": {e["id"]: "high" for e in evidence}, "update_targets": targets,
                  "policy_of": {}, "memory_policy": mem_rule, "gold": {}}
    return system, evaluation


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/external/mquake/MQuAKE-T.json")
    ap.add_argument("--out", default="data/rendered/mquake-t-v1")
    ap.add_argument("--stores", type=int, default=36)
    ap.add_argument("--cases-per-store", type=int, default=10)
    ap.add_argument("--seed", type=int, default=700)
    ap.add_argument("--min-cases", type=int, default=10**9, help="keep stores with at least this many cases")
    ap.add_argument("--random-pack", action="store_true",
                    help="large stores: draw cases at random, preferring distinct edits (instead of fact-sharing groups)")
    args = ap.parse_args()
    cases = json.loads(Path(args.data).read_text())
    rng = random.Random(args.seed)
    # group cases that share a single-hop fact (union-find), then pack groups into stores
    key = lambda h: (h["cloze"], h["answer"])
    parent = list(range(len(cases)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    first = {}
    for i, c in enumerate(cases):
        for h in c["single_hops"]:
            k = key(h)
            if k in first:
                parent[find(i)] = find(first[k])
            else:
                first[k] = i
    groups: dict[int, list[int]] = {}
    for i in range(len(cases)):
        groups.setdefault(find(i), []).append(i)
    comps = list(groups.values())
    rng.shuffle(comps)
    comps.sort(key=len, reverse=True)
    stores: list[list[int]] = []
    for comp in comps:  # split large components, pack small ones
        while comp:
            take, comp = comp[: args.cases_per_store], comp[args.cases_per_store:]
            room = next((s for s in stores if len(s) + len(take) <= args.cases_per_store), None)
            if room is not None:
                room.extend(take)
            else:
                stores.append(list(take))
    stores = [s for s in stores if len(s) >= min(args.min_cases, args.cases_per_store // 2)]
    if args.random_pack:
        order = list(range(len(cases)))
        rng.shuffle(order)
        edit_key = lambda c: tuple((c["new_single_hops"][k]["cloze"], c["new_single_hops"][k]["answer"])
                                   for k in c["orig"]["edit_triples_idx"])
        seen, first, later = set(), [], []
        for i in order:
            (later if edit_key(cases[i]) in seen else first).append(i)
            seen.add(edit_key(cases[i]))
        pick = (first + later)[: args.cases_per_store]
        stores = [pick]
    rng.shuffle(stores)
    all_rules = sorted({rule_text([t[1] for t in c["orig"]["triples_labeled"][:k]], c["orig"]["triples_labeled"][k][1])
                        for c in cases for k in range(1, len(c["orig"]["triples_labeled"]))})
    out = Path(args.out)
    for d in ("system", "eval"):
        (out / d).mkdir(parents=True, exist_ok=True)
    from beliefbench.schema import Action
    from beliefgraph.core import UpdateReading, revise

    stats = Counter()
    made = 0
    for idx, s in enumerate(stores):
        if made == args.stores:
            break
        got = build_store([cases[i] for i in s], rng, all_rules, idx)
        if not got:
            continue
        sv, ev = got
        readings = {u: UpdateReading(**r) for u, r in ev["update_targets"].items()}
        gold = revise(sv, ev["justifications"], ev["reliability"], readings)
        ev["gold"] = {k: v.value for k, v in gold.items()}
        if not any(gold[m["id"]] is not Action.KEEP for m in sv["memories"]):
            continue
        (out / "system" / f"{sv['scenario']}.json").write_text(json.dumps(sv, indent=1))
        (out / "eval" / f"{sv['scenario']}.json").write_text(json.dumps(ev, indent=1))
        made += 1
        stats["stores"] += 1
        stats["cases"] += len(s)
        stats["memories"] += len(sv["memories"])
        stats["facts"] += len(sv["evidence"])
        stats["policies"] += len(sv["policies"])
        stats["updates"] += len(sv["updates"])
        stats["chained_memories"] += sum(any(x.startswith("m_") for x in sets[0]) for sets in ev["justifications"].values())
        for m in sv["memories"]:
            stats["gold_" + gold[m["id"]].value] += 1
    (out / "spend.json").write_text(json.dumps({"provider": "converted", "source": "MQuAKE-T (princeton-nlp/MQuAKE)",
                                                "seed": args.seed, "rendered": made, "stats": dict(stats)}, indent=1))
    print(dict(stats))


if __name__ == "__main__":
    main()
