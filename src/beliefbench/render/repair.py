"""Targeted repair of a rejected rendering (approved in design 2026-10-20 after pilot-3).

A retry under render_run rewrites the whole scenario, so fixing one flagged phrase re-rolls
every other check (pilot-3 F1: attempt 2 was a different world with a new hard failure).
A repair instead keeps the rejected response frozen and lets the model replace only the
fields that carry a hard flag:

1. ``editable_paths`` maps each hard flag to one field of the original response JSON
   ("decoy_policies[0]", "nodes.B2.text", "policies.B1", ...).
2. ``repair_message`` sends the frozen response, the problems and the editable fields.
   The model must answer ``{"replacements": {path: text}}`` for exactly those fields.
3. ``apply_repair`` merges the replacements into the frozen response and refuses the
   result unless every changed field is one of the editable fields.
4. The caller re-parses the merged response and re-runs every hard check, unchanged.
"""

from __future__ import annotations

import copy
import json
import re

from beliefbench.render import leakcheck
from beliefbench.render.prompt import PROMPTS

REPAIR_VERSION = "repair-v1"
REPAIR_TEMPERATURE = 0.3  # a repair should change as little as possible

_REPAIR_INSTRUCTIONS = """\
TASK FOR THIS CALL: REPAIR, NOT A NEW RENDERING. The OUTPUT section above does not apply.

You receive a scenario you previously wrote (as JSON), the problems an automated check \
found in it, and the exact list of fields you may change. Write new text for each listed \
field so that every listed problem is fixed. Change nothing else.

The new text must:
- keep the same role in the scenario: a decoy policy still governs nothing here (an \
outcome no memory states, conditions that offer no route to any memory's conclusion, no \
entity from the scenario); a memory still states the same conclusion; a fact still \
states the same fact with the same value; a policy still states the same rule;
- follow every rule above that applies to that kind of text;
- not introduce any new problem of the kinds listed.

OUTPUT: a single JSON object, no prose, exactly:
{"replacements": {"<field path>": "<new text>"}}
with one entry for each listed field path and no other entries.
"""
REPAIR_PROMPTS = {REPAIR_VERSION: PROMPTS["render-v8"] + "\n" + _REPAIR_INSTRUCTIONS}


def load_response(raw: str) -> dict:
    return json.loads(raw.strip().removeprefix("```json").removesuffix("```").strip())


def _flatten(obj, prefix: str = "") -> dict[str, object]:
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            out |= _flatten(v, f"{prefix}.{k}" if prefix else str(k))
        return out
    if isinstance(obj, list):
        out = {}
        for i, v in enumerate(obj):
            out |= _flatten(v, f"{prefix}[{i}]")
        return out
    return {prefix: obj}


def changed_paths(before: dict, after: dict) -> set[str]:
    a, b = _flatten(before), _flatten(after)
    return {p for p in a.keys() | b.keys() if a.get(p) != b.get(p)}


def _set(obj: dict, path: str, value: str) -> None:
    parts = re.findall(r"[^.\[\]]+|\[\d+\]", path)
    cur = obj
    for i, part in enumerate(parts):
        last = i == len(parts) - 1
        key = int(part[1:-1]) if part.startswith("[") else part
        if last:
            if isinstance(key, int):
                if not (isinstance(cur, list) and 0 <= key < len(cur)):
                    raise KeyError(path)
            elif not (isinstance(cur, dict) and key in cur):
                raise KeyError(path)
            cur[key] = value
        else:
            cur = cur[key]


# Plain-language reason sent with each flag kind (the match itself may be a word stem).
WHY = {
    "decoy_shares_memory_word": "a decoy policy may not use any distinctive word that appears in a memory, "
                                "in any form or sense",
    "reliability_word": "the word 'reliability' may not appear in any text",
    "label_word": "graph or label vocabulary may not appear in any text",
    "graph_id": "item ids may not appear in any text",
    "reliability_label": "a source may not carry a bare high/medium/low label",
    "policy_echoes_memory": "a policy may not share a 3-word phrase with any memory",
    "premise_about_other_entity": "a supporting fact must name the entity of the conclusion it supports, "
                                  "or state its relation to it inside the same fact",
    "update_window_mismatch": "an update must state its value over the same time window as the original fact",
    "fact_policy_window_mismatch": "a condition must use the same time window as the fact it is compared with",
}


