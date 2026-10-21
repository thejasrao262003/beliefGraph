"""BeliefGraph core: build the justification graph with an LLM, read updates with an LLM,
and revise with truth-maintenance propagation (beliefbench.labeler, differentially
tested against Veritas-TMS)."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field

from beliefbench.labeler import gold_actions, topo_order
from beliefbench.schema import Action, Kind, Node, Relation, Scenario, Update
from beliefgraph.prompts import BATCH_NOTE, BUILD_PROMPT, READ_PROMPT, RETRY_NOTE

LEVELS = ("high", "medium", "low")
RELATIONS = {r.value for r in Relation}
# An LLM caller: (system prompt, user message, note) -> response text.
LLM = Callable[[str, str, str], str]


@dataclass
class Graph:
    justifications: dict[str, list[list[str]]]  # memory id -> OR of AND sets
    reliability: dict[str, str]  # fact id -> high | medium | low
    errors: list[str] = field(default_factory=list)
    unsupported: list[str] = field(default_factory=list)  # memories still without any justification


@dataclass
class UpdateReading:
    target: str
    relation: str  # retracts | supersedes | hedges
    reliability: str


def _load_json(raw: str) -> dict:
    text = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start : end + 1] if start >= 0 else text)


def build_message(view: dict) -> str:
    """The memory snapshot the LLM sees: facts, memories and policies, never updates."""
    return json.dumps({
        "facts": [{"id": e["id"], "observed": e["observed"], "source": e["source"], "text": e["text"]}
                  for e in view["evidence"]],
        "memories": [{"id": m["id"], "text": m["text"]} for m in view["memories"]],
        "policies": [p["text"] for p in view.get("policies", [])],
    }, indent=1)


def read_message(view: dict) -> str:
    return json.dumps({
        "facts": [{"id": e["id"], "observed": e["observed"], "source": e["source"], "text": e["text"]}
                  for e in view["evidence"]],
        "updates": [{"id": u["id"], "observed": u["observed"], "source": u["source"], "text": u["text"]}
                    for u in view["updates"]],
    }, indent=1)


def parse_graph(raw: str, view: dict) -> Graph:
    """Validate the LLM's graph against the snapshot. Unknown ids, self-references and
    empty sets are dropped; cycles are broken by removing the cycle members' sets (they
    are then treated as unsupported claims, which propagation leaves standing)."""
    facts = {e["id"] for e in view["evidence"]}
    mems = {m["id"] for m in view["memories"]}
    errors: list[str] = []
    try:
        obj = _load_json(raw)
    except (json.JSONDecodeError, ValueError) as e:
        return Graph({}, {}, [f"invalid JSON: {e}"])
    justs: dict[str, list[list[str]]] = {}
    for mid in mems:
        sets = (obj.get("justifications") or {}).get(mid)
        if sets is None:
            errors.append(f"{mid}: no justifications given")
            sets = []
        clean = []
        for j in sets if isinstance(sets, list) else []:
            items = [x for x in (j if isinstance(j, list) else [j]) if x in facts | mems and x != mid]
            if len(items) != len(j if isinstance(j, list) else [j]):
                errors.append(f"{mid}: dropped unknown or self ids in {j}")
            if items and sorted(set(items)) not in [sorted(c) for c in clean]:
                clean.append(sorted(set(items)))
        justs[mid] = clean
    try:
        topo_order(sorted(facts | mems), justs)
    except ValueError as e:
        errors.append(f"cycle: {e}")
        for mid in [m for m in mems if m in str(e)]:
            justs[mid] = []
    rel = {}
    for fid in facts:
        v = (obj.get("reliability") or {}).get(fid)
        if v not in LEVELS:
            errors.append(f"{fid}: reliability {v!r} -> high")
            v = "high"
        rel[fid] = v
    return Graph(justs, rel, errors)


def parse_readings(raw: str, view: dict) -> tuple[dict[str, UpdateReading], list[str]]:
    facts = {e["id"] for e in view["evidence"]}
    errors: list[str] = []
    try:
        obj = _load_json(raw).get("updates") or {}
    except (json.JSONDecodeError, ValueError) as e:
        return {}, [f"invalid JSON: {e}"]
    out = {}
    for u in view["updates"]:
        r = obj.get(u["id"]) or {}
        target, relation, rel = r.get("target"), r.get("relation"), r.get("reliability")
        if target not in facts:
            errors.append(f"{u['id']}: unknown target {target!r}; update ignored")
            continue
        if relation not in RELATIONS:
            errors.append(f"{u['id']}: relation {relation!r} -> hedges")
            relation = "hedges"
        if rel not in LEVELS:
            errors.append(f"{u['id']}: reliability {rel!r} -> medium")
            rel = "medium"
        out[u["id"]] = UpdateReading(target, relation, rel)
    return out, errors


def _time(view: dict) -> dict[str, int]:
    """Observation order: evidence and updates ranked by their observed dates."""
    dates = sorted({x["observed"] for x in view["evidence"] + view["updates"]})
    return {x["id"]: dates.index(x["observed"]) + 1 for x in view["evidence"] + view["updates"]}


def as_scenario(view: dict, justifications: dict, reliability: dict, readings: dict[str, UpdateReading]) -> Scenario:
    t = _time(view)
    nodes = [Node(e["id"], Kind.EVIDENCE, t=t[e["id"]], reliability=reliability.get(e["id"], "high"))
             for e in view["evidence"]]
    nodes += [Node(m["id"], Kind.BELIEF, justifications=justifications.get(m["id"], [])) for m in view["memories"]]
    updates = [Update(uid, t[uid], r.target, Relation(r.relation), reliability=r.reliability)
               for uid, r in readings.items()]
    return Scenario(view["scenario"], "", view.get("domain", ""), nodes, updates)


def revise(view: dict, justifications: dict, reliability: dict, readings: dict[str, UpdateReading]) -> dict[str, Action]:
    """Selective revision: each memory's action after the updates, by propagation over the
    graph (a memory stays supported while any one justification set is intact)."""
    s = as_scenario(view, justifications, reliability, readings)
    return gold_actions(s, justifications)


class BeliefGraph:
    """The two LLM steps. ``llm(system_prompt, message, note) -> text``."""

    def __init__(self, llm: LLM):
        self.llm = llm

    def build(self, view: dict, retry_unsupported: bool = True, batch_size: int | None = None) -> Graph:
        """Build the graph. A memory left with no justification is asked about once more on
        its own (v0.1); any still unsupported is reported in ``Graph.unsupported`` rather than
        silently treated as established. With ``batch_size``, memories are built in batches
        (every fact and memory stays a candidate premise), for stores too large for one answer."""
        mems = [m["id"] for m in view["memories"]]
        if batch_size and len(mems) > batch_size:
            base = json.loads(build_message(view))
            graph = None
            for i in range(0, len(mems), batch_size):
                chunk = mems[i : i + batch_size]
                message = json.dumps(base | {"build_for": chunk}, indent=1) + "\n\n" + BATCH_NOTE
                part = parse_graph(self.llm(BUILD_PROMPT, message, f"{view['scenario']} build{i // batch_size}"), view)
                if graph is None:
                    graph = Graph({}, part.reliability, [])  # reliabilities from the first batch
                graph.justifications.update({m: part.justifications.get(m, []) for m in chunk})
                graph.errors += [e for e in part.errors if e.split(":")[0] in chunk]
        else:
            graph = parse_graph(self.llm(BUILD_PROMPT, build_message(view), f"{view['scenario']} build"), view)
        empty = sorted(m for m, sets in graph.justifications.items() if not sets)
        if empty and retry_unsupported:
            message = json.dumps(json.loads(build_message(view)) | {"unsupported": empty}, indent=1) + "\n\n" + RETRY_NOTE
            again = parse_graph(self.llm(BUILD_PROMPT, message, f"{view['scenario']} retry"), view)
            for m in empty:
                if again.justifications.get(m):
                    graph.justifications[m] = again.justifications[m]
            graph.errors += [f"retry: {e}" for e in again.errors if e.split(":")[0] in empty]
        graph.unsupported = sorted(m for m, sets in graph.justifications.items() if not sets)
        return graph

    def read_updates(self, view: dict) -> tuple[dict[str, UpdateReading], list[str]]:
        if not view["updates"]:
            return {}, []
        return parse_readings(self.llm(READ_PROMPT, read_message(view), f"{view['scenario']} read"), view)
