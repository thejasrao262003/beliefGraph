"""Run BeliefGraph on the accepted benchmark scenarios and score it.

    uv run python scripts/run_beliefgraph.py --dry-run
    uv run --group lyzr python scripts/run_beliefgraph.py --provider lyzr --model anthropic/claude-opus-5-5 \
        --budget-usd 3 --run bg-opus55-v1 [--limit 10]

Every LLM response is cached under data/beliefgraph/<run>/raw/ (keyed by prompt version,
model and input), so a rerun never re-bills. Results: data/beliefgraph/<run>/results.json.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from beliefbench.beliefgraph_eval import load_accepted, score
from beliefbench.llm_baselines import DIRECT_VERSION, llm_direct
from beliefgraph.cache import CachedLLM
from beliefgraph.core import BeliefGraph
from beliefgraph.llm import PROVIDERS, make_llm
from beliefgraph.prompts import BUILD_VERSION, READ_VERSION

RUNS = ["pilot40-render-v10", "validate-v11", "validate-v11-f3-retry", "validate-v12"]


def cost_by_method(raw_dir: Path, opaque_ids: set[str]) -> dict:
    """Tokens and estimated dollars per method, from every cached call (new or reused) of the
    scenarios in this run: BeliefGraph = build + retry + read; LLM-direct = direct."""
    out = {"BeliefGraph": {"calls": 0, "input_tokens": 0, "output_tokens": 0, "est_usd": 0.0},
           "LLM-direct": {"calls": 0, "input_tokens": 0, "output_tokens": 0, "est_usd": 0.0}}
    for f in raw_dir.glob("*.json"):
        rec = json.loads(f.read_text())
        sid, _, stage = rec["note"].partition(" ")
        if sid not in opaque_ids:
            continue
        m = out["LLM-direct" if stage == "direct" else "BeliefGraph"]
        u = rec.get("usage") or {}
        m["calls"] += 1
        m["input_tokens"] += u.get("input_tokens") or 0
        m["output_tokens"] += u.get("output_tokens") or 0
        m["est_usd"] += u.get("est_usd") or 0.0
    for m in out.values():
        m["est_usd"] = round(m["est_usd"], 4)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="lyzr", choices=PROVIDERS)
    ap.add_argument("--model", default=None)
    ap.add_argument("--base-url", default=None)
    ap.add_argument("--run", default="bg-run")
    ap.add_argument("--budget-usd", type=float, default=3.0)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--runs", nargs="+", default=RUNS, help="rendered runs to evaluate on")
    ap.add_argument("--no-direct", action="store_true", help="skip the LLM-direct baseline (1 extra call each)")
    ap.add_argument("--workers", type=int, default=1, help="scenarios in parallel (not for lyzr: its guard is serial)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = [x for r in args.runs for x in load_accepted(Path("data/rendered") / r)]
    data = data[: args.limit] if args.limit else data
    print(f"{len(data)} accepted scenarios from {args.runs}; {2 if args.no_direct else 3} LLM calls each "
          f"(build, read{'' if args.no_direct else ', LLM-direct baseline'})")
    if args.dry_run:
        return
    out = Path("data/beliefgraph") / args.run
    (out / "raw").mkdir(parents=True, exist_ok=True)
    try:  # keys and URLs (LYZR_API_KEY, BELIEFGRAPH_VLLM_KEY / _URL, ...) from the git-ignored .env
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass
    if args.provider == "lyzr" and args.workers > 1:
        raise SystemExit("--workers > 1 is not supported for lyzr (its spend guard is serial)")
    llm = make_llm(args.provider, model=args.model, base_url=args.base_url, budget_usd=args.budget_usd,
                   max_calls=4 * len(data) + 10)  # build, retry, read, direct
    cached = CachedLLM(llm, out / "raw")
    bg = BeliefGraph(cached)
    items, failures = [], {}

    def one(sv, ev, seed):
        graph = bg.build(sv)
        readings, rerr = bg.read_updates(sv)
        direct, derr = (None, []) if args.no_direct else llm_direct(cached, sv)
        return {"sv": sv, "ev": ev, "seed": seed, "graph": asdict(graph), "readings": readings,
                "direct": direct, "errors": graph.errors + rerr + derr}

    try:
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [(f"{ev['source_scenario']}@{seed}", pool.submit(one, sv, ev, seed)) for sv, ev, seed in data]
            for name, fut in futures:
                try:
                    it = fut.result()
                except Exception as e:  # noqa: BLE001 -- budget refusals and provider errors end this scenario
                    failures[name] = f"{type(e).__name__}: {str(e)[:200]}"
                    print(f"FAIL {name}: {failures[name]}")
                    continue
                items.append(it)
                print(f"ok {name} ({len(it['errors'])} parse notes)")
    finally:
        if hasattr(llm, "close"):
            llm.close()
    result = score(items) | {"cost_by_method": cost_by_method(out / "raw", {it["sv"]["scenario"] for it in items}),"provider": args.provider, "model": llm.model, "build_prompt": BUILD_VERSION,
                             "read_prompt": READ_VERSION, "direct_prompt": DIRECT_VERSION, "failures": failures, "new_calls": cached.calls,
                             "usage": llm.usage}
    if args.provider == "lyzr":
        result["est_usd_conservative"] = round(llm.client["guard"].spent_usd, 4)
    (out / "results.json").write_text(json.dumps(result, indent=1, default=str))
    (out / "predictions.json").write_text(json.dumps(
        [{"scenario": f"{it['ev']['source_scenario']}@{it['seed']}", "opaque": it["sv"]["scenario"],
          "graph": it["graph"], "readings": {k: asdict(v) for k, v in it["readings"].items()},
          "direct": {k: v.value for k, v in (it["direct"] or {}).items()},
          "errors": it["errors"]} for it in items], indent=1))
    show = {k: result[k] for k in ("scenarios", "graph_extraction", "update_reading_exact",
                                   "source_reliability_accuracy", "unsupported_memories", "failures",
                                   "paired_P_vs_LLM_direct", "cost_by_method")}
    print(json.dumps(show, indent=1, default=str))
    for k, v in result["revision"].items():
        if v["n"]:
            print(f"{k:18s} acc {v['accuracy']:.3f}  macro-F1 {v['macro_f1']:.3f}  stale {v['stale_rate']}  "
                  f"over-inval {v['over_invalidation_rate']}")
    if "est_usd_conservative" in result:
        print("spent ≈ $", result["est_usd_conservative"])


if __name__ == "__main__":
    main()
