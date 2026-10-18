"""Seed-stability replication of pilot-1. Uses the frozen generator, labeller and metrics unchanged.

    uv run python scripts/seed_stability.py [--seeds 20] [--out data/seed-stability.results.txt]

1. Re-generates the pilot suite (10 scenarios x F1/F2/F3/F6) for each seed and reports
   mean and 95% CI (normal approximation over seeds) of SCR / OIR / macro-F1 per family.
2. Re-runs the simulated-extraction-error sweep and reports how often the pilot-1
   ordering reversal (SCR@0.5 < SCR@0.25) happens.
3. Applies one error type at a time, to see which extraction errors cause staleness
   and which cause over-invalidation.
"""

from __future__ import annotations

import argparse
import random
import statistics
from collections.abc import Callable
from pathlib import Path

from beliefbench.baselines import direct_only, naive_cascade, perturb_justifications
from beliefbench.generate import FAMILIES, generate_suite
from beliefbench.labeler import gold_actions
from beliefbench.metrics import RevisionScore
from beliefbench.schema import Justifications, Scenario

RATES = (0.1, 0.25, 0.5)
METRICS = ("stale_rate", "over_invalidation_rate", "macro_f1")
TRACKED = (*METRICS, "accuracy")
GROUPS = ("all", *FAMILIES)


def ci(xs: list[float]) -> str:
    xs = [x for x in xs if x is not None]
    if not xs:
        return "      -       "
    m = statistics.fmean(xs)
    h = 1.96 * statistics.stdev(xs) / len(xs) ** 0.5 if len(xs) > 1 else 0.0
    return f"{m:.3f} ±{h:.3f}"


def by_group(suite: list[Scenario]) -> dict[str, list[Scenario]]:
    return {"all": suite} | {f: [s for s in suite if s.family == f] for f in FAMILIES}


def revision(group: list[Scenario], predict: Callable[[Scenario], dict]) -> dict:
    score = RevisionScore()
    for s in group:
        score.add(s.gold, predict(s))
    return score.summary()


def single_op(justs: dict[str, Justifications], rng: random.Random, rate: float, op: str) -> dict:
    """Like perturb_justifications, but always applies ``op`` where it is applicable."""
    out = {}
    for nid in sorted(justs):
        js = [list(j) for j in justs[nid]]
        if rng.random() < rate:
            if op == "unlink":
                js = []
            elif op in ("drop_premise", "and_to_or") and any(len(j) > 1 for j in js):
                i = rng.choice([i for i, j in enumerate(js) if len(j) > 1])
                if op == "drop_premise":
                    js[i].pop(rng.randrange(len(js[i])))
                else:
                    js[i : i + 1] = [[p] for p in js[i]]
            elif op == "drop_alternative" and len(js) > 1:
                js.pop(rng.randrange(len(js)))
            elif op == "or_to_and" and len(js) > 1:
                js = [sorted({p for j in js for p in j})]
        out[nid] = js
    return out


OPS = ("unlink", "drop_premise", "and_to_or", "drop_alternative", "or_to_and")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--out", type=Path, default=Path("data/seed-stability.results.txt"))
    args = ap.parse_args()
    seeds = range(args.seeds)

    # results[system][group][metric] -> list over seeds
    results: dict[str, dict[str, dict[str, list]]] = {}
    ops_res: dict[str, dict[str, list]] = {op: {m: [] for m in METRICS} for op in OPS}

    def record(system: str, group: str, summary: dict) -> None:
        cell = results.setdefault(system, {}).setdefault(group, {m: [] for m in TRACKED})
        for m in TRACKED:
            cell[m].append(summary[m])

    for seed in seeds:
        suite = generate_suite(10, seed)
        groups = by_group(suite)
        for g, group in groups.items():
            record("direct_only", g, revision(group, direct_only))
            record("naive_cascade", g, revision(group, naive_cascade))
        for rate in RATES:
            # Same perturbation stream as cli.evaluate, so seed 0 reproduces pilot-1.
            rng = random.Random(f"{seed}:perturb:{rate}")
            preds = {s.id: perturb_justifications(s.justifications(), rng, rate) for s in suite}
            for g, group in groups.items():
                record(f"extract_err@{rate}", g, revision(group, lambda s: gold_actions(s, preds[s.id])))
        for op in OPS:
            rng = random.Random(f"{seed}:op:{op}")
            summary = revision(suite, lambda s: gold_actions(s, single_op(s.justifications(), rng, 0.5, op)))
            for m in METRICS:
                ops_res[op][m].append(summary[m])

    lines = [f"Seed stability: {args.seeds} seeds x 40 scenarios (10 per family). Mean ±95% CI over seeds.", ""]
    for g in GROUPS:
        lines.append(f"== {g} ==")
        lines.append(f"{'system':<22}" + "".join(f"{m:>16}" for m in ("stale", "overinv", "macroF1")))
        for system, cells in results.items():
            lines.append(f"{system:<22}" + "".join(f"{ci(cells[g][m]):>16}" for m in METRICS))
        lines.append("")

    # Pilot-1 (seed 0) looked non-monotonic between error rates 0.25 and 0.5. Count how
    # often a metric moves the "wrong" way (gets better with more extraction errors).
    lines.append("== non-monotonicity between extract_err@0.25 and @0.5 (seeds where 0.5 looks better) ==")
    for g in GROUPS:
        lo, hi = results["extract_err@0.25"][g], results["extract_err@0.5"][g]
        parts = []
        for m, worse_is_higher in (("stale_rate", True), ("macro_f1", False), ("accuracy", False)):
            pairs = [(a, b) for a, b in zip(lo[m], hi[m]) if a is not None and b is not None]
            n = sum((b < a) if worse_is_higher else (b > a) for a, b in pairs)
            parts.append(f"{m} {n}/{len(pairs)} (seed0: {lo[m][0]:.3f}->{hi[m][0]:.3f})")
        lines.append(f"{g:<5} " + " | ".join(parts))
    lines.append("")
    lines.append("== one error type at a time, rate 0.5, all families ==")
    lines.append(f"{'error type':<22}" + "".join(f"{m:>16}" for m in ("stale", "overinv", "macroF1")))
    for op in OPS:
        lines.append(f"{op:<22}" + "".join(f"{ci(ops_res[op][m]):>16}" for m in METRICS))

    text = "\n".join(lines) + "\n"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text)
    print(text)


if __name__ == "__main__":
    main()
