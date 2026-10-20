"""One targeted repair of a rejected rendering (design doc §18h). Never a whole-scenario
re-render, never more than one call.

    # plan only, no call, no key needed
    uv run python scripts/repair_run.py --base data/rendered/smoke-render-v8/raw/F1-000.46ddd88bb57031c7.a1.json \
        --run smoke-render-v8-repair --dry-run
    # the single repair call (needs approval and a cap)
    uv run --group lyzr python scripts/repair_run.py --base ... --run smoke-render-v8-repair --budget-usd <cap>

The base response is never modified. Outputs go to data/rendered/<run>/: repair.json (base
hash, permitted fields, problems, the model's raw reply, the merge result and the diff),
and, only if every hard check passes, system/, eval/, review.md, review.csv,
leak-report.json; spend.json always.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from beliefbench.generate import generate_suite
from beliefbench.render import leakcheck
from beliefbench.render.lyzr_client import DEFAULT_MODEL, MODEL_PRICES, BudgetExceeded, LyzrRenderer, SpendGuard
from beliefbench.render.repair import (
    REPAIR_PROMPTS,
    REPAIR_TEMPERATURE,
    REPAIR_VERSION,
    apply_repair,
    changed_paths,
    plan,
    repair_message,
    verify,
)
from beliefbench.render.review import review_sheet, write_csv_template


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="raw response file of the rejected attempt (frozen)")
    ap.add_argument("--run", required=True)
    ap.add_argument("--model", default=DEFAULT_MODEL, choices=sorted(MODEL_PRICES))
    ap.add_argument("--budget-usd", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    base_path = Path(args.base)
    base = json.loads(base_path.read_text())
    version = base["prompt_version"]
    base_sha = hashlib.sha256(base_path.read_bytes()).hexdigest()
    s = next(x for x in generate_suite(10, args.seed) if x.id == base["scenario"])
    response, _, _, problems = plan(s, base["response"], version, args.seed)
    if not problems:
        sys.exit("base has no hard flags; nothing to repair")
    message = repair_message(response, problems)
    system_prompt = REPAIR_PROMPTS[REPAIR_VERSION]
    guard = SpendGuard(budget_usd=args.budget_usd, max_calls=1, model=args.model)
    print(f"base {base_path} (sha256 {base_sha[:12]}, {version}); repair prompt {REPAIR_VERSION} "
          f"(sha256 {hashlib.sha256(system_prompt.encode()).hexdigest()[:12]}), temperature {REPAIR_TEMPERATURE}")
    print("permitted fields:", json.dumps(problems, indent=1))
    print(f"worst case for the single call: ${guard.worst_case(len(system_prompt) + len(message)):.4f}; "
          f"cap ${args.budget_usd:.2f}; call cap 1")
    if args.dry_run:
        return
    out = Path("data/rendered") / args.run
    if out.exists():
        sys.exit(f"{out} exists; a repair is run once")
    out.mkdir(parents=True)

    from dotenv import load_dotenv

    load_dotenv()
    renderer = LyzrRenderer(guard, temperature=REPAIR_TEMPERATURE, prompt_version=REPAIR_VERSION,
                            system_prompt=system_prompt)
    record = {"base": str(base_path), "base_sha256": base_sha, "base_prompt_version": version,
              "repair_version": REPAIR_VERSION, "temperature": REPAIR_TEMPERATURE, "permitted": problems}
    try:
        try:
            text, meta = renderer.call(message, note=f"{s.id} repair")
        except BudgetExceeded as e:
            record["outcome"] = f"refused by guard: {e}"
            text, meta = None, None
    finally:
        renderer.close()
    if text is not None:
        record |= {"response": text, "metadata": meta}
        merged, errors = apply_repair(response, text, problems)
        if errors:
            record |= {"outcome": "repair rejected (not the permitted edit)", "errors": errors}
        else:
            record["diff"] = {p: {"before": _get(response, p),
                                  "after": _get(merged, p)} for p in sorted(changed_paths(response, merged))}
            r, system, evaluation, hard = verify(s, merged, version, args.seed)
            record["hard_flags_after"] = [f.__dict__ for f in hard]
            if hard:
                record["outcome"] = "repair rejected (hard flags remain)"
            else:
                record["outcome"] = "repaired: 0 hard flags"
                for d in ("system", "eval"):
                    (out / d).mkdir()
                (out / "system" / f"{system['scenario']}.json").write_text(json.dumps(system, indent=1))
                (out / "eval" / f"{system['scenario']}.json").write_text(json.dumps(evaluation, indent=1, default=str))
                rep = leakcheck.check([(system, evaluation)], leakcheck.evidence_echo_hard(version),
                                      leakcheck.continuity_enforced(version))
                (out / "leak-report.json").write_text(json.dumps(
                    {**rep.summary(), "aucs": rep.aucs, "flags": [f.__dict__ for f in rep.flags]}, indent=1, default=str))
                (out / "review.md").write_text("# Renderer review sheet (targeted repair)\n\n"
                                               + review_sheet(system, evaluation, rep.flags))
                write_csv_template(out / "review.csv", [system["scenario"]])
    (out / "repair.json").write_text(json.dumps(record, indent=1, default=str))
    (out / "spend.json").write_text(json.dumps({"model": args.model, "budget_usd": args.budget_usd, "calls": guard.calls,
                                                "est_usd_conservative": round(guard.spent_usd, 4),
                                                "calls_log": guard.log}, indent=1))
    print(record.get("outcome"), f"spent≈${guard.spent_usd:.4f}")


def _get(obj, path):
    from beliefbench.render.repair import _flatten

    return _flatten(obj).get(path)


if __name__ == "__main__":
    main()
