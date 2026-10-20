"""Scoring BeliefGraph on rendered benchmark scenarios.

BeliefGraph sees only the system view. The eval view (and the frozen generator, for the
evidence reliabilities the views do not carry) supplies the gold graph, the gold reading of
each update and the gold actions. Variants isolate where errors come from:

- ``P``                 induced graph + induced update readings (the full system)
- ``P-oracle-graph``    gold graph + induced readings (removes graph-building error)
- ``P-oracle-readings`` induced graph + gold readings (removes update-reading error)
- ``P-oracle``          gold graph + gold readings (must equal gold: a harness check)
- ``naive-cascade`` / ``direct-only``: no-LLM baselines on the gold graph and readings
- ``LLM-direct``        the same model labels each memory itself, without a graph
                        (scored when the item carries ``direct`` actions)
"""

from __future__ import annotations

import csv
import json
import random
from math import comb
from pathlib import Path

from beliefbench.baselines import direct_only, naive_cascade
from beliefbench.generate import generate_suite
from beliefbench.metrics import ExtractionScore, RevisionScore
from beliefbench.schema import Action
from beliefgraph.core import UpdateReading, as_scenario, revise


def load_accepted(run_dir: Path) -> list[tuple[dict, dict, int]]:
    """(system view, eval view, generator seed) for every scenario accepted in review."""
    decisions = {r["scenario"]: r["decision"] for r in csv.DictReader((run_dir / "review.csv").open())}
    seed = json.loads((run_dir / "spend.json").read_text())["seed"]
    out = []
    for f in sorted((run_dir / "system").glob("*.json")):
        sv = json.loads(f.read_text())
        if decisions.get(sv["scenario"]) == "accept":
            out.append((sv, json.loads((run_dir / "eval" / f.name).read_text()), seed))
    return out


_SUITES: dict[int, dict] = {}


def gold_inputs(sv: dict, ev: dict, seed: int) -> tuple[dict, dict, dict[str, UpdateReading]]:
    """Gold graph, gold source reliabilities and gold update readings, in opaque ids."""
    if seed not in _SUITES:
        _SUITES[seed] = {s.id: s for s in generate_suite(10, seed)}
    s = _SUITES[seed][ev["source_scenario"]]
    idmap = ev["idmap"]
    reliability = {idmap[n.id]: n.reliability for n in s.nodes if n.is_evidence}
    readings = {uid: UpdateReading(u["target"], u["relation"], u["reliability"])
                for uid, u in ev["update_targets"].items()}
    return ev["justifications"], reliability, readings


def memory_gold(ev: dict) -> dict[str, Action]:
    return {k: Action(v) for k, v in ev["gold"].items() if k.startswith("m_")}


def _memories(actions: dict[str, Action]) -> dict[str, Action]:
    return {k: v for k, v in actions.items() if k.startswith("m_")}


def paired(items: list[dict], a: str = "P", b: str = "direct", resamples: int = 2000, seed: int = 0) -> dict:
    """Paired comparison of two systems on the same memories: exact McNemar test on the
    discordant memories, and a scenario-level (cluster) bootstrap 95% CI for the accuracy
    difference a - b. ``items`` carry ``pred_P`` and ``direct`` action maps and ``gold``."""
    per = []  # (correct_a, correct_b, n) per scenario
    a_only = b_only = 0
    for it in items:
        if it.get(b) is None:
            continue
        ca = cb = 0
        for m, g in it["gold"].items():
            ra, rb = it[f"pred_{a}"][m] is g, it[b][m] is g
            ca, cb = ca + ra, cb + rb
            a_only += ra and not rb
            b_only += rb and not ra
        per.append((ca, cb, len(it["gold"])))
    if not per:
        return {}
    k, n = min(a_only, b_only), a_only + b_only
    p = min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n) if n else 1.0
    rng = random.Random(seed)
    diffs = []
    for _ in range(resamples):
        sample = [per[rng.randrange(len(per))] for _ in per]
        tot = sum(x[2] for x in sample)
        diffs.append((sum(x[0] for x in sample) - sum(x[1] for x in sample)) / tot)
    diffs.sort()
    tot = sum(x[2] for x in per)
    return {"accuracy_diff": (sum(x[0] for x in per) - sum(x[1] for x in per)) / tot,
            "ci95": [diffs[int(0.025 * resamples)], diffs[int(0.975 * resamples) - 1]],
            f"{a}_right_{b}_wrong": a_only, f"{b}_right_{a}_wrong": b_only, "mcnemar_exact_p": p,
            "scenarios": len(per), "memories": tot}


def score(items: list[dict]) -> dict:
    """``items``: one dict per scenario with sv, ev, seed, and the induced graph/readings
    (``graph`` with justifications + reliability, ``readings``). Returns per-variant
    revision scores on memories, plus graph-extraction and update-reading accuracy."""
    rev = {k: RevisionScore() for k in ("P", "P-oracle-graph", "P-oracle-readings", "P-oracle",
                                         "naive-cascade", "direct-only", "LLM-direct")}
    by_family: dict[str, RevisionScore] = {}
    direct_by_family: dict[str, RevisionScore] = {}
    ext = ExtractionScore()
    reading_ok = reading_n = rel_ok = rel_n = 0
    for it in items:
        sv, ev = it["sv"], it["ev"]
        gj, grel, gread = gold_inputs(sv, ev, it["seed"])
        ij, irel, iread = it["graph"]["justifications"], it["graph"]["reliability"], it["readings"]
        gold = memory_gold(ev)
        variants = {
            "P": revise(sv, ij, irel, iread),
            "P-oracle-graph": revise(sv, gj, irel, iread),
            "P-oracle-readings": revise(sv, ij, grel, gread),
            "P-oracle": revise(sv, gj, grel, gread),
        }
        gs = as_scenario(sv, gj, grel, gread)
        variants["naive-cascade"] = naive_cascade(gs)
        variants["direct-only"] = direct_only(gs)
        for k, actions in variants.items():
            rev[k].add(gold, _memories(actions))
        it["gold"], it["pred_P"] = gold, _memories(variants["P"])
        by_family.setdefault(ev["family"], RevisionScore()).add(gold, _memories(variants["P"]))
        if it.get("direct") is not None:
            rev["LLM-direct"].add(gold, it["direct"])
            direct_by_family.setdefault(ev["family"], RevisionScore()).add(gold, it["direct"])
        ext.add({m: j for m, j in gj.items()}, ij)
        for uid, g in gread.items():
            r = iread.get(uid)
            reading_n += 1
            reading_ok += bool(r and (r.target, r.relation, r.reliability) == (g.target, g.relation, g.reliability))
        for fid, level in grel.items():
            rel_n += 1
            rel_ok += irel.get(fid) == level
    return {
        "scenarios": len(items),
        "revision": {k: v.summary() for k, v in rev.items()},
        "revision_P_by_family": {k: v.summary() for k, v in sorted(by_family.items())},
        "revision_LLM_direct_by_family": {k: v.summary() for k, v in sorted(direct_by_family.items())},
        "paired_P_vs_LLM_direct": paired(items),
        "unsupported_memories": sum(len(it["graph"].get("unsupported") or []) for it in items),
        "graph_extraction": ext.summary(),
        "update_reading_exact": reading_ok / reading_n if reading_n else None,
        "source_reliability_accuracy": rel_ok / rel_n if rel_n else None,
    }
