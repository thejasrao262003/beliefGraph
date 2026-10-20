"""LLM baseline without a graph: the same model, the same snapshot and updates, the same
label definitions, but it decides each memory's action directly (spec S3/S6: flat LLM
memory that re-reads everything). This is the comparison BeliefGraph has to beat."""

from __future__ import annotations

import json

from beliefbench.schema import Action
from beliefgraph.core import _load_json

DIRECT_VERSION = "llm-direct-v1"

DIRECT_PROMPT = """\
You manage an AI assistant's memory. You receive the facts it had observed (id, observed \
date, source, text), the memories it stored earlier (conclusions or plans), the policies \
(general rules) it applies, and UPDATES that arrived later (id, observed date, source, text).

Decide, for every memory, what should happen to it now that the updates have arrived:
- "keep": it still follows from credible facts under the policies. A memory that still has \
at least one complete line of support is kept, even if another of its supports was lost.
- "withdraw": a fact it needed was credibly shown to be false (retracted) and nothing else \
supports it.
- "recompute": a fact it needed was credibly replaced by a new value or state (whatever \
the new value is), and nothing else supports it, so it has to be worked out again.
- "uncertain": a fact it needed is now only in doubt (the update is hedged or comes from a \
source less reliable than the original fact) and nothing else supports it.
An update that is older than the fact it concerns has no effect. A memory that rests on \
another memory is affected the same way that memory is.

OUTPUT: a single JSON object, no prose:
{"actions": {"<memory id>": "keep" | "withdraw" | "recompute" | "uncertain"}}
Every memory id must appear exactly once.
"""


def direct_message(view: dict) -> str:
    return json.dumps({
        "facts": [{"id": e["id"], "observed": e["observed"], "source": e["source"], "text": e["text"]}
                  for e in view["evidence"]],
        "memories": [{"id": m["id"], "text": m["text"]} for m in view["memories"]],
        "policies": [p["text"] for p in view.get("policies", [])],
        "updates": [{"id": u["id"], "observed": u["observed"], "source": u["source"], "text": u["text"]}
                    for u in view["updates"]],
    }, indent=1)


def parse_direct(raw: str, view: dict) -> tuple[dict[str, Action], list[str]]:
    errors: list[str] = []
    try:
        obj = _load_json(raw).get("actions") or {}
    except (json.JSONDecodeError, ValueError) as e:
        obj, errors = {}, [f"invalid JSON: {e}"]
    out = {}
    for m in view["memories"]:
        v = obj.get(m["id"])
        try:
            out[m["id"]] = Action(v)
        except ValueError:
            errors.append(f"{m['id']}: action {v!r} -> keep")
            out[m["id"]] = Action.KEEP
    return out, errors


def llm_direct(llm, view: dict) -> tuple[dict[str, Action], list[str]]:
    return parse_direct(llm(DIRECT_PROMPT, direct_message(view), f"{view['scenario']} direct"), view)
