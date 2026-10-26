"""Memory-system baseline: Graphiti (graphiti-core 0.31.2; Zep's temporal knowledge graph) on the
same stores, updates and gold as scripts/run_stream.py.

Per store (embedded FalkorDB Lite database; the Kuzu backend of graphiti-core 0.31.2 cannot
store edges: its edge search expects a full-text index its own schema never creates), every fact, stored memory and rule is ingested as an episode
in time order; Graphiti's LLM extracts entities and fact edges from each. Each update is then
ingested as a new episode; Graphiti invalidates edges it contradicts (invalid_at / expired_at).
Mapping onto BeliefGraph actions: a stored memory is 'withdraw' once any edge extracted from its
episode has been invalidated, else 'keep' (Graphiti has no recompute or uncertain). Same Gemma
server (OpenAI-compatible) and the same embedding model (nomic-embed-text-v1.5 via fastembed);
retrieval order is kept (no-op reranker); telemetry off.

    uv run --all-extras --all-groups python scripts/run_graphiti.py --model gemma-4-12b-it \\
        --base-url https://...modal.direct/v1 --runs long-s300-p0 ... --per-scenario --run long-graphiti-gemma-4-12b-it
"""

from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import json
import os
import shutil
import sys
import tempfile
import time
from functools import partial
from pathlib import Path

os.environ.setdefault("GRAPHITI_TELEMETRY_ENABLED", "false")
sys.path.insert(0, str(Path(__file__).parent))
from run_mem0 import wait_for_server  # noqa: E402
from run_stream import RUNS, step_score  # noqa: E402

from beliefbench.beliefgraph_eval import load_accepted, load_rendered  # noqa: E402
from beliefbench.schema import Action  # noqa: E402
from beliefbench.stream import gold_after, merge, touched  # noqa: E402


def _clients(args):
    from graphiti_core.cross_encoder.client import CrossEncoderClient
    from graphiti_core.embedder.client import EmbedderClient
    from graphiti_core.llm_client.config import LLMConfig
    from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient

    from beliefgraph.retrieve import DenseIndex

    class FastEmbedder(EmbedderClient):
        """The embedding model BeliefGraph uses (nomic-embed-text-v1.5, local)."""

        def __init__(self):
            self.idx = DenseIndex([("x", "x")])

        async def create(self, input_data):
            text = input_data if isinstance(input_data, str) else " ".join(map(str, input_data))
            return self.idx._embed([text])[0].tolist()

        async def create_batch(self, input_data_list):
            return [v.tolist() for v in self.idx._embed(list(input_data_list))]

    class KeepOrder(CrossEncoderClient):
        async def rank(self, query, passages):
            return [(p, 1.0 - i / max(1, len(passages))) for i, p in enumerate(passages)]

    llm = OpenAIGenericClient(config=LLMConfig(api_key=os.environ["BELIEFGRAPH_VLLM_KEY"], model=args.model,
                                               small_model=args.model, base_url=args.base_url, temperature=0.1))
    return llm, FastEmbedder(), KeepOrder()


