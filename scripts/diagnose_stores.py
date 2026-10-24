"""Where does BeliefGraph lose on a dataset? Replays a run_stream run from its cache (no calls)
and swaps in the gold graph / gold update readings, per-dossier (--per-scenario runs).

    uv run --all-extras python scripts/diagnose_stores.py --run long-s300-qwen3.5-9b --model qwen3.5-9b \\
        --thinking off --runs long-s300-p0 long-s300-p1 long-s300-p2
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from beliefbench.beliefgraph_eval import gold_inputs, load_rendered
from beliefbench.metrics import ExtractionScore
from beliefbench.schema import Action
from beliefbench.stream import gold_after, merge, step_view
from beliefgraph.cache import CachedLLM
from beliefgraph.core import DecomposedBeliefGraph, UpdateReading, revise


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--thinking", default="default", choices=["default", "on", "off"])
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--variant", default="v0.4", choices=["v0.4", "v0.8"])
    ap.add_argument("--read-implicit", action="store_true")
    args = ap.parse_args()

    class Replay:  # cache only: any call that was not made in the run fails loudly
        model, usage = args.model, []
        thinking = {"default": None, "on": True, "off": False}[args.thinking]

        supports_choice_probs = True  # v0.8 replays its cached probability passes

        def __call__(self, *a):
            raise RuntimeError(f"not cached: {a[2]}")

        def choice_probs(self, *a):
            raise RuntimeError(f"not cached: {a[-1]}")

    llm = CachedLLM(Replay(), Path("data/beliefgraph") / args.run / "raw")
    bg = DecomposedBeliefGraph(llm, workers=8, read_implicit=args.read_implicit,
                               **({"route_mode": "assign"} if args.variant == "v0.8" else {}))
    pool = [x for r in args.runs for x in load_rendered(Path("data/rendered") / r)]
    tot = Counter()
    ext = ExtractionScore()
    rel_mis = Counter()
    for i, item in enumerate(pool):
        store, comps = merge([item], seed=0)
        store["scenario"] = f"dossier{i:03d}"
        gj, grel, gread = {}, {}, {}
        for c in comps:
            j, rel, rd = gold_inputs(c["sv"], c["ev"], c["seed"])
            fwd = {v: k for k, v in c["back"].items()}
            gj.update({fwd[m]: [[fwd[p] for p in s] for s in js] for m, js in j.items()})
            grel.update({fwd[f]: v for f, v in rel.items()})
            gread.update({fwd[u]: UpdateReading(fwd[r.target], r.relation, r.reliability) for u, r in rd.items()})
        try:
            g = bg.build(step_view(store, 0))
            n = len(store["updates"])
            rd = {}
            for k in range(1, n + 1):
                rd.update(bg.read_updates(step_view(store, k, only_last=True) | {"scenario": store["scenario"]})[0])
        except RuntimeError as e:
            print(f"dossier {i}: {e}")
            continue
        ext.add(gj, g.justifications)
        v, gold = step_view(store, n), gold_after(store, comps, n)
        variants = {"P": revise(v, g.justifications, g.reliability, rd),
                    "gold-graph": revise(v, gj, g.reliability, rd),
                    "gold-readings": revise(v, g.justifications, grel, gread),
                    "gold-both": revise(v, gj, grel, gread)}
        for name, P in variants.items():
            for m in gold:
                tot[name, "n"] += 1
                tot[name, "right"] += P[m] == gold[m]
                rev = gold[m] is not Action.KEEP
                tot[name, "rev" if rev else "keep"] += 1
                tot[name, "rev_hit" if rev else "keep_hit"] += (P[m] is not Action.KEEP) == rev
        tot["updates"] += n
        tot["reading_exact"] += sum(rd.get(u) == gread[u] for u in gread)
        tot["target_right"] += sum(bool(rd.get(u)) and rd[u].target == gread[u].target for u in gread)
        for u in gread:
            r = rd.get(u)
            if r and r.target == gread[u].target and (r.relation, r.reliability) != (gread[u].relation, gread[u].reliability):
                rel_mis[(gread[u].relation, gread[u].reliability), (r.relation, r.reliability)] += 1
    s = ext.summary()
    print(f"{args.run}: graph set-F1 {s['justification_set_f1']:.3f}; update reading exact {tot['reading_exact']}/{tot['updates']}, "
          f"right target {tot['target_right']}/{tot['updates']}")
    for name in ("P", "gold-graph", "gold-readings", "gold-both"):
        bal = (tot[name, "rev_hit"] / tot[name, "rev"] + tot[name, "keep_hit"] / tot[name, "keep"]) / 2
        print(f"  {name:13s} accuracy {tot[name, 'right'] / tot[name, 'n']:.3f}  balanced {bal:.3f}")
    print("  most common reading confusions (gold -> read):", rel_mis.most_common(5))


if __name__ == "__main__":
    main()
