"""Quick check on the hard subset of the 143-memory store: whole scenarios where v0.2.1
(thinking, 1 sample) has a graph error, plus 4 clean ones (93 memories). Prints how many
memories get the gold graph, and fixes / breaks against v0.2.1.

    uv run --all-extras python scripts/eval_subset.py --provider modal --thinking off --samples 1
"""

from __future__ import annotations

import argparse
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from run_stream import RUNS  # noqa: E402

from beliefbench.beliefgraph_eval import gold_inputs, load_accepted  # noqa: E402
from beliefbench.stream import merge, step_view  # noqa: E402
from beliefgraph.cache import CachedLLM  # noqa: E402
from beliefgraph.core import DecomposedBeliefGraph  # noqa: E402
from beliefgraph.llm import make_llm  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="modal")
    ap.add_argument("--model", default="qwen3.5-9b")
    ap.add_argument("--thinking", default="on", choices=["on", "off"])
    ap.add_argument("--samples", type=int, default=1)
    ap.add_argument("--adjudicate", action="store_true")
    ap.add_argument("--all", action="store_true", help="every memory of the store, not the hard subset")
    args = ap.parse_args()
    try:
        from dotenv import load_dotenv

        load_dotenv(Path.cwd() / ".env")
    except ImportError:
        pass
    raw = Path("data/beliefgraph/stream-qwen35-9b/raw")
    base_llm = CachedLLM(make_llm("modal", model="qwen3.5-9b", max_output_tokens=16000, max_calls=0), raw)
    llm = CachedLLM(make_llm(args.provider, model=args.model, max_output_tokens=16000, max_calls=5000,
                             thinking=None if args.thinking == "on" else False), raw)
    pool = [x for r in RUNS for x in load_accepted(Path("data/rendered") / r)]
    store, comps = merge(random.Random("0:30").sample(pool, 30), seed=0)
    view = step_view(store, 0)
    gj, comp_of = {}, {}
    for c in comps:
        j, _, _ = gold_inputs(c["sv"], c["ev"], c["seed"])
        fwd = {v: k for k, v in c["back"].items()}
        for m, js in j.items():
            gj[fwd[m]] = sorted(sorted(fwd[p] for p in s) for s in js)
            comp_of[fwd[m]] = c["k"]

    def ok(g, m):
        return sorted(sorted(s) for s in g.justifications.get(m, [])) == gj[m]

    base = DecomposedBeliefGraph(base_llm, workers=8, samples=1, adjudicate=False).build(view)  # cached
    bad = {comp_of[m] for m in gj if not ok(base, m)}
    picked = bad | set(random.Random(1).sample(sorted(set(comp_of.values()) - bad), 4))
    sub = list(gj) if args.all else [m for m in gj if comp_of[m] in picked]
    t = time.time()
    g = DecomposedBeliefGraph(llm, workers=32, samples=args.samples, adjudicate=args.adjudicate).build(view, only=sub)
    print(f"{args.provider}/{args.model} thinking={args.thinking} samples={args.samples} adjudicate={args.adjudicate}: "
          f"correct {sum(ok(g, m) for m in sub)}/{len(sub)} (v0.2.1 {sum(ok(base, m) for m in sub)}), "
          f"fixed {sum(ok(g, m) and not ok(base, m) for m in sub)}, broke {sum(ok(base, m) and not ok(g, m) for m in sub)}, "
          f"unsupported {sum(not g.justifications.get(m) for m in sub)}; {time.time() - t:.0f}s, {llm.calls} new calls",
          flush=True)


if __name__ == "__main__":
    main()
