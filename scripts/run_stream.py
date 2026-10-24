"""Large memory stores with sequential updates: BeliefGraph vs LLM-direct, same model.

    uv run python scripts/run_stream.py --sizes 10 30 63 --dry-run
    uv run --all-extras python scripts/run_stream.py --provider modal --model qwen3.5-9b --run stream-qwen35-9b
    uv run --all-extras --group lyzr python scripts/run_stream.py --provider lyzr --model anthropic/claude-haiku-5-5 \
        --budget-usd 2 --run stream-haiku55

For each store size K, K accepted scenarios (seeded sample) are merged into one store and
their updates arrive one at a time. BeliefGraph builds its graph once (in batches), then
makes one call per update to read it and revises by propagation. LLM-direct re-reads the
whole store at every update and names the memories that change. Both are scored after
every update against exact gold. Calls are cached under data/beliefgraph/<run>/raw/.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path

from beliefbench.beliefgraph_eval import load_accepted, load_rendered
from beliefbench.llm_baselines import DIRECT_STORE_VERSION, llm_direct_store, llm_rag_store
from beliefbench.schema import Action
from beliefbench.stream import gold_after, merge, step_view, touched
from beliefgraph.cache import CachedLLM
from beliefgraph.core import BeliefGraph, DecomposedBeliefGraph, revise
from beliefgraph.llm import PROVIDERS, make_llm
from beliefgraph.prompts import BUILD_VERSION, READ_VERSION

RUNS = ["pilot40-render-v10", "validate-v11", "validate-v11-f3-retry", "validate-v12"]
REVISING = {Action.WITHDRAW, Action.RECOMPUTE, Action.SUPERSEDE, Action.UNCERTAIN}


def step_score(gold: dict, pred: dict, focus: set[str]) -> dict:
    def acc(ids):
        ids = list(ids)
        return sum(pred.get(m, Action.KEEP) is gold[m] for m in ids) / len(ids) if ids else None
    revising = [m for m in gold if gold[m] in REVISING]
    keep = [m for m in gold if gold[m] is Action.KEEP]
    rev_recall = sum(pred.get(m, Action.KEEP) is not Action.KEEP for m in revising) / len(revising) if revising else None
    keep_recall = sum(pred.get(m, Action.KEEP) is Action.KEEP for m in keep) / len(keep) if keep else None
    return {"acc_all": acc(gold), "acc_touched": acc(focus & set(gold)),
            "balanced": (rev_recall + keep_recall) / 2 if revising and keep else None,
            "stale": sum(pred.get(m, Action.KEEP) is Action.KEEP for m in revising) / len(revising) if revising else None,
            "over_invalidation": sum(pred.get(m, Action.KEEP) is not Action.KEEP for m in keep) / len(keep) if keep else None,
            "n_revising": len(revising)}


def pooled(sizes: dict) -> dict:
    """Per-scenario runs: means over dossiers of the final-step and step-averaged scores."""
    out = {}
    for m in ("BeliefGraph", "LLM-direct", "LLM-RAG"):
        if not all(m in r["final"] for r in sizes.values()):
            continue
        finals = [r["final"][m] for r in sizes.values()]
        bal = [f["balanced"] for f in finals if f.get("balanced") is not None]
        out[m] = {"final_acc": sum(f["acc_all"] for f in finals) / len(finals),
                  "final_balanced": sum(bal) / len(bal) if bal else None,
                  "mean_step_balanced": sum(
                      sum(s[m]["balanced"] for s in r["steps"] if s[m]["balanced"] is not None)
                      / max(1, sum(s[m]["balanced"] is not None for s in r["steps"])) for r in sizes.values()) / len(sizes),
                  "stale": sum(f["stale"] or 0 for f in finals) / len(finals),
                  "over_invalidation": sum(f["over_invalidation"] or 0 for f in finals) / len(finals)}
    return out


def usage_of(raw_dir: Path, store_id: str) -> dict:
    out = {m: Counter() for m in ("BeliefGraph-build", "BeliefGraph-read", "LLM-direct", "LLM-RAG")}
    for f in raw_dir.glob(f"{store_id}.*.json"):
        rec = json.loads(f.read_text())
        stage = rec["note"].split(" ", 1)[1]
        m = "LLM-direct" if stage.startswith("direct") else "LLM-RAG" if stage.startswith("rag") \
            else "BeliefGraph-read" if stage.startswith("read") else "BeliefGraph-build"
        u = rec.get("usage") or {}
        out[m].update({"calls": 1, "input_tokens": u.get("input_tokens") or 0,
                       "output_tokens": u.get("output_tokens") or 0, "seconds": u.get("seconds") or 0,
                       "est_usd": u.get("est_usd") or 0})
    return {k: dict(v) for k, v in out.items()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="lyzr", choices=PROVIDERS)
    ap.add_argument("--model", default=None)
    ap.add_argument("--base-url", default=None)
    ap.add_argument("--sizes", type=int, nargs="+", default=[10, 30, 63])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--batch-size", type=int, default=25, help="memories per graph-building call")
    ap.add_argument("--run", default="stream-run")
    ap.add_argument("--budget-usd", type=float, default=2.0, help="hard cap (lyzr provider)")
    ap.add_argument("--workers", type=int, default=1, help="parallel calls (not for lyzr: its guard is serial)")
    ap.add_argument("--algo", default="v0.1", choices=["v0.1", "v0.2"],
                    help="v0.1: one graph-building call per store or batch; v0.2: policy-anchored decomposition")
    ap.add_argument("--max-output-tokens", type=int, default=16000)
    ap.add_argument("--json-mode", action="store_true", help="constrain answers to valid JSON (OpenAI-compatible servers)")
    ap.add_argument("--thinking", default="default", choices=["default", "on", "off"],
                    help="self-hosted Qwen-style models: force thinking on/off (same for every method)")
    ap.add_argument("--runs", nargs="+", default=None, help="rendered runs (default: the accepted pilot runs)")
    ap.add_argument("--store-workers", type=int, default=6, help="--per-scenario: stores processed concurrently")
    ap.add_argument("--rag", action="store_true", help="also run the retrieval (RAG) baseline")
    ap.add_argument("--per-scenario", action="store_true",
                    help="each scenario is its own store (long dossiers); results are pooled over scenarios")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    pool = ([x for r in args.runs for x in load_rendered(Path("data/rendered") / r)] if args.runs
            else [x for r in RUNS for x in load_accepted(Path("data/rendered") / r)])
    plans = []
    if args.per_scenario:
        for i, item in enumerate(pool):
            store, comps = merge([item], seed=args.seed)
            store["scenario"] = f"dossier{i:03d}"
            plans.append((f"d{i:03d}", store, comps))
    for k in ([] if args.per_scenario else args.sizes):
        chosen = random.Random(f"{args.seed}:{k}").sample(pool, min(k, len(pool)))
        store, comps = merge(chosen, seed=args.seed)
        chars = len(json.dumps(store))
        plans.append((k, store, comps))
        n_build = -(-len(store["memories"]) // args.batch_size)
        print(f"K={k}: {len(store['memories'])} memories, {len(store['evidence'])} facts, {len(store['updates'])} updates, "
              f"~{chars // 4:,} tokens; BeliefGraph {n_build} build + {len(store['updates'])} read calls, "
              f"LLM-direct {len(store['updates'])} whole-store calls")
    if args.dry_run:
        return
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass
    if args.provider == "lyzr" and args.workers > 1:
        raise SystemExit("--workers > 1 is not supported for lyzr (its spend guard is serial)")
    out = Path("data/beliefgraph") / args.run
    total_calls = sum(-(-len(s["memories"]) // args.batch_size) * 2 + 2 * len(s["updates"]) for _, s, _ in plans)
    llm = make_llm(args.provider, model=args.model, base_url=args.base_url, budget_usd=args.budget_usd, max_output_tokens=args.max_output_tokens,
                   thinking={"default": None, "on": True, "off": False}[args.thinking], json_mode=args.json_mode,
                   max_calls=total_calls + 20)
    cached = CachedLLM(llm, out / "raw")
    bg = (DecomposedBeliefGraph(cached, workers=max(1, args.workers)) if args.algo == "v0.2"
          else BeliefGraph(cached))
    results = {"algo": args.algo, "max_output_tokens": args.max_output_tokens, "provider": args.provider, "model": llm.model, "prompts": [BUILD_VERSION, READ_VERSION, DIRECT_STORE_VERSION],
               "seed": args.seed, "batch_size": args.batch_size, "sizes": {}}
    def one_store(plan):
        k, store, comps = plan
        sid = store["scenario"]
        graph = bg.build(step_view(store, 0), batch_size=args.batch_size)
        n_up = len(store["updates"])
        # Every per-update call is independent of the others (BeliefGraph reads one update;
        # LLM-direct sees the store after n updates), so they can run concurrently.
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            reads = [pool.submit(bg.read_updates, step_view(store, n, only_last=True) | {"scenario": sid})
                     for n in range(1, n_up + 1)]
            directs = [pool.submit(llm_direct_store, cached, step_view(store, n), f"{sid} direct{n}")
                       for n in range(1, n_up + 1)]
            rags = [pool.submit(llm_rag_store, cached, step_view(store, n), f"{sid} rag{n}")
                    for n in range(1, n_up + 1)] if args.rag else []
            reads = [f.result() for f in reads]
            directs = [f.result() for f in directs]
            rags = [f.result() for f in rags]
        readings, steps = {}, []
        for n in range(1, n_up + 1):
            r, rerr = reads[n - 1]
            readings.update(r)
            p_actions = revise(step_view(store, n), graph.justifications, graph.reliability, readings)
            d_actions, derr = directs[n - 1]
            gold = gold_after(store, comps, n)
            focus = touched(store, comps, n)
            steps.append({"n": n, "BeliefGraph": step_score(gold, p_actions, focus),
                          "LLM-direct": step_score(gold, d_actions, focus), "errors": rerr + derr})
            if rags:
                steps[-1]["LLM-RAG"] = step_score(gold, rags[n - 1][0], focus)
            print(f"K={k} step {n}/{len(store['updates'])}: BG {steps[-1]['BeliefGraph']['acc_touched']:.3f} "
                  f"direct {steps[-1]['LLM-direct']['acc_touched']:.3f} (touched)", flush=True)
        methods = [m for m in ("BeliefGraph", "LLM-direct", "LLM-RAG") if m in steps[-1]]
        mean = {m: sum(s[m]["acc_touched"] for s in steps) / len(steps) for m in methods}
        return str(k), {
            "memories": len(store["memories"]), "facts": len(store["evidence"]), "updates": len(store["updates"]),
            "graph_unsupported": len(graph.unsupported), "mean_acc_touched": mean,
            "final": {m: steps[-1][m] for m in methods},
            "usage": usage_of(out / "raw", sid), "steps": steps}

    try:
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=args.store_workers if args.per_scenario else 1) as stores:
            for key, entry in stores.map(one_store, plans):
                results["sizes"][key] = entry
                (out / "results.json").write_text(json.dumps(results, indent=1, default=str))
    finally:
        if hasattr(llm, "close"):
            llm.close()
    if args.per_scenario and results["sizes"]:
        results["pooled"] = pooled(results["sizes"])
        print("pooled over", len(results["sizes"]), "dossiers:", json.dumps(results["pooled"]))
    if args.provider == "lyzr":
        results["est_usd_conservative"] = round(llm.client["guard"].spent_usd, 4)
    (out / "results.json").write_text(json.dumps(results, indent=1, default=str))
    for k, r in results["sizes"].items():
        print(f"K={k} ({r['memories']} memories, {r['updates']} updates): mean touched-accuracy BG "
              f"{r['mean_acc_touched']['BeliefGraph']:.3f} vs direct {r['mean_acc_touched']['LLM-direct']:.3f}; "
              f"usage {json.dumps(r['usage'])}")


if __name__ == "__main__":
    main()
