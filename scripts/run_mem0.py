"""Memory-system baseline: Mem0 (mem0ai 1.0.5, the ADD/UPDATE/DELETE/NONE pipeline of the Mem0
paper, arXiv 2504.19413) on the same stores, updates and gold as scripts/run_stream.py.

Per store, Mem0 gets what BeliefGraph gets: every fact, memory and rule is stored as an existing
Mem0 memory (infer=False, no extraction). Each update then arrives as a new user message
(infer=True): Mem0 extracts facts from it, retrieves the 5 most similar stored memories per fact and
asks the LLM to ADD / UPDATE / DELETE / NONE them. Mapping onto BeliefGraph actions for our stored
memories: DELETE -> withdraw, UPDATE -> recompute, otherwise keep; effects persist across updates.
Mem0 has no 'uncertain'. Same LLM server and the same embedding model (nomic-embed-text-v1.5 via
fastembed) as BeliefGraph; local Qdrant per store; telemetry off.

    uv run --all-extras --all-groups python scripts/run_mem0.py --model gemma-4-12b-it \\
        --base-url https://...modal.direct/v1 --runs long-s300-p0 ... --per-scenario --run long-mem0-gemma-4-12b-it
"""

from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import sys
import tempfile
import time
from pathlib import Path

os.environ.setdefault("MEM0_TELEMETRY", "False")
sys.path.insert(0, str(Path(__file__).parent))
from run_stream import RUNS, pooled, step_score  # noqa: E402

from beliefbench.beliefgraph_eval import load_accepted, load_rendered  # noqa: E402
from beliefbench.schema import Action  # noqa: E402
from beliefbench.stream import gold_after, merge, touched  # noqa: E402


def _init_process(root: str) -> None:
    """Each worker process gets its own Mem0 home (Mem0 keeps a process-wide local Qdrant there)."""
    d = Path(root) / f"mem0home-{os.getpid()}"
    d.mkdir(parents=True, exist_ok=True)
    os.environ["MEM0_DIR"] = str(d)


def wait_for_server(base_url: str, key: str, timeout_s: int = 1200) -> None:
    """Mem0's client does not wait out a cold start: block until the server answers."""
    import requests

    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            if requests.get(f"{base_url}/models", headers={"Authorization": f"Bearer {key}"}, timeout=30).status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(15)
    raise SystemExit(f"server not up after {timeout_s}s: {base_url}")


def mem0_for(store_id: str, args, root: Path):
    from mem0 import Memory

    d = root / store_id
    d.mkdir(parents=True, exist_ok=True)
    config = {
        "llm": {"provider": "vllm", "config": {"model": args.model, "vllm_base_url": args.base_url,
                                               "api_key": os.environ["BELIEFGRAPH_VLLM_KEY"],
                                               "temperature": 0.1, "max_tokens": 2000}},
        "embedder": {"provider": "fastembed", "config": {"model": "nomic-ai/nomic-embed-text-v1.5"}},
        "vector_store": {"provider": "qdrant", "config": {"collection_name": "bg", "path": str(d / "qdrant"),
                                                          "embedding_model_dims": 768, "on_disk": True}},
        "history_db_path": str(d / "history.db"),
    }
    return Memory.from_config(config)