def editable_paths(flags: list[leakcheck.Flag], evaluation: dict, response: dict) -> dict[str, str]:
    """Field path -> problem description, for every hard flag. A flag that cannot be mapped
    to exactly one field raises: such a rendering is not repairable by this mechanism."""
    inv = {v: k for k, v in evaluation["idmap"].items()}
    policy_node = {pid: inv[mid] for pid, mid in (evaluation.get("policy_of") or {}).items()}
    decoy_index = {pid: i for i, pid in enumerate(evaluation.get("decoy_policies") or [])}

    def path_of(opaque: str, match: str) -> str:
        if opaque in decoy_index:
            return f"decoy_policies[{decoy_index[opaque]}]"
        if opaque in policy_node:
            return f"policies.{policy_node[opaque]}"
        orig = inv.get(opaque)
        if orig is None:
            raise ValueError(f"cannot map flagged item {opaque!r} to a response field")
        section = "updates" if orig.startswith("U") else "nodes"
        item = response[section][orig]
        field = "source" if match and match not in item.get("text", "") and match in item.get("source", "") else "text"
        return f"{section}.{orig}.{field}"

    out: dict[str, str] = {}
    for f in flags:
        if not f.hard:
            continue
        if "~" in f.item:  # echo / window pairs: the policy side is the one to reword
            target = f.item.split("~")[1]
        elif "->" in f.item:  # premise -> memory: the premise must name the memory's entity
            target = f.item.split("->")[0]
        else:
            target = f.item
        path = path_of(target, f.match)
        why = f"{f.kind} '{f.match}'" + (f" ({WHY[f.kind]})" if f.kind in WHY else "")
        out[path] = (out[path] + "; " if path in out else "") + why
    return out


def repair_message(response: dict, problems: dict[str, str]) -> str:
    fields = "\n".join(f'- "{p}": current text {json.dumps(_flatten(response)[p])}; problem: {why}'
                       for p, why in sorted(problems.items()))
    return ("Repair this scenario.\n\nSCENARIO (as you wrote it):\n" + json.dumps(response, indent=1)
            + "\n\nFIELDS YOU MAY CHANGE, AND WHY:\n" + fields)


def apply_repair(response: dict, repair_raw: str, problems: dict[str, str]) -> tuple[dict | None, list[str]]:
    """Merge the model's replacements into a copy of the frozen response. Returns
    (merged, errors); merged is None if the repair is not exactly the permitted edit."""
    try:
        obj = load_response(repair_raw)
    except json.JSONDecodeError as e:
        return None, [f"repair is not valid JSON: {e}"]
    if not isinstance(obj, dict) or set(obj) != {"replacements"} or not isinstance(obj["replacements"], dict):
        return None, ['repair must be exactly {"replacements": {...}}']
    repl = obj["replacements"]
    errors = []
    if set(repl) != set(problems):
        errors.append(f"replacement fields {sorted(repl)} != permitted fields {sorted(problems)}")
    for p, v in repl.items():
        if not isinstance(v, str) or not v.strip():
            errors.append(f"{p}: replacement must be non-empty text")
    if errors:
        return None, errors
    merged = copy.deepcopy(response)
    for p, v in repl.items():
        try:
            _set(merged, p, v.strip())
        except (KeyError, IndexError, TypeError):
            return None, [f"{p}: no such field in the frozen response"]
    outside = changed_paths(response, merged) - set(problems)
    if outside:
        return None, [f"changes outside the permitted fields: {sorted(outside)}"]
    return merged, []


def plan(s, base_raw: str, prompt_version: str, seed: int = 0) -> tuple[dict, dict, dict, dict[str, str]]:
    """Parse the frozen base exactly as the pipeline does and map its hard flags to fields.
    Returns (response, system, evaluation, problems)."""
    from beliefbench.render.prompt import parse_response
    from beliefbench.render.views import build_views

    r = parse_response(s, base_raw, version=prompt_version)
    if not r.ok:
        raise ValueError(f"base does not parse: {r.errors}")
    system, evaluation = build_views(s, r, seed=seed)
    flags = leakcheck.hard_flags(system, evaluation, prompt_version)
    return load_response(base_raw), system, evaluation, editable_paths(flags, evaluation, load_response(base_raw))


def verify(s, merged: dict, prompt_version: str, seed: int = 0):
    """Re-parse the merged response and re-run every hard check, unchanged.
    Returns (rendering, system, evaluation, hard_flags)."""
    from beliefbench.render.prompt import parse_response
    from beliefbench.render.views import build_views

    r = parse_response(s, json.dumps(merged), version=prompt_version)
    if not r.ok:
        return r, None, None, [leakcheck.Flag("-", "-", "parse_error", "; ".join(r.errors), True)]
    system, evaluation = build_views(s, r, seed=seed)
    return r, system, evaluation, leakcheck.hard_flags(system, evaluation, prompt_version)
