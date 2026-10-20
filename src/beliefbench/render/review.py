"""Human-review sheet for rendered scenarios, and parsing of the filled-in decisions."""

from __future__ import annotations

import csv
from pathlib import Path

from beliefbench.render.leakcheck import Flag

CHECKLIST = [
    ("C1_meaning", "Each text says what its node is meant to say (evidence = a fact; memory = a conclusion or plan)."),
    ("C2_and", "Within each justification set, all facts together entail the conclusion, and dropping any one breaks it."),
    ("C3_or", "Each alternative justification set alone entails the conclusion, using genuinely different facts."),
    ("C4_updates", "Each update says what its relation requires (retracts / supersedes with a new value / hedges), "
                   "speaks only about its target, and its source matches the stated reliability."),
    ("C5_sources", "Evidence source descriptions match their reliability (high / medium / low)."),
    ("C6_distractors", "Facts and memories in different groups are unrelated: nothing in one bears on another."),
    ("C7_no_reveal", "Read as the system would (system view only): the wording does not reveal which facts support "
                     "which memory, beyond what the meaning itself implies."),
    # Information availability (render-v2): judged from section A only, before reading B.
    ("C8_inferable", "From the visible facts and policies alone, the intended AND/OR structure can be inferred."),
    ("C9_no_hidden_needed", "Every gold label can be derived without the hidden rationale or any eval metadata."),
    ("C10_unambiguous", "No reasonable alternative reading of the text would make a gold label wrong."),
    ("C11_policy_not_graph", "Policies state reusable rules about kinds of facts; they do not name the specific "
                             "entity, quote evidence, or otherwise disclose which item supports which memory."),
    # render-v3
    ("C12_decoys_inert", "Decoy policies govern nothing here and offer no alternative route to any memory."),
    ("C13_final_state", "The renderer's after-update state for each memory follows from the policies and the "
                        "facts that remain credible (and recompute results are right)."),
]
COLUMNS = ["scenario", "reviewer", *[c for c, _ in CHECKLIST], "decision", "notes"]
DECISIONS = {"accept", "revise", "reject"}
# Semantic quality is judged by the reviewer, independently of the lexical checks: a
# scenario cannot be accepted unless these pass, however clean its automated report is
# (render-v7 revision, approved 2026-10-20).
REQUIRED_FOR_ACCEPT = ("C8_inferable", "C10_unambiguous")
# Which checklist item a soft flag is evidence for.
FLAG_ITEMS = {"policy_echoes_evidence": "C7/C11", "policy_names_subject": "C11", "explains_reason": "C7",
              "mentions_sources": "C7", "order_cue": "C7", "update_mentions_implication": "C4",
              "retraction_reads_as_hedge": "C4", "cross_group_entity": "C6", "unnamed_entity_in_groups": "C6",
              "final_state_mismatch": "C13", "recompute_unresolved": "C13"}


def review_sheet(system: dict, evaluation: dict, flags: list[Flag]) -> str:
    """Markdown block for one scenario: system view first (to judge C7 blind), then the
    structure, gold and rationale."""
    inv = {v: k for k, v in evaluation["idmap"].items()}
    lines = [f"## {system['scenario']}  ({evaluation['source_scenario']}, {system['domain']})", "",
             f"*World:* {evaluation['world']}", "", "### A. System view (judge C7 from this alone)"]
    for e in system["evidence"]:
        lines.append(f"- `{e['id']}` [{e['observed']}, {e['source']}] {e['text']}")
    lines.append("- memories:")
    for m in system["memories"]:
        lines.append(f"  - `{m['id']}` {m['text']}")
    for u in system["updates"]:
        lines.append(f"- update `{u['id']}` [{u['observed']}, {u['source']}] {u['text']}")
    if system.get("policies"):
        lines.append("- policies:")
        for p in system["policies"]:
            lines.append(f"  - `{p['id']}` {p['text']}")
    lines += ["", "### B. Intended structure"]
    pol_for = {m: p for p, m in evaluation.get("policy_of", {}).items()}
    for mid, justs in evaluation["justifications"].items():
        sets = " **OR** ".join("(" + " AND ".join(f"`{p}`" for p in j) + ")" for j in justs)
        pol = f" [policy `{pol_for[mid]}`]" if mid in pol_for else ""
        lines.append(f"- `{mid}` ({inv[mid]}){pol} <= {sets}; gold after update: **{evaluation['gold'][mid]}**")
        for i, r in enumerate(evaluation["rationale"].get(mid, [])):
            lines.append(f"  - set {i + 1}: {r}")
    for uid, u in evaluation["update_targets"].items():
        lines.append(f"- `{uid}` {u['relation']} `{u['target']}` (reliability {u['reliability']})")
    if evaluation.get("decoy_policies"):
        lines.append("- decoy policies: " + ", ".join(f"`{p}`" for p in evaluation["decoy_policies"]))
    if evaluation.get("final_state"):
        lines.append("- final state after updates (gold action -> state): " + "; ".join(
            f"`{m}` {evaluation['gold'][m]} -> {st}" for m, st in evaluation["final_state"].items()))
    if flags:
        lines += ["", "### C. Automated flags (for review, not verdicts)"]
        lines += [f"- {'HARD' if f.hard else 'soft'} `{f.item}` {f.kind}: \"{f.match}\""
                  + (f" (judge under {FLAG_ITEMS[f.kind]})" if not f.hard and f.kind in FLAG_ITEMS else "")
                  for f in flags]
    lines += ["", "### Checklist (record pass/fail + reason in the CSV)"]
    lines += [f"- [ ] **{c}** {d}" for c, d in CHECKLIST]
    return "\n".join(lines) + "\n"


def write_csv_template(path: Path, scenarios: list[str], reviewer: str = "") -> None:
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, COLUMNS)
        w.writeheader()
        for sid in scenarios:
            w.writerow({"scenario": sid, "reviewer": reviewer})


def read_decisions(path: Path) -> list[dict]:
    """Validated rows: every checklist cell is pass/fail, a fail needs a note, and an
    accepted scenario must pass the semantic-quality items (C8, C10)."""
    rows = []
    with path.open() as f:
        for row in csv.DictReader(f):
            for c, _ in CHECKLIST:
                if row[c] not in {"pass", "fail"}:
                    raise ValueError(f"{row['scenario']}: {c} must be pass/fail, got {row[c]!r}")
            if row["decision"] not in DECISIONS:
                raise ValueError(f"{row['scenario']}: decision must be one of {sorted(DECISIONS)}")
            if any(row[c] == "fail" for c, _ in CHECKLIST) and not row["notes"].strip():
                raise ValueError(f"{row['scenario']}: a failed item needs a reason in notes")
            if row["decision"] == "accept" and any(row[c] != "pass" for c in REQUIRED_FOR_ACCEPT):
                raise ValueError(f"{row['scenario']}: accept requires {' and '.join(REQUIRED_FOR_ACCEPT)} to pass")
            rows.append(row)
    return rows
