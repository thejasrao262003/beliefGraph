"""Model-free checks for spec v0.2: differential test vs Veritas-TMS, and S5/S7 baselines.

    uv sync --all-groups
    uv run python scripts/prior_art_report.py [--seeds 20] [--fuzz 5000]

Writes data/prior-art.results.txt. Generator, labeller and metrics are unchanged.
"""

from __future__ import annotations

import argparse
import random
import statistics
from collections import Counter
from pathlib import Path

from beliefbench.baselines import direct_only, naive_cascade
from beliefbench.diffcheck import (
    disagreements,
    features,
    in_shared_subset,
    minimize,
    random_retraction_scenario,
    render,
)
from beliefbench.generate import FAMILIES, generate_suite
from beliefbench.metrics import RevisionScore
from beliefbench.prior_art import (
    atlas_actions_native,
    atlas_actions_threshold,
    atlas_proposals,
    pacmi_actions,
)
from beliefbench.schema import Action

METRICS = ("stale_rate", "over_invalidation_rate", "macro_f1")
TAUS = (0.5, 0.6, 0.7, 0.75)


def ci(xs: list) -> str:
    xs = [x for x in xs if x is not None]
    if not xs:
        return "-"
    m = statistics.fmean(xs)
    h = 1.96 * statistics.stdev(xs) / len(xs) ** 0.5 if len(xs) > 1 else 0.0
    return f"{m:.3f} ±{h:.3f}"


def differential(seeds: int, n_fuzz: int) -> list[str]:
    lines = ["== 1. Differential test: labeler.gold_actions vs Veritas-TMS 0.16.0 (shared subset) =="]
    pilot = [s for seed in range(seeds) for s in generate_suite(10, seed) if in_shared_subset(s)]
    fuzz = [random_retraction_scenario(random.Random(f"fuzz:{i}"), f"fuzz-{i:05d}") for i in range(n_fuzz)]
    for name, suite in (("pilot F1-F3 retractions", pilot), ("random DAGs", fuzz)):
        cov = Counter(f for s in suite for f in features(s))
        bad = [s for s in suite if disagreements(s)]
        n_nodes = sum(len(s.nodes) for s in suite)
        lines.append(f"{name}: {len(suite)} scenarios, {n_nodes} nodes, disagreeing scenarios: {len(bad)}")
        lines.append("  coverage: " + ", ".join(f"{k}={v}" for k, v in sorted(cov.items())))
        for s in bad[:3]:
            small = minimize(s, lambda c: bool(disagreements(c)))
            lines.append(f"  counterexample {s.id} (minimised):\n{render(small)}\n  diff: {disagreements(small)}")
    lines.append("Scope: retract-only, reliability >= target, not outdated. Not compared: supersede/STALE, "
                 "hedge/UNK, low-reliability, outdated (no equivalent Veritas representation).")
    return lines


def systems() -> dict:
    out = {
        "direct_only": direct_only,
        "naive_cascade": naive_cascade,
        "S5 pacmi": pacmi_actions,
        "S7 atlas (native |Δ|>=0.15)": atlas_actions_native,
    }
    for tau in TAUS:
        out[f"S7 atlas (applied, c<{tau})"] = lambda s, tau=tau: atlas_actions_threshold(s, tau)
    return out


def baselines(seeds: int) -> list[str]:
    res: dict = {}
    conf: dict = {}  # family -> {"keep"/"revise"} -> list of max confidence drops
    for seed in range(seeds):
        suite = generate_suite(10, seed)
        groups = {"all": suite} | {f: [s for s in suite if s.family == f] for f in FAMILIES}
        for g, group in groups.items():
            for name, fn in systems().items():
                score = RevisionScore()
                for s in group:
                    score.add(s.gold, fn(s))
                summ = score.summary()
                cell = res.setdefault(name, {}).setdefault(g, {m: [] for m in METRICS})
                for m in METRICS:
                    cell[m].append(summ[m])
        for s in suite:
            drops: dict[str, float] = {}
            for p in atlas_proposals(s):
                drops[p.target] = max(drops.get(p.target, 0.0), p.old - p.new)
            for nid, d in drops.items():
                kind = "keep" if s.gold[nid] is Action.KEEP else "revise"
                conf.setdefault(s.family, {}).setdefault(kind, []).append(d)

    lines = [f"== 2. Baselines: {seeds} seeds x 40 scenarios. Mean ±95% CI over seeds =="]
    for g in ("all", *FAMILIES):
        lines.append(f"-- {g} --")
        lines.append(f"{'system':<30}{'stale':>16}{'overinv':>16}{'macroF1':>16}")
        for name, cells in res.items():
            lines.append(f"{name:<30}" + "".join(f"{ci(cells[g][m]):>16}" for m in METRICS))
    lines.append("")
    lines.append("== 3. Atlas native confidence behaviour (unapplied proposals, c0=0.8) ==")
    lines.append("Max confidence drop per impacted node, split by gold action:")
    for fam in FAMILIES:
        parts = []
        for kind in ("keep", "revise"):
            xs = conf.get(fam, {}).get(kind, [])
            parts.append(f"{kind}: n={len(xs)} mean={statistics.fmean(xs):.4f}" if xs else f"{kind}: n=0")
        lines.append(f"  {fam}: " + " | ".join(parts))
    return lines


def counterexamples() -> list[str]:
    """Smallest generated scenarios where each prior-art baseline over-invalidates or
    leaves a conclusion stale."""
    lines = ["== 4. Minimal failure graphs (from generated scenarios; over-invalidation searched in F2) =="]
    full = [s for seed in range(5) for s in generate_suite(10, seed)]
    for name, fn in (("S5 pacmi", pacmi_actions), ("S7 atlas native", atlas_actions_native)):
        for label, pred in (
            ("over-invalidation", lambda g, p: g is Action.KEEP and p is not Action.KEEP),
            ("stale", lambda g, p: g is not Action.KEEP and p is Action.KEEP),
        ):
            def fails(s, fn=fn, pred=pred):
                from beliefbench.labeler import gold_actions

                gold, got = gold_actions(s), fn(s)
                return any(pred(gold[n], got[n]) for n in gold)

            suite = [s for s in full if s.family == "F2"] if label == "over-invalidation" else full
            hits = [s for s in suite if fails(s)]
            if not hits:
                lines.append(f"{name} / {label}: none found")
                continue
            small = minimize(min(hits, key=lambda s: len(s.nodes)), fails)
            from beliefbench.labeler import gold_actions

            gold, got = gold_actions(small), fn(small)
            lines.append(f"{name} / {label}  (gold -> {name}):")
            lines.append("\n".join(
                f"{line}   [gold {gold[n.id].value} -> {got[n.id].value}]"
                for line, n in zip(render(small).splitlines(), small.nodes)
            ))
            lines.append(render(small).splitlines()[-1])
    return lines


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--fuzz", type=int, default=5000)
    ap.add_argument("--out", type=Path, default=Path("data/prior-art.results.txt"))
    args = ap.parse_args()
    lines = differential(args.seeds, args.fuzz) + [""] + baselines(args.seeds) + [""] + counterexamples()
    text = "\n".join(lines) + "\n"
    args.out.write_text(text)
    print(text)


if __name__ == "__main__":
    main()
