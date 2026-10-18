"""Command line: generate a scenario suite, and evaluate the deterministic baselines on it.

    beliefbench generate --n-per-family 10 --seed 0 --out data/pilot.jsonl
    beliefbench evaluate data/pilot.jsonl [--by-family]
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path

from beliefbench.baselines import BASELINES, perturb_justifications
from beliefbench.generate import FAMILIES, generate_suite
from beliefbench.labeler import descendants, gold_actions
from beliefbench.metrics import ExtractionScore, RevisionScore
from beliefbench.schema import Scenario

PERTURB_RATES = (0.1, 0.25, 0.5)


def load(path: Path) -> list[Scenario]:
    with path.open() as f:
        return [Scenario.from_dict(json.loads(line)) for line in f if line.strip()]


def _fmt(x: float | None) -> str:
    return "  -  " if x is None else f"{x:.3f}"


def _row(name: str, rev: dict, ext: dict | None = None) -> str:
    cols = [rev["accuracy"], rev["macro_f1"], rev["stale_rate"], rev["over_invalidation_rate"]]
    cols += [ext[0]["justification_set_f1"], ext[1]["justification_set_f1"], ext[0]["and_or_typing_accuracy"]] if ext else [None] * 3
    return f"{name:<24}" + "".join(f"{_fmt(c):>9}" for c in cols)


HEADER = (
    f"{'system':<24}{'acc':>9}{'macroF1':>9}{'stale':>9}{'overinv':>9}"
    f"{'jsetF1':>9}{'jsetF1@A':>9}{'and/or':>9}"
)


def cmd_generate(args: argparse.Namespace) -> None:
    suite = generate_suite(args.n_per_family, args.seed, args.families)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w") as f:
        for s in suite:
            f.write(json.dumps(s.to_dict()) + "\n")
    print(f"wrote {len(suite)} scenarios to {args.out}")
    for fam in args.families:
        dist = Counter(a.value for s in suite if s.family == fam for a in s.gold.values())
        print(f"  {fam}: {dict(sorted(dist.items()))}")


def evaluate(suite: list[Scenario], seed: int) -> list[str]:
    lines = [HEADER]
    for name, system in BASELINES.items():
        score = RevisionScore()
        for s in suite:
            score.add(s.gold, system(s))
        lines.append(_row(name, score.summary()))
    # Simulated extraction errors, propagated correctly: how much revision quality
    # is lost purely to extraction.
    for rate in PERTURB_RATES:
        rng = random.Random(f"{seed}:perturb:{rate}")
        rev, ext, ext_affected = RevisionScore(), ExtractionScore(), ExtractionScore()
        for s in suite:
            pred = perturb_justifications(s.justifications(), rng, rate)
            ext.add(s.justifications(), pred)
            ext_affected.add(s.justifications(), pred, only=descendants(s, (u.target for u in s.updates)))
            rev.add(s.gold, gold_actions(s, pred))
        lines.append(_row(f"jtms+extract_err@{rate}", rev.summary(), (ext.summary(), ext_affected.summary())))
    return lines


def cmd_evaluate(args: argparse.Namespace) -> None:
    suite = load(args.data)
    groups = {"all": suite}
    if args.by_family:
        groups |= {fam: [s for s in suite if s.family == fam] for fam in sorted({s.family for s in suite})}
    for label, group in groups.items():
        print(f"\n== {label} ({len(group)} scenarios) ==")
        print("\n".join(evaluate(group, args.seed)))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="beliefbench")
    sub = parser.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate", help="generate a scenario suite as JSONL")
    g.add_argument("--n-per-family", type=int, default=10)
    g.add_argument("--seed", type=int, default=0)
    g.add_argument("--families", nargs="+", default=list(FAMILIES), choices=list(FAMILIES))
    g.add_argument("--out", type=Path, default=Path("data/pilot.jsonl"))
    g.set_defaults(func=cmd_generate)
    e = sub.add_parser("evaluate", help="score deterministic baselines on a suite")
    e.add_argument("data", type=Path)
    e.add_argument("--seed", type=int, default=0)
    e.add_argument("--by-family", action="store_true")
    e.set_defaults(func=cmd_evaluate)
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