def run_store(plan, args, root: Path, log: Path) -> tuple[str, dict]:
    key, store, comps = plan
    sid = store["scenario"]
    t0 = time.monotonic()
    m = mem0_for(sid, args, root)
    ours = {}  # mem0 id -> our memory id (only stored memories are scored)
    fact_of = {}  # mem0 id -> our fact id (to check whether Mem0 changed the fact an update targets)
    targets = {}
    for c in comps:
        fwd = {v: k for k, v in c["back"].items()}
        targets.update({fwd[u]: fwd[t["target"]] for u, t in c["ev"]["update_targets"].items()})
    for sec in ("evidence", "memories", "policies"):
        for x in store.get(sec, []):
            text = x["text"] if sec != "evidence" else f"{x['text']} (source: {x['source']}, {x['observed']})"
            res = m.add([{"role": "user", "content": text}], user_id="u", infer=False, metadata={"bg_id": x["id"]})
            for r in res.get("results", []):
                if sec == "memories":
                    ours[r["id"]] = x["id"]
                elif sec == "evidence":
                    fact_of[r["id"]] = x["id"]
    actions = {x["id"]: Action.KEEP for x in store["memories"]}
    steps, events_log = [], []
    for n, u in enumerate(store["updates"], start=1):
        msg = f"{u['text']} (source: {u['source']}, {u['observed']})"
        try:
            res = m.add([{"role": "user", "content": msg}], user_id="u", infer=True)
            events = res.get("results", [])
        except Exception as e:  # noqa: BLE001 -- a failed Mem0 call changes nothing
            events = [{"event": "ERROR", "memory": str(e)[:200]}]
        for ev in events:
            mid = ours.get(ev.get("id"))
            if mid and ev.get("event") == "DELETE":
                actions[mid] = Action.WITHDRAW
            elif mid and ev.get("event") == "UPDATE" and actions[mid] is not Action.WITHDRAW:
                actions[mid] = Action.RECOMPUTE
        events_log.append({"update": u["id"], "events": [{k: ev.get(k) for k in ("event", "id", "memory", "previous_memory")}
                                                          for ev in events]})
        changed_facts = {fact_of.get(ev.get("id")) for ev in events if ev.get("event") in ("UPDATE", "DELETE")}
        gold = gold_after(store, comps, n)
        steps.append({"n": n, "Mem0": step_score(gold, dict(actions), touched(store, comps, n)),
                      "target_fact_changed": targets.get(u["id"]) in changed_facts,
                      "memories_touched": sum(1 for ev in events if ours.get(ev.get("id")))})
    with log.open("a") as fh:
        fh.write(json.dumps({"store": sid, "events": events_log}) + "\n")
    try:
        shutil.rmtree(root / sid)
    except OSError:
        pass
    mean = {"Mem0": sum(s["Mem0"]["acc_touched"] for s in steps) / len(steps)}
    print(f"{key}: Mem0 final balanced {steps[-1]['Mem0']['balanced']} ({time.monotonic() - t0:.0f}s)", flush=True)
    return key, {"memories": len(store["memories"]), "facts": len(store["evidence"]), "updates": len(store["updates"]),
                 "mean_acc_touched": mean, "final": {"Mem0": steps[-1]["Mem0"]}, "steps": steps}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--runs", nargs="+", default=None)
    ap.add_argument("--per-scenario", action="store_true")
    ap.add_argument("--sizes", type=int, nargs="+", default=[10, 30])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--store-workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=None, help="first N stores only (smoke test)")
    ap.add_argument("--run", required=True)
    args = ap.parse_args()
    try:
        from dotenv import load_dotenv

        load_dotenv(Path.cwd() / ".env")
    except ImportError:
        pass
    pool = ([x for r in args.runs for x in load_rendered(Path("data/rendered") / r)] if args.runs
            else [x for r in RUNS for x in load_accepted(Path("data/rendered") / r)])
    plans = []
    if args.per_scenario:
        for i, item in enumerate(pool):
            store, comps = merge([item], seed=args.seed)
            store["scenario"] = f"dossier{i:03d}"
            plans.append((f"d{i:03d}", store, comps))
    else:
        for k in args.sizes:
            store, comps = merge(random.Random(f"{args.seed}:{k}").sample(pool, min(k, len(pool))), seed=args.seed)
            plans.append((str(k), store, comps))
    plans = plans[: args.limit] if args.limit else plans
    out = Path("data/beliefgraph") / args.run
    out.mkdir(parents=True, exist_ok=True)
    log = out / "mem0_events.jsonl"
    log.write_text("")
    root = Path(tempfile.mkdtemp(prefix="mem0-"))
    wait_for_server(args.base_url, os.environ["BELIEFGRAPH_VLLM_KEY"])
    results = {"method": "Mem0 (mem0ai 1.0.5)", "model": args.model, "sizes": {}}
    from concurrent.futures import ProcessPoolExecutor
    from functools import partial

    with ProcessPoolExecutor(max_workers=args.store_workers, initializer=_init_process, initargs=(str(root),)) as pool_:
        for key, entry in pool_.map(partial(run_store, args=args, root=root, log=log), plans):
            results["sizes"][key] = entry
            (out / "results.json").write_text(json.dumps(results, indent=1, default=str))
    if args.per_scenario:
        finals = [r["final"]["Mem0"] for r in results["sizes"].values()]
        bal = [f["balanced"] for f in finals if f.get("balanced") is not None]
        results["pooled"] = {"Mem0": {"final_balanced": sum(bal) / len(bal),
                                      "stale": sum(f["stale"] or 0 for f in finals) / len(finals),
                                      "over_invalidation": sum(f["over_invalidation"] or 0 for f in finals) / len(finals)}}
        allsteps = [st for r in results["sizes"].values() for st in r["steps"]]
        results["pooled"]["target_fact_changed"] = sum(st["target_fact_changed"] for st in allsteps) / len(allsteps)
        results["pooled"]["updates_touching_a_stored_memory"] = sum(st["memories_touched"] > 0 for st in allsteps) / len(allsteps)
        print("pooled:", json.dumps(results["pooled"]))
    (out / "results.json").write_text(json.dumps(results, indent=1, default=str))
    shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
