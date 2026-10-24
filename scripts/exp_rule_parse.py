"""Experiment (v0.7 #1): parse rules into IF/THEN and route on THEN, with an IF-match penalty.

Embedding-only routing accuracy (no routing LLM call): the rank of each memory's gold rule
among all rules of its store, scored by
  full   cos(memory, rule text)                       (current retrieval)
  then   cos(memory, THEN clause)
  then-L cos(memory, THEN) - L * max cos(memory, IF condition)
The parse itself is one LLM call per rule (cached).

    uv run --all-extras python scripts/exp_rule_parse.py   # baseline model: gemma-4-12b-it
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from run_stream import RUNS  # noqa: E402

from beliefbench.beliefgraph_eval import load_accepted, load_rendered  # noqa: E402
from beliefbench.stream import merge  # noqa: E402
from beliefgraph.cache import CachedLLM  # noqa: E402
from beliefgraph.core import _load_json  # noqa: E402
from beliefgraph.llm import make_llm  # noqa: E402
from beliefgraph.prompts import RULE_PARSE_PROMPT  # noqa: E402
from beliefgraph.retrieve import DenseIndex  # noqa: E402

LONG = ["long-s300-p0", "long-s300-p1", "long-s300-p2", "long-s300-p3", "long-s300-p4"]


def stores():
    pool = [x for r in RUNS for x in load_accepted(Path("data/rendered") / r)]
    store, comps = merge(random.Random("0:30").sample(pool, 30), seed=0)
    yield "143-memory store", [(store, comps)]
    dossiers = []
    for i, item in enumerate(x for r in LONG for x in load_rendered(Path("data/rendered") / r)):
        s, c = merge([item], seed=0)
        s["scenario"] = f"dossier{i:03d}"
        dossiers.append((s, c))
    yield "36 long dossiers", dossiers


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gemma-4-12b-it")
    ap.add_argument("--base-url", default="https://<workspace>--beliefgraph-gemma-4-12b-it-server.us-east.modal.direct/v1")
    ap.add_argument("--thinking", default="default", choices=["default", "on", "off"])
    args = ap.parse_args()
    try:
        from dotenv import load_dotenv

        load_dotenv(Path.cwd() / ".env")
    except ImportError:
        pass
    llm = CachedLLM(make_llm("modal", model=args.model, base_url=args.base_url, max_output_tokens=1500, max_calls=10000,
                             thinking={"default": None, "on": True, "off": False}[args.thinking]),
                    Path("data/beliefgraph/exp-rule-parse") / args.model / "raw")
    from concurrent.futures import ThreadPoolExecutor

    def parse(p):
        try:
            obj = _load_json(llm(RULE_PARSE_PROMPT, p["text"], f"parse.{p['id']}"))
            then = obj.get("then") if isinstance(obj.get("then"), str) and obj["then"].strip() else p["text"]
            conds = [c for g in obj.get("if") or [] if isinstance(g, list) for c in g if isinstance(c, str) and c.strip()]
            return then, conds, True
        except Exception:  # noqa: BLE001
            return p["text"], [], False

    for name, group in stores():
        ranks = {k: [] for k in ("full", "then", "then-0.5", "then-1.0")}
        parsed_ok = n_rules = 0
        for store, comps in group:
            pol_of = {}
            for c in comps:
                fwd = {v: k for k, v in c["back"].items()}
                pol_of.update({fwd[m]: fwd[p] for p, m in c["ev"]["policy_of"].items()})
            pols = store["policies"]
            with ThreadPoolExecutor(32) as pool:
                parses = dict(zip([p["id"] for p in pols], pool.map(parse, pols)))
            parsed_ok += sum(ok for _, _, ok in parses.values())
            n_rules += len(pols)
            ids = [p["id"] for p in pols]
            emb = DenseIndex([("x", "x")])  # shared model; embed directly below
            E = lambda texts: emb._embed(texts) if texts else np.zeros((0, 768))
            full = E([p["text"] for p in pols])
            then = E([parses[i][0] for i in ids])
            cond_texts = [(i, c) for i in ids for c in parses[i][1]]
            C = E([c for _, c in cond_texts])
            mems = [m for m in store["memories"] if m["id"] in pol_of]
            M = E([m["text"] for m in mems])
            s_full, s_then = M @ full.T, M @ then.T
            s_if = np.full_like(s_then, -1.0)
            for j, (i, _) in enumerate(cond_texts):
                col = ids.index(i)
                s_if[:, col] = np.maximum(s_if[:, col], M @ C[j])
            s_if = np.maximum(s_if, 0)
            scores = {"full": s_full, "then": s_then, "then-0.5": s_then - 0.5 * s_if, "then-1.0": s_then - 1.0 * s_if}
            for k, S in scores.items():
                for r, m in enumerate(mems):
                    order = list(np.argsort(-S[r]))
                    ranks[k].append(order.index(ids.index(pol_of[m["id"]])))
        print(f"\n{name}: {len(ranks['full'])} memories, {n_rules} rules ({parsed_ok} parsed)")
        for k, rs in ranks.items():
            rs = np.array(rs)
            print(f"  {k:9s} top-1 {np.mean(rs < 1):.3f}  top-3 {np.mean(rs < 3):.3f}  top-5 {np.mean(rs < 5):.3f}  top-12 {np.mean(rs < 12):.3f}")
    print("new parse calls:", llm.calls)


if __name__ == "__main__":
    main()
