"""Compare BeliefGraph builder variants on the large-store stream (BeliefGraph only; the
LLM-direct baseline does not change between variants, see scripts/run_stream.py).

    uv run --all-extras python scripts/eval_stream_variants.py --sizes 10 30 63

Calls go through the stream run's cache (data/beliefgraph/stream-qwen35-9b/raw), so a
rerun with the same prompts replays for free; new variants only pay for their new calls.
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from run_stream import RUNS, step_score  # noqa: E402

from beliefbench.beliefgraph_eval import gold_inputs, load_accepted  # noqa: E402
from beliefbench.metrics import ExtractionScore  # noqa: E402
from beliefbench.stream import gold_after, merge, step_view, touched  # noqa: E402
from beliefgraph.cache import CachedLLM  # noqa: E402
from beliefgraph.core import DecomposedBeliefGraph, revise  # noqa: E402
from beliefgraph.llm import make_llm  # noqa: E402

VARIANTS = {
    "v0.2.1": dict(samples=1, adjudicate=False),
    "v0.4": dict(),  # 3 seeded samples for routing and grounding, adjudication of split votes
    "v0.4-vote-only": dict(adjudicate=False),
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", type=int, nargs="+", default=[10, 30])
    ap.add_argument("--variants", nargs="+", default=["v0.2.1", "v0.4"], choices=list(VARIANTS))
    ap.add_argument("--provider", default="modal")
    ap.add_argument("--model", default="qwen3.5-9b")
    ap.add_argument("--run", default="stream-qwen35-9b")
    ap.add_argument("--workers", type=int, default=24)
    args = ap.parse_args()
    try:
        from dotenv import load_dotenv

        load_dotenv(Path.cwd() / ".env")
    except ImportError:
        pass
    llm = CachedLLM(make_llm(args.provider, model=args.model, max_output_tokens=16000, max_calls=5000),
                    Path("data/beliefgraph") / args.run / "raw")
    pool = [x for r in RUNS for x in load_accepted(Path("data/rendered") / r)]
    for k in args.sizes:
        store, comps = merge(random.Random(f"0:{k}").sample(pool, k), seed=0)
        gj = {}
        for c in comps:
            j, _, _ = gold_inputs(c["sv"], c["ev"], c["seed"])
            fwd = {v: key for key, v in c["back"].items()}
            gj.update({fwd[m]: [[fwd[p] for p in s] for s in js] for m, js in j.items()})
        n = len(store["updates"])
        for name in args.variants:
            bg = DecomposedBeliefGraph(llm, workers=args.workers, **VARIANTS[name])
            g = bg.build(step_view(store, 0))
            readings, _ = bg.read_updates(step_view(store, n))
            ext = ExtractionScore()
            ext.add(gj, g.justifications)
            steps = []
            for i in range(1, n + 1):
                v = step_view(store, i)
                applied = {u["id"] for u in v["updates"]}
                P = revise(v, g.justifications, g.reliability, {u: r for u, r in readings.items() if u in applied})
                steps.append(step_score(gold_after(store, comps, i), {m: a for m, a in P.items() if m.startswith("m_")},
                                        touched(store, comps, i)))
            f = steps[-1]
            print(f"K={k} ({len(gj)} memories) {name:15s} graph set-F1 {ext.summary()['justification_set_f1']:.3f}  "
                  f"unsupported {len(g.unsupported):2d}  touched(mean) {sum(s['acc_touched'] for s in steps) / n:.3f}  "
                  f"final all {f['acc_all']:.3f}  stale {f['stale']:.2f}  over {f['over_invalidation']:.3f}", flush=True)
    print("new calls", llm.calls)


if __name__ == "__main__":
    main()
