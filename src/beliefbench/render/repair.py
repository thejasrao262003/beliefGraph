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
_RECORDS_NOTE = """\
A field path that names a record ("facts.<id>" or "conditions.<id>") is replaced as a whole \
JSON value of the same shape (an object for facts, a list for conditions). After the repair, \
the texts and the records must agree with each other.
"""


def repair_prompt(version: str) -> str:
    """The repair system prompt for a rendering made under ``version``."""
    from beliefbench.render.prompt import RECORD_VERSIONS

    return PROMPTS[version] + "\n" + _REPAIR_INSTRUCTIONS + (_RECORDS_NOTE if version in RECORD_VERSIONS else "")


REPAIR_PROMPTS = {REPAIR_VERSION: repair_prompt("render-v8")}


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


def _parts(path: str) -> list:
    return [int(p[1:-1]) if p.startswith("[") else p for p in re.findall(r"[^.\[\]]+|\[\d+\]", path)]


def get_path(obj, path: str):
    for key in _parts(path):
        obj = obj[key]
    return obj


def _under(path: str, permitted: set[str]) -> bool:
    return any(path == p or path.startswith(p + ".") or path.startswith(p + "[") for p in permitted)


def _set(obj: dict, path: str, value) -> None:
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
    "record_scope_mismatch": "the fact's scope must be the scope the condition requires",
    "record_condition_not_met": "the fact's value must satisfy the condition's threshold",
    "relation_not_stated_in_fact": "a fact about a related entity must state the relation inside the fact",
    "record_outcome_mismatch": "after_updates must follow from the records and the updates",
    "final_state_mismatch": "after_updates must follow from the policies and the credible facts: a weak-source "
                            "retraction or hedge of the only support leaves the conclusion undetermined, never fails",
    "recompute_unresolved": "after_updates must resolve to holds or fails here",
    "update_window_introduced": "an update replacing a figure stated without a time window must not introduce one",
    "or_alternatives_same_condition": "alternative justification sets must rest on different quantities or credentials, "
                                      "not two measurements of the same quantity against one condition",
}
# Record-check kinds (render-v9+): the problem can sit in a text or in its record, so the
# repair may change the texts and records of the items involved, and nothing else.
_RECORD_PREFIXES = ("record_", "relation_not_stated", "conclusion_about_other", "update_entity_", "update_kind_",
                    "update_quantity_", "update_unit_", "update_scope_")


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

    has_records = "facts" in response and "conditions" in response
    node_of = inv

    def record_paths(f) -> list[str]:
        if "->" in f.item:
            p, m = (node_of.get(x) for x in f.item.split("->"))
            if p is None or m is None:
                raise ValueError(f"cannot map flagged item {f.item!r}")
            paths = [f"policies.{m}", f"conditions.{m}"]
            if p in response["facts"]:
                sec = "updates" if p.startswith("U") else "nodes"
                paths += [f"facts.{p}", f"{sec}.{p}.text", f"{sec}.{p}.source"]
            if f.kind == "record_entity_not_in_memory":
                paths.append(f"nodes.{m}.text")
            return paths
        x = node_of.get(f.item)
        if x is None:
            raise ValueError(f"cannot map flagged item {f.item!r}")
        if f.kind == "record_outcome_mismatch":
            return [f"after_updates.{x}", f"conditions.{x}", f"policies.{x}"]
        if x.startswith("U") and f.kind.startswith("update_"):  # an update disagreeing with its target
            target = node_of[evaluation["update_targets"][f.item]["target"]]
            return [f"facts.{x}", f"updates.{x}.text", f"updates.{x}.source", f"facts.{target}"]
        # A fact's text and its source description move together, so a repair cannot make
        # the text cite a different body than its source (fix-f6-v10-a).
        sec = "updates" if x.startswith("U") else "nodes"
        return [f"facts.{x}", f"{sec}.{x}.text", f"{sec}.{x}.source"]

    def semantic_paths(f) -> list[str]:  # render-v11 kinds
        x = node_of.get(f.item)
        if x is None:
            raise ValueError(f"cannot map flagged item {f.item!r}")
        if f.kind == "update_window_introduced":
            return [f"updates.{x}.text", f"updates.{x}.source"] + ([f"facts.{x}"] if has_records else [])
        # The after-update judgement, and the updates whose wording it depends on, so a
        # repair cannot just flip the label while the text says otherwise.
        return [f"after_updates.{x}"] + [p for u in response.get("updates", {}) for p in
                                         (f"updates.{u}.text", f"updates.{u}.source")]

    out: dict[str, str] = {}
    for f in flags:
        if not f.hard:
            continue
        why = f"{f.kind} '{f.match}'" + (f" ({WHY[f.kind]})" if f.kind in WHY else "")
        if f.kind == "or_alternatives_same_condition":  # "pa|pb->m": both facts, their records, the policy
            premises, m = f.item.split("->")
            mm = node_of[m]
            paths = [f"policies.{mm}", f"conditions.{mm}"]
            for p in premises.split("|"):
                pp = node_of[p]
                paths += [f"nodes.{pp}.text", f"nodes.{pp}.source", f"facts.{pp}"]
            for path in paths:
                out[path] = (out[path] + "; " if path in out else "") + why
            continue
        if f.kind in ("final_state_mismatch", "recompute_unresolved", "update_window_introduced"):
            for path in semantic_paths(f):
                out[path] = (out[path] + "; " if path in out else "") + why
            continue
        if has_records and f.kind.startswith(_RECORD_PREFIXES):
            for path in record_paths(f):
                out[path] = (out[path] + "; " if path in out else "") + why
            continue
        if "~" in f.item:  # echo / window pairs: the policy side is the one to reword
            target = f.item.split("~")[1]
        elif "->" in f.item:  # premise -> memory: the premise must name the memory's entity
            target = f.item.split("->")[0]
        else:
            target = f.item
        path = path_of(target, f.match)
        out[path] = (out[path] + "; " if path in out else "") + why
    return out


def repair_message(response: dict, problems: dict[str, str]) -> str:
    fields = "\n".join(f'- "{p}": current value {json.dumps(get_path(response, p))}; problem: {why}'
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
        try:
            old = get_path(response, p)
        except (KeyError, IndexError, TypeError):
            errors.append(f"{p}: no such field in the frozen response")
            continue
        if isinstance(old, str) and (not isinstance(v, str) or not v.strip()):
            errors.append(f"{p}: replacement must be non-empty text")
        elif not isinstance(old, str) and type(v) is not type(old):
            errors.append(f"{p}: replacement must be a {type(old).__name__} like the original")
    if errors:
        return None, errors
    merged = copy.deepcopy(response)
    for p, v in repl.items():
        _set(merged, p, v.strip() if isinstance(v, str) else v)
    outside = {c for c in changed_paths(response, merged) if not _under(c, set(problems))}
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
