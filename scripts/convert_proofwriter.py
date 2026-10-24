"""Convert ProofWriter (Tafjord et al. 2021; HF mirror tasksource/proofwriter) into BeliefGraph's
store format: system views (what a system sees) and eval views (gold), as for rendered runs.

- facts     = the theory's base facts (triples), from their canonical text in allProofs
- memories  = every derived conclusion (depth >= 1)
- policies  = the theory's rules (rules that never fire are natural decoys)
- graph     = exact OR-of-AND justifications from allProofs: each proof "(premises) -> rule" is
              one AND set; a nested application is the intermediate conclusion it derives
- updates   = 3-6 typed updates per theory, mostly on facts conclusions depend on: retractions,
              new values (attribute or object replaced), hedges from reliable sources, and denials
              from unverified sources. Gold actions come from the same labeller as BeliefBench.

Only no-negation, open-world theories are used (removing a fact can only remove conclusions).

    curl -L -o data/external/proofwriter/test.parquet \\
        https://huggingface.co/api/datasets/tasksource/proofwriter/parquet/default/test/0.parquet
    uv run --with pyarrow python scripts/convert_proofwriter.py --out data/rendered/proofwriter-v1
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import re
from collections import Counter
from pathlib import Path

ADJECTIVES = ["big", "small", "cold", "kind", "nice", "red", "blue", "green", "white", "young", "rough", "round",
              "furry", "quiet", "smart", "rough", "round", "high", "red"]


# ── allProofs parsing ──
def tokens(s: str) -> list[str]:
    return re.findall(r"\(|\)|->|OR|triple\d+|rule\d+", s)


def parse_proofs(expr: str):
    """'(alt OR alt ...)' -> list of alternatives; an alternative is ('fact', n) or
    ('app', rule, (items...))."""
    toks = tokens(expr)
    pos = 0

    def eat(t=None):
        nonlocal pos
        tok = toks[pos]
        if t is not None and tok != t:
            raise ValueError(f"expected {t}, got {tok} in {expr}")
        pos += 1
        return tok

    def item():
        tok = toks[pos]
        if tok.startswith("triple"):
            eat()
            return ("fact", int(tok[6:]))
        eat("(")
        eat("(")
        prem = []
        while toks[pos] != ")":
            prem.append(item())
        eat(")")
        eat("->")
        rule = eat()
        eat(")")
        return ("app", int(rule[4:]), tuple(prem))

    eat("(")
    alts = [item()]
    while toks[pos] == "OR":
        eat("OR")
        alts.append(item())
    eat(")")
    return alts


def conclusions(all_proofs: str) -> dict[str, list]:
    """{conclusion text: alternatives}."""
    out = {}
    for text, proof in re.findall(r"(?:@\d+:\s*)?([^\[\]@]+?\.)\[(\(.*?\))\]", all_proofs):
        out[text.strip()] = parse_proofs(proof)
    return out


def sentences(text: str) -> list[str]:
    return [s.strip() if s.strip().endswith(".") else s.strip() + "." for s in re.split(r"(?<=\.)\s+", text.strip())
            if s.strip(". ")]


# ── update texts ──
def negate(fact: str) -> str:
    return "It is not the case that " + fact[0].lower() + fact[1:]


def supersede(fact: str, rng: random.Random, objects: list[str]) -> str | None:
    m = re.match(r"^(.+?) is (\w+)\.$", fact)
    if m and m.group(2) in ADJECTIVES:
        new = rng.choice([a for a in sorted(set(ADJECTIVES)) if a != m.group(2)])
        return f"{m.group(1)} is now {new} rather than {m.group(2)}."
    m = re.match(r"^(.+?) (likes|sees|visits|chases|eats|needs) (.+?)\.$", fact)
    if m:
        others = [o for o in objects if o.lower() != m.group(3).lower() and o.lower() != m.group(1).lower()]
        if others:
            return f"{m.group(1)} now {m.group(2)} {rng.choice(others)} rather than {m.group(3)}."
    return None


def convert(row: dict, rng: random.Random, k: int) -> tuple[dict, dict] | None:
    concl = conclusions(row["allProofs"])
    fact_text, derived = {}, {}
    for text, alts in concl.items():
        base = [a[1] for a in alts if a[0] == "fact"]
        if base:
            fact_text[base[0]] = text
        else:
            derived[text] = alts
    n_fact, n_rule = row["NFact"], row["NRule"]
    rules = sentences(row["theory"])[-n_rule:]
    if len(rules) != n_rule or len(derived) < 4 or len(fact_text) < n_fact * 0.8:
        return None
    hexid = lambda: f"{rng.randrange(16 ** 4):04x}"
    used = set()

    def new(prefix):
        while True:
            i = f"{prefix}_{hexid()}"
            if i not in used:
                used.add(i)
                return i

    fid = {n: new("e") for n in fact_text}
    mid = {t: new("m") for t in derived}
    pid = {r + 1: new("p") for r in range(n_rule)}
    app_of = {alt: t for t, alts in derived.items() for alt in alts}  # application -> conclusion it derives

    def premise(x):
        if x[0] == "fact":
            return fid.get(x[1])
        t = app_of.get(x)
        return mid.get(t) if t else None

    justs, policy_of_mem = {}, {}
    for t, alts in derived.items():
        sets = []
        for a in alts:
            prem = [premise(x) for x in a[2]]
            if a[0] == "app" and all(prem):
                sets.append(sorted(set(prem)))
                policy_of_mem.setdefault(mid[t], pid[a[1]])
        justs[mid[t]] = [s for i, s in enumerate(sets) if s not in sets[:i]]
    if not all(justs.values()):
        return None
    # updates: mostly facts that something depends on
    supporting = [f for f in fid.values() if any(f in s for sets in justs.values() for s in sets)]
    rel = r"^(.+?) (likes|sees|visits|chases|eats|needs) (.+?)\.$"
    objects = sorted({x.lower() if x.lower().startswith("the ") else x
                      for t in fact_text.values() for m in [re.match(rel, t)] if m for x in (m.group(1), m.group(3))})
    start = dt.date(2026, 1, 1)
    evidence = [{"id": fid[n], "observed": (start + dt.timedelta(days=i)).isoformat(), "source": "Observation log",
                 "text": fact_text[n]} for i, n in enumerate(sorted(fact_text))]
    text_of = {e["id"]: e["text"] for e in evidence}
    updates, targets = [], {}
    for j in range(rng.randint(3, 6)):
        target = rng.choice(supporting) if supporting and rng.random() < 0.85 else rng.choice(list(fid.values()))
        r = rng.random()
        fact = text_of[target]
        sup = supersede(fact, rng, objects) if r < 0.25 else None
        if sup:
            rel, rel_src, src, text = "supersedes", "high", "Revised observation log", sup
        elif r < 0.6:
            rel, rel_src, src, text = "retracts", "high", "Verified correction notice", negate(fact)
        elif r < 0.8:
            rel, rel_src, src = "hedges", "high", "Verified review notice"
            text = "It is uncertain whether " + fact[0].lower() + fact[1:-1] + "; the observation is being re-checked."
        else:
            rel, rel_src, src = "retracts", "low", "Anonymous unverified note"
            text = "An unverified note claims that " + negate(fact)[0].lower() + negate(fact)[1:]
        u = new("u")
        updates.append({"id": u, "observed": (start + dt.timedelta(days=60 + j)).isoformat(), "source": src, "text": text})
        targets[u] = {"target": target, "relation": rel, "reliability": rel_src}
    sid = f"pw_{hexid()}{hexid()}"
    family = row["id"].rsplit("-", 1)[0]
    system = {"scenario": sid, "domain": "proofwriter", "evidence": evidence,
              "memories": [{"id": mid[t], "text": t} for t in derived],
              "policies": [{"id": pid[r], "text": rules[r - 1]} for r in sorted(pid)], "updates": updates}
    evaluation = {"scenario": sid, "source_scenario": row["id"], "family": family, "meta": {"maxD": row["maxD"]},
                  "idmap": {}, "justifications": justs, "reliability": {f: "high" for f in fid.values()},
                  "update_targets": targets, "policy_of": {}, "memory_policy": policy_of_mem, "gold": {}}
    return system, evaluation


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", default="data/external/proofwriter/test.parquet")
    ap.add_argument("--out", default="data/rendered/proofwriter-v1")
    ap.add_argument("--per-family", type=int, default=12)
    ap.add_argument("--seed", type=int, default=500)
    args = ap.parse_args()
    import pyarrow.parquet as pq

    t = pq.read_table(args.parquet, columns=["id", "maxD", "NFact", "NRule", "config", "theory", "allProofs"]).to_pylist()
    pools = {"AttNoneg-OWA-D5": [], "RelNoneg-OWA-D5": [], "AttNonegNatLang": []}
    seen = set()
    for row in t:
        key = next((k for k in pools if row["id"].startswith(k)), None)
        if key and row["theory"] not in seen and (key == "AttNonegNatLang" or row["maxD"] >= 3):
            seen.add(row["theory"])
            pools[key].append(row)
    rng = random.Random(args.seed)
    out = Path(args.out)
    for d in ("system", "eval"):
        (out / d).mkdir(parents=True, exist_ok=True)
    stats = Counter()
    from beliefbench.schema import Action
    from beliefgraph.core import UpdateReading, revise

    for key, rows in pools.items():
        rng.shuffle(rows)
        made = 0
        for row in rows:
            if made == args.per_family:
                break
            got = convert(row, rng, made)
            if not got:
                continue
            sv, ev = got
            readings = {u: UpdateReading(**r) for u, r in ev["update_targets"].items()}
            gold = revise(sv, ev["justifications"], ev["reliability"], readings)
            ev["gold"] = {k: v.value for k, v in gold.items()}
            changed = sum(1 for m in sv["memories"] if gold[m["id"]] is not Action.KEEP)
            if changed == 0:
                continue  # every scenario must test some revision
            (out / "system" / f"{sv['scenario']}.json").write_text(json.dumps(sv, indent=1))
            (out / "eval" / f"{sv['scenario']}.json").write_text(json.dumps(ev, indent=1))
            made += 1
            stats["scenarios"] += 1
            stats["memories"] += len(sv["memories"])
            stats["facts"] += len(sv["evidence"])
            stats["updates"] += len(sv["updates"])
            stats["or_memories"] += sum(len(s) > 1 for s in ev["justifications"].values())
            stats["chained_memories"] += sum(any(x.startswith("m_") for s in sets for x in s) for sets in ev["justifications"].values())
            for m in sv["memories"]:
                stats["gold_" + gold[m["id"]].value] += 1
        print(f"{key}: {made} scenarios")
    (out / "spend.json").write_text(json.dumps({"provider": "converted", "source": "ProofWriter (tasksource/proofwriter, test)",
                                                "seed": args.seed, "rendered": stats["scenarios"], "stats": dict(stats)}, indent=1))
    print(dict(stats))


if __name__ == "__main__":
    main()
