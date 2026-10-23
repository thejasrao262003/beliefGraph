"""BeliefGraph core: build the justification graph with an LLM, read updates with an LLM,
and revise with truth-maintenance propagation (beliefbench.labeler, differentially
tested against Veritas-TMS)."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field

from beliefbench.labeler import gold_actions, topo_order
from beliefbench.schema import Action, Kind, Node, Relation, Scenario, Update
from beliefgraph.prompts import (
    BATCH_NOTE,
    BUILD_PROMPT,
    GROUND_PROMPT,
    READ_PROMPT,
    RELIABILITY_PROMPT,
    RETRY_NOTE,
    ROUTE_PROMPT,
)

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
            items = [x for x in (j if isinstance(j, list) else [j])
                     if isinstance(x, str) and x in facts | mems and x != mid]  # small models emit odd shapes
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


class DecomposedBeliefGraph(BeliefGraph):
    """v0.2: build the graph one memory at a time from small, constrained decisions, so a
    small model never has to read the whole store.

    - reliability: source descriptions rated in batches;
    - route: the memory's policy chosen from the ``k_policies`` nearest (dense retrieval),
      with a second, wider tier if the model says none fits;
    - ground: that policy split into OR-of-AND conditions, each matched to one of the
      ``k_items`` nearest facts and memories (ids only), assembled into justification sets;
    - read: each update read against its ``k_read`` nearest facts.
    """

    def __init__(self, llm: LLM, k_policies: int = 12, k_items: int = 16, k_read: int = 5, workers: int = 8,
                 reliability_batch: int = 40, max_reroutes: int = 2):
        super().__init__(llm)
        self.max_reroutes = max_reroutes
        self.k_policies, self.k_items, self.k_read = k_policies, k_items, k_read
        self.workers, self.reliability_batch = workers, reliability_batch

    def _map(self, fn, xs):
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            return list(pool.map(fn, xs))

    def _reliability(self, view: dict) -> tuple[dict, list[str]]:
        facts = view["evidence"]
        chunks = [facts[i : i + self.reliability_batch] for i in range(0, len(facts), self.reliability_batch)]

        def rate(args):
            i, chunk = args
            msg = json.dumps([{"id": e["id"], "source": e["source"]} for e in chunk], indent=1)
            try:
                got = (_load_json(self.llm(RELIABILITY_PROMPT, msg, f"{view['scenario']} rel{i}")).get("reliability")
                       or {})
            except (json.JSONDecodeError, ValueError):
                got = {}
            return {e["id"]: got.get(e["id"]) for e in chunk}

        rel, errors = {}, []
        for part in self._map(rate, list(enumerate(chunks))):
            for fid, v in part.items():
                if v not in LEVELS:
                    errors.append(f"{fid}: reliability {v!r} -> high")
                    v = "high"
                rel[fid] = v
        return rel, errors

    def build(self, view: dict, retry_unsupported: bool = True, batch_size: int | None = None) -> Graph:
        from beliefgraph.retrieve import DenseIndex

        sid = view["scenario"]
        facts = {e["id"]: e for e in view["evidence"]}
        mems = {m["id"]: m for m in view["memories"]}
        pols = {p["id"]: p for p in view.get("policies", [])}
        pidx = DenseIndex([(p, x["text"]) for p, x in pols.items()])
        iidx = DenseIndex([(i, x["text"]) for i, x in {**facts, **mems}.items()])

        def route(mid: str, ranked: list[str], tried: set[str], tag: str) -> str | None:
            text = mems[mid]["text"]
            near_facts = [f for f in iidx.rank(text, exclude={mid}) if f in facts][:5]
            pool = [p for p in ranked if p not in tried]
            for tier, cands in enumerate((pool[: self.k_policies], pool[self.k_policies : 2 * self.k_policies])):
                if not cands:
                    break
                msg = json.dumps({"memory": text, "facts_about_it": [facts[f]["text"] for f in near_facts],
                                  "policies": {str(n + 1): pols[p]["text"] for n, p in enumerate(cands)}}, indent=1)
                try:
                    pick = _load_json(self.llm(ROUTE_PROMPT, msg, f"{sid} route{tag}{tier}.{mid}")).get("policy")
                except (json.JSONDecodeError, ValueError, AttributeError):
                    pick = None
                if isinstance(pick, str) and pick.strip().isdigit():
                    pick = int(pick)
                if isinstance(pick, int) and 1 <= pick <= len(cands):
                    return cands[pick - 1]
            return None

        def ground(mid: str, policy: str, tag: str) -> tuple[list[list[str]], list[str]]:
            text, errs = mems[mid]["text"], []
            cands = iidx.rank(text + " " + pols[policy]["text"], exclude={mid})[: self.k_items]
            msg = json.dumps({"memory": text, "policy": pols[policy]["text"],
                              "candidates": [{"id": c, "kind": "memory" if c in mems else "fact",
                                              "text": (facts.get(c) or mems.get(c))["text"]} for c in cands]}, indent=1)
            try:
                groups = _load_json(self.llm(GROUND_PROMPT, msg, f"{sid} ground{tag}.{mid}")).get("groups") or []
            except (json.JSONDecodeError, ValueError, AttributeError) as e:
                return [], [f"ground: invalid JSON: {e}"]
            sets = []
            for g in groups if isinstance(groups, list) else []:
                # Accept {"all_of": [...]} or a bare list; conditions as {"item": id} or bare ids.
                conds = g.get("all_of") if isinstance(g, dict) else g if isinstance(g, list) else None
                items = [c.get("item") if isinstance(c, dict) else c for c in conds or []]
                if not items or any(not isinstance(x, str) or x not in cands for x in items):
                    errs.append(f"dropped a group with an unmatched condition: {items}")
                    continue  # an alternative with an unmet condition supports nothing
                key = sorted(set(items))
                if key not in sets:
                    sets.append(key)
            return sets, errs

        def one(mid: str) -> tuple[str, list[list[str]], list[str]]:
            """Route, ground, and when grounding finds no complete justification, re-route with
            that policy excluded: a decoy or wrong rule cannot be grounded in the facts."""
            ranked, tried, errs = pidx.rank(mems[mid]["text"]), set(), []
            for attempt in range(self.max_reroutes + 1):
                tag = "" if attempt == 0 else f"r{attempt}"
                policy = route(mid, ranked, tried, tag)
                if policy is None:
                    errs.append("no policy routed")
                    break
                sets, gerrs = ground(mid, policy, tag)
                errs += gerrs
                if sets:
                    return mid, sets, errs
                tried.add(policy)
                errs.append(f"policy {policy} could not be grounded; re-routing")
            return mid, [], errs

        results = self._map(one, list(mems))
        rel, rerr = self._reliability(view)
        justs = {mid: sets for mid, sets, _ in results}
        errors = [f"{mid}: {e}" for mid, _, errs in results for e in errs] + rerr
        try:
            topo_order(sorted(set(facts) | set(mems)), justs)
        except ValueError as e:
            errors.append(f"cycle: {e}")
            for mid in [m for m in mems if m in str(e)]:
                justs[mid] = []
        return Graph(justs, rel, errors, sorted(m for m, sets in justs.items() if not sets))

    def read_updates(self, view: dict) -> tuple[dict[str, UpdateReading], list[str]]:
        from beliefgraph.retrieve import facts_near

        def one(u):
            small = facts_near(view, u["text"], self.k_read) | {"updates": [u]}
            return parse_readings(self.llm(READ_PROMPT, read_message(small), f"{view['scenario']} read.{u['id']}"), small)

        readings, errors = {}, []
        for r, e in self._map(one, view["updates"]):
            readings.update(r)
            errors += e
        return readings, errors
