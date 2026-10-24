"""Experiment (#3): pick a memory's rule with a cross-encoder reranker (Qwen3-Reranker-4B on vLLM).

Same 12 candidates as the v0.4 router. The reranker scores (memory, rule) pairs with an
instruction that states the direction (the rule whose outcome IS the memory). Reports how often
the gold rule ranks first: reranker alone, and fused with the embedding ranking (reciprocal
rank fusion). Compare with Gemma-4-12B's routing in scripts/exp_logprob_route.py.

    BG_MODEL=Qwen/Qwen3-Reranker-4B BG_MAX_MODEL_LEN=8192 modal deploy deploy/modal_qwen.py
    uv run --all-extras python scripts/exp_rerank_route.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from run_stream import RUNS  # noqa: E402

from beliefbench.beliefgraph_eval import load_accepted, load_rendered  # noqa: E402
from beliefbench.stream import merge  # noqa: E402
from beliefgraph.retrieve import DenseIndex  # noqa: E402

LONG = ["long-s300-p0", "long-s300-p1", "long-s300-p2", "long-s300-p3", "long-s300-p4"]
# Qwen3-Reranker input format (vLLM scoring example)
PREFIX = ('<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the '
          'Instruct provided. Note that the answer can only be "yes" or "no".<|im_end|>\n<|im_start|>user\n')
SUFFIX = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
INSTRUCTIONS = {
    "direction": ("The query is a conclusion an assistant stored. Does the document (a rule) produce exactly this "
                  "conclusion as its outcome? A rule that only requires this conclusion, or that grants one of its "
                  "preconditions, does not."),
    "plain": "Given a stored conclusion, retrieve the rule that produced it.",
}


def stores():
    pool = [x for r in RUNS for x in load_accepted(Path("data/rendered") / r)]
    store, comps = merge(random.Random("0:30").sample(pool, 30), seed=0)
    yield "143-memory store", [(store, comps)]
    ds = []
    for i, item in enumerate(x for r in LONG for x in load_rendered(Path("data/rendered") / r)):
        s, c = merge([item], seed=0)
        ds.append((s, c))
    yield "36 long dossiers", ds


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3-reranker-4b")
    ap.add_argument("--base-url", default="https://<workspace>--beliefgraph-qwen3-reranker-4b-server.us-east.modal.direct")
    ap.add_argument("--k", type=int, default=12)
    args = ap.parse_args()
    import requests
    from dotenv import load_dotenv

    load_dotenv(Path.cwd() / ".env")
    headers = {"Authorization": f"Bearer {os.environ['BELIEFGRAPH_VLLM_KEY']}"}
    cache = Path("data/beliefgraph/exp-rerank-route") / args.model
    cache.mkdir(parents=True, exist_ok=True)

    def score(instr: str, query: str, docs: list[str]) -> list[float]:
        q = f"{PREFIX}<Instruct>: {instr}\n<Query>: {query}\n"
        ds = [f"<Document>: {d}{SUFFIX}" for d in docs]
        f = cache / (hashlib.sha256(json.dumps([q, ds]).encode()).hexdigest()[:16] + ".json")
        if f.exists():
            return json.loads(f.read_text())
        for attempt in range(60):  # wait out a cold start
            r = requests.post(f"{args.base_url}/score", headers=headers, timeout=300,
                              json={"model": args.model, "text_1": q, "text_2": ds})
            if r.status_code == 200:
                break
            time.sleep(15)
        r.raise_for_status()
        out = [d["score"] for d in sorted(r.json()["data"], key=lambda d: d["index"])]
        f.write_text(json.dumps(out))
        return out

    for name, group in stores():
        jobs = []
        for store, comps in group:
            pol_of = {}
            for c in comps:
                fwd = {v: k for k, v in c["back"].items()}
                pol_of.update({fwd[m]: fwd[p] for p, m in c["ev"]["policy_of"].items()})
            pols = {p["id"]: p["text"] for p in store["policies"]}
            pidx = DenseIndex(list(pols.items()))
            for m in store["memories"]:
                if m["id"] in pol_of:
                    cands = pidx.rank(m["text"])[: args.k]
                    jobs.append((m["text"], cands, [pols[p] for p in cands], pol_of[m["id"]]))
        for key, instr in INSTRUCTIONS.items():
            with ThreadPoolExecutor(16) as pool:
                scores = list(pool.map(lambda j: score(instr, j[0], j[2]), jobs))
            emb = rr = fused = 0
            for (_, cands, _, gold), sc in zip(jobs, scores):
                order = sorted(range(len(cands)), key=lambda i: -sc[i])
                rr += cands[order[0]] == gold
                emb += cands[0] == gold
                f = {cands[i]: 1 / (10 + i) + 1 / (10 + order.index(i)) for i in range(len(cands))}
                fused += max(f, key=f.get) == gold
            n = len(jobs)
            print(f"{name} [{key} instruction]: {n} memories | right rule first: embedding {emb / n:.3f}, "
                  f"reranker {rr / n:.3f}, reranker+embedding {fused / n:.3f}", flush=True)


if __name__ == "__main__":
    main()
