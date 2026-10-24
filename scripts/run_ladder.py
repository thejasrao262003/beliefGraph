"""Run one dataset on every ~10B model of the ladder (in parallel, one Modal server each) and
print a balanced-accuracy table: BeliefGraph v0.4 vs the same model given the whole store.

    uv run --all-extras python scripts/run_ladder.py --tag long-s300 -- --runs long-s300-p0 long-s300-p1 \\
        long-s300-p2 --per-scenario

Everything after ``--`` is passed to scripts/run_stream.py. Results: data/beliefgraph/<tag>-<model>/.
Servers: deploy/modal_qwen.py (BG_MODEL=<hf id>), one app per model.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ACCOUNT = "<workspace>"
# served model name -> (Modal app slug, thinking flag)
LADDER = {
    "gemma-4-12b-it": ("gemma-4-12b-it", "default"),
    "qwen3.5-9b": ("qwen35-9b", "off"),
    "granite-4.1-8b": ("granite-4-1-8b", "default"),
    "meta-llama-3.1-8b": ("meta-llama-3-1-8b", "default"),
    "ministral-3-8b-2512": ("ministral-3-8b-2512", "default"),
    "olmo-3-7b": ("olmo-3-7b", "default"),
}


def url(app: str) -> str:
    return f"https://{ACCOUNT}--beliefgraph-{app}-server.us-east.modal.direct/v1"


def run(model: str, tag: str, extra: list[str], log_dir: Path) -> int:
    app, thinking = LADDER[model]
    cmd = [sys.executable, "scripts/run_stream.py", "--provider", "modal", "--model", model, "--base-url", url(app),
           "--algo", "v0.2", "--workers", "32", "--thinking", thinking, "--max-output-tokens", "4000",
           "--run", f"{tag}-{model}", *extra]
    with (log_dir / f"{tag}-{model}.log").open("w") as log:
        return subprocess.call(cmd, stdout=log, stderr=subprocess.STDOUT)


def balanced(x: dict) -> float:
    return (2 - (x["stale"] or 0) - (x["over_invalidation"] or 0)) / 2


def table(tag: str, models: list[str]) -> None:
    print(f"{'model':22s} {'store':>6s} | {'BG bal':>6s} {'stale':>5s} {'over':>5s} | {'direct bal':>10s} {'stale':>5s} {'over':>5s}")
    for m in models:
        f = Path(f"data/beliefgraph/{tag}-{m}/results.json")
        if not f.exists():
            print(f"{m:22s} (no results)")
            continue
        r = json.loads(f.read_text())
        if "pooled" in r:
            p = r["pooled"]
            bg, d = p["BeliefGraph"], p["LLM-direct"]
            print(f"{m:22s} {'pooled':>6s} | {bg['final_balanced']:6.3f} {bg['stale']:5.2f} {bg['over_invalidation']:5.2f} | "
                  f"{d['final_balanced']:10.3f} {d['stale']:5.2f} {d['over_invalidation']:5.2f}   "
                  f"(step-mean balanced {bg['mean_step_balanced']:.3f} vs {d['mean_step_balanced']:.3f}; {len(r['sizes'])} stores)")
            continue
        for k, s in r["sizes"].items():
            bg, d = s["final"]["BeliefGraph"], s["final"]["LLM-direct"]
            print(f"{m:22s} {s['memories']:6d} | {balanced(bg):6.3f} {bg['stale']:5.2f} {bg['over_invalidation']:5.2f} | "
                  f"{balanced(d):10.3f} {d['stale']:5.2f} {d['over_invalidation']:5.2f}")


def main() -> None:
    argv = sys.argv[1:]
    extra = argv[argv.index("--") + 1 :] if "--" in argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--models", nargs="+", default=list(LADDER), choices=list(LADDER))
    ap.add_argument("--table-only", action="store_true")
    args = ap.parse_args(argv[: argv.index("--")] if "--" in argv else argv)
    if not args.table_only:
        log_dir = Path("data/beliefgraph/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        with ThreadPoolExecutor(len(args.models)) as pool:
            codes = dict(zip(args.models, pool.map(lambda m: run(m, args.tag, extra, log_dir), args.models)))
        print("exit codes:", codes)
    table(args.tag, args.models)


if __name__ == "__main__":
    main()
