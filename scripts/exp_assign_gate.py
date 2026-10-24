"""Offline: rule-assignment accuracy from cached v0.8 probability passes, for argmax, the full
per-entity Hungarian assignment, and a confidence-gated assignment (memories whose top rule has
probability >= tau keep it; only the rest are assigned jointly, excluding rules confidently held
in their group). No model calls.

    uv run --all-extras python scripts/exp_assign_gate.py
"""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from beliefbench.beliefgraph_eval import load_rendered  # noqa: E402
from beliefbench.stream import merge  # noqa: E402
from beliefgraph.cache import CachedLLM  # noqa: E402
from beliefgraph.core import _assign_by_entity  # noqa: E402
from beliefgraph.prompts import ROUTE_LETTER_PROMPT  # noqa: E402
from beliefgraph.retrieve import DenseIndex, entity_names  # noqa: E402

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class Replay:
    model, usage, thinking, supports_choice_probs = "gemma-4-12b-it", [], None, True

    def __call__(self, *a):
        raise RuntimeError("nc")

    def choice_probs(self, *a):
        raise RuntimeError("nc")


def gated(dists, texts, tau):
    keep = {m: max(d, key=d.get) for m, d in dists.items() if d and max(d.values()) >= tau}
    rest = {m: d for m, d in dists.items() if m not in keep}
    # exclude, for each uncertain memory, rules confidently held by a memory that shares a name
    names = {m: entity_names(t) for m, t in texts.items()}
    pruned = {}
    for m, d in rest.items():
        held = {p for k, p in keep.items() if names[k] & names[m]}
        dd = {p: v for p, v in d.items() if p not in held} or d
        z = sum(dd.values()) or 1
        pruned[m] = {p: v / z for p, v in dd.items()}
    out = dict(keep)
    out.update(_assign_by_entity(pruned, {m: texts[m] for m in pruned}) if pruned else {})
    return out


def dists_for(store, run_raw):
    """Re-create v0.8's candidate lists and read the cached probability passes."""
    llm = CachedLLM(Replay(), run_raw)
    facts = {e["id"]: e for e in store["evidence"]}
    mems = {m["id"]: m for m in store["memories"]}
    pols = {p["id"]: p for p in store["policies"]}
    pidx = DenseIndex([(p, x["text"]) for p, x in pols.items()])
    iidx = DenseIndex([(i, x["text"]) for i, x in {**facts, **mems}.items()])
    out = {}
    for mid, m in mems.items():
        text = m["text"]
        near = [f for f in iidx.rank(text, exclude={mid}) if f in facts][:5]
        cands = pidx.rank(text)[:12]
        tot = {p: 0.0 for p in cands}
        for o, order in enumerate((cands, cands[::-1])):
            msg = json.dumps({"memory": text, "facts_about_it": [facts[f]["text"] for f in near],
                              "policies": {LETTERS[k]: pols[p]["text"] for k, p in enumerate(order)}}, indent=1)
            try:
                probs = llm.choice_probs(ROUTE_LETTER_PROMPT, msg, '{"policy": "', LETTERS[: len(order)],
                                         f"{store['scenario']} choice{o}.{mid}")
            except RuntimeError:
                return None
            for k, v in probs.items():
                tot[order[LETTERS.index(k)]] += v
        z = sum(tot.values())
        out[mid] = {p: v / z for p, v in tot.items()} if z else {p: 1 / len(cands) for p in cands}
    return out


def main() -> None:
    sets = []
    long_runs = ["long-s300-p0", "long-s300-p1", "long-s300-p2", "long-s300-p3", "long-s300-p4"]
    dossiers = []
    for i, item in enumerate(x for r in long_runs for x in load_rendered(Path("data/rendered") / r)):
        s, c = merge([item], seed=0)
        s["scenario"] = f"dossier{i:03d}"
        dossiers.append((s, c))
    sets.append(("36 long dossiers", dossiers, Path("data/beliefgraph/long-v08-gemma-4-12b-it/raw"), "policy_of"))
    pool = load_rendered(Path("data/rendered/mquake-t-v1"))
    s, c = merge(random.Random("0:36").sample(pool, 36), seed=0)
    sets.append(("MQuAKE 423 memories", [(s, c)], Path("data/beliefgraph/mqbig-v08-gemma-4-12b-it/raw"), "memory_policy"))
    for name, stores, raw, key in sets:
        tot = {k: 0 for k in ("argmax", "hungarian", "gate0.5", "gate0.7", "gate0.9")}
        n = 0
        for store, comps in stores:
            gold = {}
            for comp in comps:
                fwd = {v: k for k, v in comp["back"].items()}
                if key == "policy_of":
                    gold.update({fwd[m]: fwd[p] for p, m in comp["ev"]["policy_of"].items()})
                else:
                    gold.update({fwd[m]: fwd[p] for m, p in comp["ev"]["memory_policy"].items()})
            d = dists_for(store, raw)
            if d is None:
                continue
            texts = {m["id"]: m["text"] for m in store["memories"]}
            picks = {"argmax": {m: max(x, key=x.get) for m, x in d.items()}, "hungarian": _assign_by_entity(d, texts)}
            for tau in (0.5, 0.7, 0.9):
                picks[f"gate{tau}"] = gated(d, texts, tau)
            for k, p in picks.items():
                tot[k] += sum(p.get(m) == gold[m] for m in gold)
            n += len(gold)
        print(f"{name} ({n} memories): " + ", ".join(f"{k} {v / n:.3f}" for k, v in tot.items()), flush=True)


if __name__ == "__main__":
    main()
