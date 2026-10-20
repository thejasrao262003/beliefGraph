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
import re
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
from beliefbench.render import repair
from beliefbench.render.review import review_sheet, write_csv_template
from beliefbench.render.views import build_views


def payload_hash(s, model: str, seed: int = 0, version: str = PROMPT_VERSION) -> str:
    return hashlib.sha256(f"{version}|{model}|{user_message(s, seed)}".encode()).hexdigest()[:16]


def attempt_message(s, feedback: list[str], seed: int = 0) -> str:
    msg = user_message(s, seed)
    if feedback:
        msg += "\n\nYour previous attempt had these problems. Fix all of them:\n" + "\n".join(f"- {f}" for f in feedback)
    return msg


def repair_loop(s, base_response: dict, system: dict, evaluation: dict, hard: list, repairer, raw_dir: Path,
                cache_stem: str, max_repairs: int, seed: int, version: str):
    """Targeted repairs (repair.py) of one rejected rendering: each call may change only the
    fields its hard flags map to; every hard check is re-run after each merge. Returns
    (rendering, system, evaluation) on success, else None. Each repair is cached as
    <stem>.r<k>.json next to the attempt it repairs."""
    response = base_response
    for k in range(1, max_repairs + 1):
        try:
            problems = repair.editable_paths(hard, evaluation, response)
        except ValueError:
            return None  # a flag that maps to no field: not repairable
        cache = raw_dir / f"{cache_stem}.r{k}.json"
        if cache.exists():
            rec = json.loads(cache.read_text())
        else:
            if repairer is None:
                return None
            text, meta = repairer.call(repair.repair_message(response, problems), note=f"{s.id} {cache_stem[-2:]} repair {k}")
            rec = {"scenario": s.id, "repair": k, "prompt_version": version, "permitted": problems,
                   "response": text, "metadata": meta}
        merged, errors = repair.apply_repair(response, rec["response"], problems)
        rec["merge_errors"] = errors
        if merged is not None:
            rec["diff"] = sorted(repair.changed_paths(response, merged))
            rec["merged"] = merged
        cache.write_text(json.dumps(rec, indent=1, default=str))
        if merged is None:
            return None
        r, system, evaluation, hard = repair.verify(s, merged, version, seed)
        if not hard:
            return r, system, evaluation
        response = merged
    return None


def render_one(s, renderer: LyzrRenderer | None, raw_dir: Path, model: str, max_attempts: int, seed: int,
               version: str = PROMPT_VERSION, repairer: LyzrRenderer | None = None, max_repairs: int = 0):
    """Returns (rendering, system, evaluation, attempts) or raises after max_attempts. With
    max_repairs > 0, a rendering rejected by hard checks gets up to that many targeted
    repairs before the next whole-scenario attempt."""
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
        hard = leakcheck.hard_flags(system, evaluation, version)
        if hard and max_repairs:
            fixed = repair_loop(s, repair.load_response(rec["response"]), system, evaluation, hard, repairer, raw_dir,
                                cache.stem, max_repairs, seed, version)
            if fixed:
                return (*fixed, attempt)
        if hard:
            inv = {v: k for k, v in evaluation["idmap"].items()}
            def name(item):
                return re.sub(r"[empu]_[0-9a-f]{4}", lambda m: inv.get(m.group(0), m.group(0)), item)

            feedback = [f"{name(f.item)} has forbidden {f.kind}: '{name(f.match)}'" for f in hard]
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
    ap.add_argument("--prior-spend-usd", type=float, default=0.0,
                    help="spend already charged against this budget by earlier runs (makes the cap cumulative)")
    ap.add_argument("--max-attempts", type=int, default=3)
    ap.add_argument("--only", nargs="+", default=None, help="render only these scenario ids (e.g. F1-000 F6-000)")
    ap.add_argument("--max-repairs", type=int, default=0,
                    help="targeted repairs of a rejected rendering before the next whole attempt")
    ap.add_argument("--stop-on-failure", action="store_true",
                    help="stop the whole run when a scenario fails all its attempts (pilot-2 control)")
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
    if args.only:
        suite = [s for s in suite if s.id in set(args.only)]
        missing = set(args.only) - {s.id for s in suite}
        if missing:
            sys.exit(f"unknown scenario ids: {sorted(missing)}")
    max_calls = len(suite) * args.max_attempts * (1 + args.max_repairs)
    guard = SpendGuard(budget_usd=args.budget_usd, max_calls=max_calls, model=args.model,
                       spent_usd=args.prior_spend_usd)
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
    repairer = (LyzrRenderer(guard, temperature=repair.REPAIR_TEMPERATURE, prompt_version=args.prompt_version,
                             system_prompt=repair.repair_prompt(args.prompt_version)) if args.max_repairs else None)
    pairs, failures, attempts = [], {}, {}
    try:
        for s in suite:
            try:
                r, system, evaluation, k = render_one(s, renderer, raw_dir, args.model, args.max_attempts, args.seed,
                                                      args.prompt_version, repairer, args.max_repairs)
            except BudgetExceeded as e:
                print(f"STOP: {e}", file=sys.stderr)
                break
            except ValueError as e:
                failures[s.id] = str(e)
                print(f"FAIL {s.id}: {e}", file=sys.stderr)
                if args.stop_on_failure:
                    print("STOP: --stop-on-failure", file=sys.stderr)
                    break
                continue
            attempts[s.id] = k
            (out / "system" / f"{system['scenario']}.json").write_text(json.dumps(system, indent=1))
            (out / "eval" / f"{system['scenario']}.json").write_text(json.dumps(evaluation, indent=1, default=str))
            pairs.append((system, evaluation))
            print(f"ok {s.id} -> {system['scenario']} (attempt {k}, spent≈${guard.spent_usd:.4f})")
    finally:
        renderer.close()
        if repairer:
            repairer.close()

    rep = leakcheck.check(pairs, leakcheck.evidence_echo_hard(args.prompt_version),
                          leakcheck.continuity_enforced(args.prompt_version)) if pairs else None
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
             "prior_spend_usd": args.prior_spend_usd, "calls": guard.calls,
             "est_usd_conservative": round(guard.spent_usd, 4), "budget_usd": args.budget_usd,
             "rendered": len(pairs), "first_attempt_ok": sum(1 for k in attempts.values() if k == 1),
             "failures": failures, "calls_log": guard.log}
    (out / "spend.json").write_text(json.dumps(spend, indent=1))
    print(json.dumps({k: v for k, v in spend.items() if k != "calls_log"}, indent=1))
    if rep:
        print(json.dumps(rep.summary(), indent=1, default=str))


if __name__ == "__main__":
    main()
