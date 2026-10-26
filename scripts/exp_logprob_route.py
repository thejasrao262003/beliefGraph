"""Experiment (#2): choose a memory's rule from token probabilities instead of a sampled answer.

For each memory, the same 12 candidates and context the v0.4 router sees, labelled A-L. The
assistant turn is prefilled with '{"policy": "' and the next token's log-probabilities give a
distribution over the letters (one forward pass, no sampling). "perm" averages the
probabilities over the identity and reversed option orders (position-bias correction,
cf. PriDe / permutation self-consistency). Compared with the model's current first sampled
pick, replayed from the run's cache.

    uv run --all-extras python scripts/exp_logprob_route.py   # baseline model: gemma-4-12b-it
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

try:  # local configuration (git-ignored): keys and BELIEFGRAPH_MODAL_WORKSPACE
    from dotenv import load_dotenv

    load_dotenv(Path.cwd() / ".env")
except ImportError:
    pass

sys.path.insert(0, str(Path(__file__).parent))
from run_stream import RUNS  # noqa: E402

from beliefbench.beliefgraph_eval import load_accepted, load_rendered  # noqa: E402
from beliefbench.stream import merge  # noqa: E402
from beliefgraph.cache import CachedLLM  # noqa: E402
from beliefgraph.core import _load_json  # noqa: E402
from beliefgraph.prompts import ROUTE_PROMPT  # noqa: E402
from beliefgraph.retrieve import DenseIndex  # noqa: E402

LONG = ["long-s300-p0", "long-s300-p1", "long-s300-p2", "long-s300-p3", "long-s300-p4"]
LETTERS = "ABCDEFGHIJKL"
LETTER_PROMPT = ROUTE_PROMPT.replace('{"policy": <number or null>}', '{"policy": "<letter>"}').replace(
    "Decide which numbered policy it is. Answer null if none of them is.", "Decide which lettered policy it is.")


def stores():
    pool = [x for r in RUNS for x in load_accepted(Path("data/rendered") / r)]
    store, comps = merge(random.Random("0:30").sample(pool, 30), seed=0)
    yield "143-memory store", "ladder-gemma-4-12b-it-nothink", [(store, comps)]
    ds = []
    for i, item in enumerate(x for r in LONG for x in load_rendered(Path("data/rendered") / r)):
        s, c = merge([item], seed=0)
        s["scenario"] = f"dossier{i:03d}"
        ds.append((s, c))
    yield "36 long dossiers", "long-v06-gemma-4-12b-it", ds


def assignment(dist) -> int:
    """#4: per entity group, maximise the summed log-probability of a one-to-one memory-to-rule
    assignment (Hungarian). Groups: memories of one store that share an entity name."""
    import numpy as np
    from scipy.optimize import linear_sum_assignment

    from beliefgraph.retrieve import entity_names

    groups: dict = {}
    for meta, gold, probs in dist:
        groups.setdefault(meta[0], []).append((meta, gold, probs))
    right = 0
    for items in groups.values():
        # union memories that share a name
        parent = list(range(len(items)))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        names = [entity_names(meta[2]) for meta, _, _ in items]
        for i in range(len(items)):
            for j in range(i):
                if names[i] & names[j]:
                    parent[find(i)] = find(j)
        clusters: dict = {}
        for i in range(len(items)):
            clusters.setdefault(find(i), []).append(i)
        for idx in clusters.values():
            rules = sorted({p for i in idx for p in items[i][2]})
            cost = np.full((len(idx), len(rules)), 50.0)
            for r, i in enumerate(idx):
                tot = sum(items[i][2].values()) or 1.0
                for c, p in enumerate(rules):
                    v = items[i][2].get(p, 0.0) / tot
                    if v > 0:
                        cost[r, c] = -np.log(v + 1e-9)
            rows, cols = linear_sum_assignment(cost)
            right += sum(rules[c] == items[idx[r]][1] for r, c in zip(rows, cols))
    return right


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gemma-4-12b-it")
    ap.add_argument("--base-url", default=f"https://{os.environ.get('BELIEFGRAPH_MODAL_WORKSPACE', '<workspace>')}--beliefgraph-gemma-4-12b-it-server.us-east.modal.direct/v1")
    args = ap.parse_args()
    from dotenv import load_dotenv
    import openai

    load_dotenv(Path.cwd() / ".env")
    client = openai.OpenAI(base_url=args.base_url, api_key=os.environ["BELIEFGRAPH_VLLM_KEY"], timeout=600)
    cache_dir = Path("data/beliefgraph/exp-logprob-route") / args.model
    cache_dir.mkdir(parents=True, exist_ok=True)

    def letter_probs(msg: str) -> dict[str, float]:
        import hashlib

        f = cache_dir / (hashlib.sha256(msg.encode()).hexdigest()[:16] + ".json")
        if f.exists():
            return json.loads(f.read_text())
        r = client.chat.completions.create(
            model=args.model, max_tokens=1, logprobs=True, top_logprobs=20, temperature=0,
            messages=[{"role": "system", "content": LETTER_PROMPT}, {"role": "user", "content": msg},
                      {"role": "assistant", "content": '{"policy": "'}],
            extra_body={"continue_final_message": True, "add_generation_prompt": False})
        probs: dict[str, float] = {}
        for t in r.choices[0].logprobs.content[0].top_logprobs:
            k = t.token.strip().upper()
            if k in LETTERS:
                probs[k] = probs.get(k, 0.0) + math.exp(t.logprob)
        f.write_text(json.dumps(probs))
        return probs

    class Replay:
        model, usage, thinking = args.model, [], None

        def __call__(self, *a):
            raise RuntimeError("not cached")

    for name, run, group in stores():
        cached = CachedLLM(Replay(), Path("data/beliefgraph") / run / "raw")
        n = right_sample = right_lp = right_perm = gold_offered = right_vote = 0
        jobs = []
        for store, comps in group:
            pol_of = {}
            for c in comps:
                fwd = {v: k for k, v in c["back"].items()}
                pol_of.update({fwd[m]: fwd[p] for p, m in c["ev"]["policy_of"].items()})
            facts = {e["id"]: e for e in store["evidence"]}
            mems = {m["id"]: m for m in store["memories"]}
            pols = {p["id"]: p for p in store["policies"]}
            pidx = DenseIndex([(p, x["text"]) for p, x in pols.items()])
            iidx = DenseIndex([(i, x["text"]) for i, x in {**facts, **mems}.items()])
            for mid in mems:
                if mid not in pol_of:
                    continue
                text = mems[mid]["text"]
                near = [f for f in iidx.rank(text, exclude={mid}) if f in facts][:5]
                cands = pidx.rank(text)[:12]
                about = [facts[f]["text"] for f in near]
                numbered = json.dumps({"memory": text, "facts_about_it": about,
                                       "policies": {str(k + 1): pols[p]["text"] for k, p in enumerate(cands)}}, indent=1)
                picks = []
                for k in range(3):  # the model's sampled picks (v0.4 route calls, samples 0-2)
                    note = f"{store['scenario']} route0.{mid}" + (f"~s{k}" if k else "")
                    try:
                        v = _load_json(cached(ROUTE_PROMPT, numbered, note)).get("policy")
                        picks.append(cands[int(v) - 1] if v is not None and 1 <= int(v) <= len(cands) else None)
                    except RuntimeError:
                        picks.append("uncached")
                    except Exception:  # noqa: BLE001
                        picks.append(None)
                pick = picks[0]
                from collections import Counter

                votes = Counter(x for x in picks if x not in (None, "uncached"))
                voted = max(votes, key=lambda x: (votes[x], -picks.index(x))) if votes else None
                lettered = [json.dumps({"memory": text, "facts_about_it": about,
                                        "policies": {LETTERS[k]: pols[p]["text"] for k, p in enumerate(order)}}, indent=1)
                            for order in (cands, cands[::-1])]
                jobs.append((pol_of[mid], cands, pick, lettered, voted, (store["scenario"], mid, text)))
        with ThreadPoolExecutor(32) as pool:
            probs = list(pool.map(lambda j: [letter_probs(m) for m in j[3]], jobs))
        dist = []  # per memory: {policy: averaged probability}
        for (gold, cands, pick, _, voted, _meta), (p_id, p_rev) in zip(jobs, probs):
            if pick == "uncached":
                continue
            n += 1
            gold_offered += gold in cands
            right_sample += pick == gold
            right_vote += voted == gold
            s_id = {cands[LETTERS.index(k)]: v for k, v in p_id.items() if LETTERS.index(k) < len(cands)}
            rev = cands[::-1]
            s_rev = {rev[LETTERS.index(k)]: v for k, v in p_rev.items() if LETTERS.index(k) < len(rev)}
            right_lp += bool(s_id) and max(s_id, key=s_id.get) == gold
            both = {p: s_id.get(p, 0) + s_rev.get(p, 0) for p in cands}
            right_perm += max(both, key=both.get) == gold
            dist.append((_meta, gold, both))
        right_assign = assignment(dist)
        print(f"{name}: global assignment (one rule per memory, at most one memory per rule per entity group): "
              f"{right_assign / len(dist):.3f}", flush=True)
        print(f"{name}: {n} memories (gold among the 12 for {gold_offered}) | right rule first: sampled pick "
              f"{right_sample / n:.3f}, 3-sample vote {right_vote / n:.3f}, logprob {right_lp / n:.3f}, logprob + reversed order {right_perm / n:.3f}", flush=True)


if __name__ == "__main__":
    main()
