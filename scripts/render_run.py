"""Render pilot scenarios to natural language via a Lyzr agent, under a hard spend cap.

    # 1. plan only, no calls, no key needed
    uv run python scripts/render_run.py --dry-run
    # 2. smoke test: one scenario
    uv run --group lyzr python scripts/render_run.py --limit 1 --budget-usd 0.25
    # 3. full validation pilot (after checking the smoke-test spend in the Lyzr dashboard)
    uv run --group lyzr python scripts/render_run.py --budget-usd 5

Outputs go to data/rendered/<run>/: raw/ (every response, cached; never re-billed),
system/ (what evaluated systems see), eval/ (gold + structure), review.md,
review.csv (template), leak-report.json and spend.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from beliefbench.generate import generate_suite
from beliefbench.render import leakcheck
from beliefbench.render.lyzr_client import (
    DEFAULT_MODEL,
    MAX_VISIBLE_OUTPUT,
    MODEL_PRICES,
    THINKING_ALLOWANCE,
    BudgetExceeded,
    LyzrRenderer,
    SpendGuard,
)
from beliefbench.render.prompt import PROMPT_VERSION, PROMPTS, parse_response, user_message
from beliefbench.render.review import review_sheet, write_csv_template
from beliefbench.render.views import build_views


def payload_hash(s, model: str, seed: int = 0, version: str = PROMPT_VERSION) -> str:
    return hashlib.sha256(f"{version}|{model}|{user_message(s, seed)}".encode()).hexdigest()[:16]


def attempt_message(s, feedback: list[str], seed: int = 0) -> str:
    msg = user_message(s, seed)
    if feedback:
        msg += "\n\nYour previous attempt had these problems. Fix all of them:\n" + "\n".join(f"- {f}" for f in feedback)
    return msg


def render_one(s, renderer: LyzrRenderer | None, raw_dir: Path, model: str, max_attempts: int, seed: int,
               version: str = PROMPT_VERSION):
    """Returns (rendering, system, evaluation, attempts) or raises after max_attempts."""
    feedback: list[str] = []
    for attempt in range(1, max_attempts + 1):
        cache = raw_dir / f"{s.id}.{payload_hash(s, model, seed, version)}.a{attempt}.json"
        if cache.exists():
            rec = json.loads(cache.read_text())
        else:
            if renderer is None:
                raise RuntimeError("not cached and no renderer (dry run)")
            text, meta = renderer.call(attempt_message(s, feedback, seed), note=f"{s.id} attempt {attempt}")
            rec = {"scenario": s.id, "attempt": attempt, "prompt_version": version, "model": model,
                   "feedback": feedback, "response": text, "metadata": meta}
            cache.write_text(json.dumps(rec, indent=1, default=str))
        r = parse_response(s, rec["response"], version=version)
        if not r.ok:
            feedback = r.errors
            continue
        system, evaluation = build_views(s, r, seed=seed)
        hard = [f for f in leakcheck.text_flags(system) if f.hard]
        if hard:
            inv = {v: k for k, v in evaluation["idmap"].items()}
            feedback = [f"text of {inv.get(f.item, f.item)} contains forbidden {f.kind}: '{f.match}'" for f in hard]
            continue
        return r, system, evaluation, attempt
    raise ValueError(f"{s.id}: no valid rendering after {max_attempts} attempts; last problems: {feedback}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=None, help="output directory name (default: pilot-<prompt version>)")
    ap.add_argument("--prompt-version", default=PROMPT_VERSION, choices=sorted(PROMPTS))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-per-family", type=int, default=10)
    ap.add_argument("--limit", type=int, default=None, help="render only the first N scenarios (smoke test)")
    ap.add_argument("--model", default=DEFAULT_MODEL, choices=sorted(MODEL_PRICES))
    ap.add_argument("--budget-usd", type=float, default=5.0)
    ap.add_argument("--max-attempts", type=int, default=3)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    suite = generate_suite(args.n_per_family, args.seed)
    if args.limit:
        # Smoke test: one scenario per family first, so a small run still covers all families.
        by_fam = {}
        for s in suite:
            by_fam.setdefault(s.family, []).append(s)
        order = [x for group in zip(*by_fam.values()) for x in group]
        suite = order[: args.limit]
    max_calls = len(suite) * args.max_attempts
    guard = SpendGuard(budget_usd=args.budget_usd, max_calls=max_calls, model=args.model)
    out = Path("data/rendered") / (args.run or f"pilot-{args.prompt_version}")
    if out.exists() and any((out / "system").glob("*.json")) and not args.dry_run:
        # Never overwrite a finished run (e.g. the failed v2 smoke test); cached raw
        # responses are reused, but views and reports must go to a new directory.
        if (out / "spend.json").exists():
            sys.exit(f"{out} already holds a completed run; choose a new --run name")
    raw_dir = out / "raw"

    worst = sum(guard.worst_case(len(PROMPTS[args.prompt_version]) + len(user_message(s, args.seed))) for s in suite)
    print(f"{len(suite)} scenarios, prompt {args.prompt_version}, model {args.model} (guard prices "
          f"${guard.prices[0]:.2f}/${guard.prices[1]:.2f} per 1M), worst case per first attempt incl. {THINKING_ALLOWANCE + MAX_VISIBLE_OUTPUT:,} output tokens: "
          f"${worst:.3f} total; x{args.max_attempts} attempts = ${worst * args.max_attempts:.3f}. "
          f"Hard budget: ${args.budget_usd:.2f}, call cap {max_calls}.")
    if args.dry_run:
        return
    import os

    from dotenv import load_dotenv  # ships with lyzr-adk; .env is git-ignored

    from beliefbench.render.lyzr_client import lyzr_catalogue

    load_dotenv()
    catalogue = lyzr_catalogue(os.environ["LYZR_API_KEY"])
    if f"gemini/{args.model}" not in catalogue:
        sys.exit(f"gemini/{args.model} is not in Lyzr's live catalogue; refusing to run")
    print(f"Lyzr catalogue: gemini/{args.model} is live "
          f"(intelligence index {catalogue[f'gemini/{args.model}'].get('intelligence_index')})")

    for d in ("raw", "system", "eval"):
        (out / d).mkdir(parents=True, exist_ok=True)
    renderer = LyzrRenderer(guard, prompt_version=args.prompt_version)
    pairs, failures, attempts = [], {}, {}
    try:
        for s in suite:
            try:
                r, system, evaluation, k = render_one(s, renderer, raw_dir, args.model, args.max_attempts, args.seed,
                                                      args.prompt_version)
            except BudgetExceeded as e:
                print(f"STOP: {e}", file=sys.stderr)
                break
            except ValueError as e:
                failures[s.id] = str(e)
                print(f"FAIL {s.id}: {e}", file=sys.stderr)
                continue
            attempts[s.id] = k
            (out / "system" / f"{system['scenario']}.json").write_text(json.dumps(system, indent=1))
            (out / "eval" / f"{system['scenario']}.json").write_text(json.dumps(evaluation, indent=1, default=str))
            pairs.append((system, evaluation))
            print(f"ok {s.id} -> {system['scenario']} (attempt {k}, spent≈${guard.spent_usd:.4f})")
    finally:
        renderer.close()

    rep = leakcheck.check(pairs) if pairs else None
    if rep:
        (out / "leak-report.json").write_text(json.dumps(
            {**rep.summary(), "aucs": rep.aucs, "flags": [f.__dict__ for f in rep.flags]}, indent=1, default=str))
        flags_by = {}
        for f in rep.flags:
            flags_by.setdefault(f.scenario, []).append(f)
        (out / "review.md").write_text("# Renderer review sheet\n\n" + "\n".join(
            review_sheet(sv, ev, flags_by.get(sv["scenario"], [])) for sv, ev in pairs))
        write_csv_template(out / "review.csv", [sv["scenario"] for sv, _ in pairs])
    spend = {"model": args.model, "lyzr_catalogue_entry": catalogue.get(f"gemini/{args.model}"),
             "prompt_version": args.prompt_version, "seed": args.seed, "guard_prices_per_1m": guard.prices,
             "calls": guard.calls,
             "est_usd_conservative": round(guard.spent_usd, 4), "budget_usd": args.budget_usd,
             "rendered": len(pairs), "first_attempt_ok": sum(1 for k in attempts.values() if k == 1),
             "failures": failures, "calls_log": guard.log}
    (out / "spend.json").write_text(json.dumps(spend, indent=1))
    print(json.dumps({k: v for k, v in spend.items() if k != "calls_log"}, indent=1))
    if rep:
        print(json.dumps(rep.summary(), indent=1, default=str))


if __name__ == "__main__":
    main()
