"""Reproducible, quota-stratified sample of scenarios for a fresh validation run.

    uv run python scripts/sample_validation.py --seed 2 --rng 20261020

Four scenarios per family from the frozen generator at ``--seed``. The quotas force each
family's stress cases into the sample (declared before any rendering; design doc §23);
within a quota the pick is random under ``--rng``, so the sample is not hand-chosen.
"""

from __future__ import annotations

import argparse
import random

from beliefbench.generate import generate_suite

QUOTAS = {
    "F1": [lambda m: m["relation"] == "retracts", lambda m: m["relation"] == "retracts",
           lambda m: m["depth"] >= 4, lambda m: True],
    "F2": [lambda m: m["relation"] == "retracts", lambda m: m["relation"] == "supersedes",
           lambda m: m["preserved"], lambda m: not m["preserved"]],
    "F3": [lambda m: m["has_alternative"], lambda m: m["has_alternative"],
           lambda m: m["relation"] == "retracts", lambda m: not m["has_alternative"]],
    "F6": [lambda m: not m["has_alternative"] and m["variant"] == "hedge",
           lambda m: not m["has_alternative"] and m["variant"] == "low_reliability",
           lambda m: m["has_alternative"], lambda m: True],
}


def sample(seed: int, rng_seed: int) -> list:
    suite = generate_suite(10, seed)
    rng = random.Random(rng_seed)
    picked = []
    for fam, rules in QUOTAS.items():
        pool = [s for s in suite if s.family == fam]
        rng.shuffle(pool)
        chosen = []
        for rule in rules:
            chosen.append(next(s for s in pool if s not in chosen and rule(s.meta)))
        picked += chosen
    return picked


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=2)
    ap.add_argument("--rng", type=int, default=20261020)
    args = ap.parse_args()
    for s in sample(args.seed, args.rng):
        print(s.id, s.meta)