async def _run_store(plan, args, root: Path) -> tuple[str, dict]:
    from graphiti_core import Graphiti
    from graphiti_core.driver.falkordb_driver import FalkorDriver
    from graphiti_core.edges import EntityEdge
    from redislite.async_falkordb_client import AsyncFalkorDB
    from graphiti_core.nodes import EpisodeType

    key, store, comps = plan
    sid = store["scenario"]
    t0 = time.monotonic()
    llm, emb, rr = _clients(args)
    from graphiti_core.helpers import get_default_group_id

    driver = FalkorDriver(falkor_db=AsyncFalkorDB(str(root / f"{sid}.falkor.db")))
    g = Graphiti(graph_driver=driver, llm_client=llm, embedder=emb, cross_encoder=rr)
    await g.build_indices_and_constraints()
    gid = get_default_group_id(driver.provider)  # one embedded database per store: the default group
    when = lambda s: dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc)
    latest = max(when(e["observed"]) for e in store["evidence"])
    mem_episode = {}  # episode uuid -> our memory id
    errors = 0
    items = ([("fact", e, when(e["observed"])) for e in store["evidence"]] +
             [("memory", m, latest + dt.timedelta(hours=1)) for m in store["memories"]] +
             [("rule", p, latest + dt.timedelta(hours=1)) for p in store.get("policies", [])])
    items.sort(key=lambda x: x[2])
    for kind, x, t in items:
        body = x["text"] if kind != "fact" else f"{x['text']} (source: {x['source']})"
        try:
            res = await g.add_episode(name=f"{kind} {x['id']}", episode_body=body, source=EpisodeType.text,
                                      source_description=kind if kind != "fact" else x["source"], reference_time=t)
            if kind == "memory":
                mem_episode[res.episode.uuid] = x["id"]
        except Exception:  # noqa: BLE001 -- a failed ingestion leaves the item out of the graph
            errors += 1
    actions = {m["id"]: Action.KEEP for m in store["memories"]}
    steps = []
    for n, u in enumerate(store["updates"], start=1):
        try:
            await g.add_episode(name=f"update {u['id']}", episode_body=f"{u['text']} (source: {u['source']})",
                                source=EpisodeType.text, source_description=u["source"],
                                reference_time=when(u["observed"]))
        except Exception:  # noqa: BLE001
            errors += 1
        try:
            edges = await EntityEdge.get_by_group_ids(driver, [gid])
        except Exception:  # noqa: BLE001 -- includes 'no edges found'
            edges = []
        n_edges = len(edges)
        n_invalid = sum(e.invalid_at is not None or e.expired_at is not None for e in edges)
        n_mem_edges = sum(any(ep in mem_episode for ep in (e.episodes or [])) for e in edges)
        for e in edges:
            if e.invalid_at is not None or e.expired_at is not None:
                for ep in e.episodes or []:
                    if ep in mem_episode:
                        actions[mem_episode[ep]] = Action.WITHDRAW
        gold = gold_after(store, comps, n)
        steps.append({"n": n, "Graphiti": step_score(gold, dict(actions), touched(store, comps, n)),
                      "edges": n_edges, "invalidated_edges": n_invalid, "edges_from_memories": n_mem_edges})
    try:
        await g.close()
    except Exception:  # noqa: BLE001
        pass
    print(f"{key}: Graphiti final balanced {steps[-1]['Graphiti']['balanced']} ({time.monotonic() - t0:.0f}s, "
          f"{errors} failed episodes; edges {steps[-1]['edges']}, from memories {steps[-1]['edges_from_memories']}, "
          f"invalidated {steps[-1]['invalidated_edges']})", flush=True)
    return key, {"memories": len(store["memories"]), "updates": len(store["updates"]), "failed_episodes": errors,
                 "mean_acc_touched": {"Graphiti": sum(s["Graphiti"]["acc_touched"] for s in steps) / len(steps)},
                 "final": {"Graphiti": steps[-1]["Graphiti"]}, "steps": steps}


def run_store(plan, args, root: Path):
    return asyncio.run(_run_store(plan, args, root))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--runs", nargs="+", default=None)
    ap.add_argument("--per-scenario", action="store_true")
    ap.add_argument("--store-workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--run", required=True)
    args = ap.parse_args()
    from dotenv import load_dotenv

    load_dotenv(Path.cwd() / ".env")
    pool = ([x for r in args.runs for x in load_rendered(Path("data/rendered") / r)] if args.runs
            else [x for r in RUNS for x in load_accepted(Path("data/rendered") / r)])
    plans = []
    for i, item in enumerate(pool):
        store, comps = merge([item], seed=args.seed)
        store["scenario"] = f"dossier{i:03d}"
        plans.append((f"d{i:03d}", store, comps))
    plans = plans[: args.limit] if args.limit else plans
    out = Path("data/beliefgraph") / args.run
    out.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="graphiti-"))
    wait_for_server(args.base_url, os.environ["BELIEFGRAPH_VLLM_KEY"])
    from concurrent.futures import ProcessPoolExecutor

    results = {"method": "Graphiti (graphiti-core 0.31.2, FalkorDB Lite)", "model": args.model, "sizes": {}}
    prev = out / "results.json"
    if prev.exists():  # resume: keep finished stores (these runners have no call cache)
        done = json.loads(prev.read_text()).get("sizes", {})
        results["sizes"].update(done)
        plans = [p for p in plans if p[0] not in done]
        print(f"resuming: {len(done)} stores already done, {len(plans)} to run", flush=True)
    with ProcessPoolExecutor(max_workers=args.store_workers) as pool_:
        for key, entry in pool_.map(partial(run_store, args=args, root=root), plans):
            results["sizes"][key] = entry
            (out / "results.json").write_text(json.dumps(results, indent=1, default=str))
    finals = [r["final"]["Graphiti"] for r in results["sizes"].values()]
    bal = [f["balanced"] for f in finals if f.get("balanced") is not None]
    results["pooled"] = {"Graphiti": {"final_balanced": sum(bal) / len(bal),
                                      "stale": sum(f["stale"] or 0 for f in finals) / len(finals),
                                      "over_invalidation": sum(f["over_invalidation"] or 0 for f in finals) / len(finals)},
                         "failed_episodes": sum(r["failed_episodes"] for r in results["sizes"].values())}
    print("pooled:", json.dumps(results["pooled"]))
    (out / "results.json").write_text(json.dumps(results, indent=1, default=str))
    shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
