"""BeliefGraph core: build the justification graph with an LLM, read updates with an LLM,
and revise with truth-maintenance propagation (beliefbench.labeler, differentially
tested against Veritas-TMS)."""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field

from beliefbench.labeler import gold_actions, topo_order
from beliefgraph.retrieve import entity_names
from beliefbench.schema import Action, Kind, Node, Relation, Scenario, Update
from beliefgraph.prompts import (
    BATCH_NOTE,
    BUILD_PROMPT,
    ADJUDICATE_PROMPT,
    GROUND_PROMPT,
    OUTCOME_PROMPT,
    READ_PROMPT,
    RELIABILITY_PROMPT,
    RETRY_NOTE,
    ROUTE_OUTCOME_PROMPT,
    ROUTE_PROMPT,
    RULE_PARSE_PROMPT,
    SCORE_PROMPT,
    VERIFY_PROMPT,
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
    confidence: dict[str, float] = field(default_factory=dict)  # memory id -> share of routing votes (v0.4)


@dataclass
class UpdateReading:
    target: str
    relation: str  # retracts | supersedes | hedges
    reliability: str


def _load_json(raw: str) -> dict:
    """The JSON object in a model's answer. Small models often wrap it in code fences or break
    the syntax in small ways (doubled or trailing commas); those are repaired, nothing else."""
    text = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    start, end = text.find("{"), text.rfind("}")
    text = text[start : end + 1] if start >= 0 else text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        fixed = re.sub(r",\s*(?=,)", "", text)            # ", ," -> ","
        fixed = re.sub(r",\s*([}\]])", r"\1", fixed)      # trailing commas
        fixed = re.sub(r"([{,]\s*),", r"\1", fixed)        # "{," or ", ," leftovers
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            return json.loads(_balance_brackets(fixed))


def _balance_brackets(text: str) -> str:
    """Close brackets a small model left open: '[["a"]}' -> '[["a"]]}' (outside strings)."""
    out, stack, in_str, esc = [], [], False, False
    pairs = {"{": "}", "[": "]"}
    for ch in text:
        if in_str:
            out.append(ch)
            esc = ch == "\\" and not esc
            if ch == '"' and not esc:
                in_str = False
            continue
        if ch == '"':
            in_str, esc = True, False
        elif ch in pairs:
            stack.append(pairs[ch])
        elif ch in "]}":
            while stack and stack[-1] != ch and ch in stack:
                out.append(stack.pop())  # close what was left open inside
            if stack and stack[-1] == ch:
                stack.pop()
            else:
                continue  # a stray closer
        out.append(ch)
    return "".join(out) + "".join(reversed(stack))


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


def _tie_rank(memory_text: str, policy_text: str) -> float:
    """Higher = less like the policy (used to pick a conflict's loser when votes tie)."""
    from beliefgraph.retrieve import _tokens

    a, b = set(_tokens(memory_text)), set(_tokens(policy_text))
    return -len(a & b) / (len(a) or 1)


def break_cycles(justs: dict[str, list[list[str]]], errors: list[str]) -> None:
    """Drop only the justification sets that close a dependency cycle (in place). Sets are
    admitted one at a time, fact-only sets first; a set that would make a memory depend on
    itself through other memories is dropped and reported, and the rest of the graph stays.
    A memory that also has fact-only support gives way first: it loses an alternative, not
    all of its support."""
    deps: dict[str, set[str]] = {m: set() for m in justs}

    def reaches(a: str, b: str) -> bool:  # does a depend, transitively, on b?
        seen, stack = set(), [a]
        while stack:
            x = stack.pop()
            if x == b:
                return True
            if x not in seen:
                seen.add(x)
                stack += deps.get(x, ())
        return False

    grounded = {m for m, sets in justs.items() if any(not any(x in justs for x in j) for j in sets)}
    order = sorted((n := sum(x in justs for x in j), n > 0 and m in grounded, m, i)
                   for m, sets in justs.items() for i, j in enumerate(sets))
    keep: dict[str, list[int]] = {m: [] for m in justs}
    for *_, m, i in order:
        j = justs[m][i]
        if any(x in justs and reaches(x, m) for x in j):
            errors.append(f"cycle: dropped {m} <- {j}")
            continue
        keep[m].append(i)
        deps[m] |= {x for x in j if x in justs}
    for m in justs:
        justs[m] = [justs[m][i] for i in sorted(keep[m])]


def parse_graph(raw: str, view: dict) -> Graph:
    """Validate the LLM's graph against the snapshot. Unknown ids, self-references and
    empty sets are dropped; cycles are broken by dropping only the sets that close them."""
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
    break_cycles(justs, errors)
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

    v0.3 (``outcome_routing``, off by default: it routed worse): each policy is first split
    into what it gives and what it requires, and routing matches the memory to what it gives.

    v0.4, sample-vote-constrain (after AbsCon, Chen et al. 2025, arXiv 2508.00255): routing and
    grounding are each sampled ``samples`` times (seeded) and aggregated. Policies are tried in
    vote order and accepted only if they ground; a justification set is kept when most samples
    produce it (else the most frequent complete set). Then a store-level constraint: two
    memories that take the same policy on overlapping premises cannot both be right (one is
    usually a downstream conclusion routed to the rule that grants its premise), so the one with
    fewer votes is re-routed with that policy excluded (``resolve_conflicts``; off by default:
    on a 93-memory hard subset it fired once and changed nothing).

    Vote share is calibrated (there, 62% of memories with split votes had a wrong graph, 10%
    of unanimous ones), so split-vote memories get one more step (``adjudicate``): every
    voted policy is grounded and the candidates are compared side by side, each with the
    items that satisfy it.

    v0.5, small-model mode (``route_mode="verify"``, ``entity_ground=True``): every call is an
    easy one. Routing checks the ``k_verify`` nearest policies one by one with a yes/no question
    (in parallel) instead of asking for one choice among many; grounding sees only the items
    that name the memory's entity, topped up with the nearest items to ``k_ground``. On a
    45-memory store, 0.8-4B models picked the right policy among 12 only 24-61% of the time,
    worse than embedding top-1 (62%); the name filter keeps 92-98% of true premises at ~3
    candidates instead of 16.
    """

    def __init__(self, llm: LLM, k_policies: int = 12, k_items: int = 16, k_read: int = 5, workers: int = 8,
                 reliability_batch: int = 40, max_reroutes: int = 2, outcome_routing: bool = False,
                 outcome_batch: int = 20, samples: int = 3, resolve_conflicts: bool = False, conflict_rounds: int = 2,
                 adjudicate: bool = True, route_mode: str = "choose", k_verify: int = 5,
                 entity_ground: bool = False, k_ground: int = 8, conflict_mode: str = "overlap",
                 rule_parse: bool = False):
        super().__init__(llm)
        self.samples, self.resolve_conflicts, self.conflict_rounds = samples, resolve_conflicts, conflict_rounds
        self.adjudicate = adjudicate
        if route_mode not in ("choose", "verify", "score"):
            raise ValueError(f"route_mode must be 'choose', 'verify' or 'score', not {route_mode!r}")
        self.route_mode, self.k_verify, self.entity_ground, self.k_ground = route_mode, k_verify, entity_ground, k_ground
        if conflict_mode not in ("overlap", "entity"):
            raise ValueError(f"conflict_mode must be 'overlap' or 'entity', not {conflict_mode!r}")
        self.conflict_mode = conflict_mode
        self.rule_parse = rule_parse
        self.outcome_routing, self.outcome_batch = outcome_routing, outcome_batch
        self.max_reroutes = max_reroutes
        self.k_policies, self.k_items, self.k_read = k_policies, k_items, k_read
        self.workers, self.reliability_batch = workers, reliability_batch

    def _samples(self, fn):
        """``fn(k)`` for every sample k, concurrently (samples of one memory are independent)."""
        if self.samples == 1:
            return [fn(0)]
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=self.samples) as pool:
            return list(pool.map(fn, range(self.samples)))

    def _map_inner(self, fn, xs):
        """Parallel map for the checks of one memory (kept separate from the memory-level pool)."""
        from concurrent.futures import ThreadPoolExecutor

        if not xs:
            return []
        with ThreadPoolExecutor(max_workers=len(xs)) as pool:
            return list(pool.map(fn, xs))

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

    def _rule_thens(self, view: dict) -> dict[str, str]:
        """{policy id: THEN clause} from one cached parse per rule; the full text on failure."""
        def parse(p):
            try:
                obj = _load_json(self.llm(RULE_PARSE_PROMPT, p["text"], f"{view['scenario']} ruleparse.{p['id']}"))
                then = obj.get("then")
                return p["id"], then.strip() if isinstance(then, str) and then.strip() else p["text"]
            except Exception:  # noqa: BLE001 -- an unusable parse falls back to the full rule
                return p["id"], p["text"]

        return dict(self._map(parse, view.get("policies", [])))

    def _outcomes(self, view: dict) -> tuple[dict[str, dict], list[str]]:
        """{policy id: {"gives", "requires"}}, from batched calls; a policy the model leaves
        out keeps its full text as both."""
        pols = view.get("policies", [])
        chunks = [pols[i : i + self.outcome_batch] for i in range(0, len(pols), self.outcome_batch)]

        def split(args):
            i, chunk = args
            msg = json.dumps({p["id"]: p["text"] for p in chunk}, indent=1)
            try:
                got = _load_json(self.llm(OUTCOME_PROMPT, msg, f"{view['scenario']} outcome{i}")).get("policies") or {}
            except (json.JSONDecodeError, ValueError, AttributeError):
                got = {}
            return {p["id"]: got.get(p["id"]) for p in chunk}

        out, errors = {}, []
        text = {p["id"]: p["text"] for p in pols}
        for part in self._map(split, list(enumerate(chunks))):
            for pid, v in part.items():
                if not (isinstance(v, dict) and isinstance(v.get("gives"), str) and v["gives"].strip()):
                    errors.append(f"{pid}: no outcome split; routing on its full text")
                    v = {"gives": text[pid], "requires": text[pid]}
                out[pid] = {"gives": v["gives"], "requires": str(v.get("requires") or "")}
        return out, errors

    def build(self, view: dict, retry_unsupported: bool = True, batch_size: int | None = None,
              only: list[str] | None = None) -> Graph:
        """``only``: build just these memories (e.g. ones written since the last build); every
        fact and memory of the store stays a candidate premise."""
        from beliefgraph.retrieve import DenseIndex

        sid = view["scenario"]
        facts = {e["id"]: e for e in view["evidence"]}
        mems = {m["id"]: m for m in view["memories"]}
        pols = {p["id"]: p for p in view.get("policies", [])}
        pidx = DenseIndex([(p, x["text"]) for p, x in pols.items()])
        outcomes, oerr = self._outcomes(view) if self.outcome_routing and pols else ({}, [])
        oidx = DenseIndex([(p, o["gives"]) for p, o in outcomes.items()]) if outcomes else None
        # v0.7: each rule parsed once into IF/THEN; routing candidates are ranked by the THEN clause
        # fused with the full text (the router's prompt is unchanged)
        thens = self._rule_thens(view) if self.rule_parse and pols else {}
        tidx = DenseIndex(list(thens.items())) if thens else None

        def rank_policies(text: str) -> list[str]:
            """Reciprocal-rank fusion of outcome and full-text similarity (outcome first)."""
            full = pidx.rank(text)
            if tidx is not None:  # v0.7: THEN clause and full text, equal weight
                score = {p: 0.0 for p in full}
                for ranking in (tidx.rank(text), full):
                    for r, p in enumerate(ranking):
                        score[p] += 1.0 / (10 + r)
                return sorted(full, key=lambda p: -score[p])
            if oidx is None:
                return full
            score = {p: 0.0 for p in full}
            for weight, ranking in ((2.0, oidx.rank(text)), (1.0, full)):
                for r, p in enumerate(ranking):
                    score[p] += weight / (10 + r)
            return sorted(full, key=lambda p: -score[p])
        iidx = DenseIndex([(i, x["text"]) for i, x in {**facts, **mems}.items()])

        def sample_note(base: str, k: int) -> str:
            return base if k == 0 else f"{base}~s{k}"  # sample 0 keeps the v0.2 cache names

        def route(mid: str, ranked: list[str], tried: set[str], tag: str, k: int = 0) -> str | None:
            text = mems[mid]["text"]
            near_facts = [f for f in iidx.rank(text, exclude={mid}) if f in facts][:5]
            pool = [p for p in ranked if p not in tried]
            for tier, cands in enumerate((pool[: self.k_policies], pool[self.k_policies : 2 * self.k_policies])):
                if not cands:
                    break
                shown = ({str(n + 1): {"gives": outcomes[p]["gives"], "requires": outcomes[p]["requires"]}
                          for n, p in enumerate(cands)} if outcomes else
                         {str(n + 1): pols[p]["text"] for n, p in enumerate(cands)})
                msg = json.dumps({"memory": text, "facts_about_it": [facts[f]["text"] for f in near_facts],
                                  "policies": shown}, indent=1)
                try:
                    pick = _load_json(self.llm(ROUTE_OUTCOME_PROMPT if outcomes else ROUTE_PROMPT, msg,
                                               sample_note(f"{sid} route{tag}{tier}.{mid}", k))).get("policy")
                except (json.JSONDecodeError, ValueError, AttributeError):
                    pick = None
                if isinstance(pick, str) and pick.strip().isdigit():
                    pick = int(pick)
                if isinstance(pick, int) and 1 <= pick <= len(cands):
                    return cands[pick - 1]
            return None

        def ground_candidates(mid: str, policy: str) -> list[str]:
            ranked = iidx.rank(mems[mid]["text"] + " " + pols[policy]["text"], exclude={mid})
            if not self.entity_ground:
                return ranked[: self.k_items]
            names = entity_names(mems[mid]["text"])
            named = [i for i in ranked if names & entity_names((facts.get(i) or mems.get(i))["text"])]
            return (named + [i for i in ranked if i not in set(named)])[: max(self.k_ground, len(named))]

        def verify(mid: str, policy: str, tag: str) -> float:
            """Share of samples that answer yes to "did this rule produce this memory?"."""
            msg = json.dumps({"memory": mems[mid]["text"], "rule": pols[policy]["text"]}, indent=1)

            def ask(k):
                try:
                    raw = self.llm(VERIFY_PROMPT, msg, sample_note(f"{sid} verify{tag}.{mid}.{policy}", k))
                except Exception:  # noqa: BLE001 -- one failed check counts as "no"
                    return False
                try:
                    v = str(_load_json(raw).get("answer", "")).strip().lower()
                except (json.JSONDecodeError, ValueError, AttributeError):
                    v = raw.strip().lower()
                return v.startswith("yes")

            got = self._samples(ask)
            return sum(got) / len(got)

        def score(mid: str, policy: str, tag: str) -> float:
            """Mean 0-10 rating of "this rule produced this memory" over samples (unparsable = 0)."""
            msg = json.dumps({"memory": mems[mid]["text"], "rule": pols[policy]["text"]}, indent=1)

            def ask(k):
                try:
                    v = _load_json(self.llm(SCORE_PROMPT, msg, sample_note(f"{sid} score{tag}.{mid}.{policy}", k))).get("score")
                    return min(10.0, max(0.0, float(v)))
                except Exception:  # noqa: BLE001 -- unparsable or failed: no support
                    return 0.0

            got = self._samples(ask)
            return sum(got) / len(got)

        def ground(mid: str, policy: str, tag: str, k: int = 0) -> tuple[list[list[str]], list[str]]:
            text, errs = mems[mid]["text"], []
            cands = ground_candidates(mid, policy)
            msg = json.dumps({"memory": text, "policy": pols[policy]["text"],
                              "candidates": [{"id": c, "kind": "memory" if c in mems else "fact",
                                              "text": (facts.get(c) or mems.get(c))["text"]} for c in cands]}, indent=1)
            try:
                groups = _load_json(self.llm(GROUND_PROMPT, msg, sample_note(f"{sid} ground{tag}.{mid}", k))
                                    ).get("groups") or []
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

        def voted_ground(mid: str, policy: str, tag: str) -> tuple[list[list[str]], list[str]]:
            """Sets produced by most samples; failing that, the most frequent complete sets."""
            counts: dict[tuple, int] = {}
            errs: list[str] = []
            for k, (sets, e) in enumerate(self._samples(lambda k: ground(mid, policy, tag, k))):
                errs += [f"s{k}: {x}" for x in e] if self.samples > 1 else e
                for st in sets:
                    counts[tuple(st)] = counts.get(tuple(st), 0) + 1
            if not counts:
                return [], errs
            top = max(counts.values())
            keep = [st for st, c in counts.items() if 2 * c > self.samples] or \
                   [st for st, c in counts.items() if c == top]
            return [list(st) for st in keep], errs

        def one(mid: str, banned: frozenset = frozenset(), tag0: str = ""):
            """Route (voted), ground the voted policies in order, and when none grounds, re-route
            with them excluded: a decoy or wrong rule cannot be grounded in the facts."""
            ranked, tried, errs = rank_policies(mems[mid]["text"]), set(banned), []
            if self.route_mode == "score":
                # windows of k_verify policies in retrieval order, each rated 0-10; the best-rated
                # ones (ties: retrieval order) are grounded in turn, grounding being the filter
                for w in range(self.max_reroutes + 1):
                    window = [p for p in ranked if p not in tried][: self.k_verify]
                    if not window:
                        break
                    tag = tag0 + ("" if w == 0 else f"w{w}")
                    scores = dict(zip(window, self._map_inner(lambda p: score(mid, p, tag0), window)))
                    order = sorted(window, key=lambda p: (-scores[p], window.index(p)))
                    for policy in order[:2]:
                        if scores[policy] <= 0:
                            break
                        sets, gerrs = voted_ground(mid, policy, tag)
                        errs += gerrs
                        if sets:
                            top = scores[order[0]]
                            margin = top - max([scores[p] for p in order[1:]] or [0])
                            return {"policy": policy, "share": 1.0 if policy == order[0] and margin >= 2 else 0.5,
                                    "sets": sets, "errs": errs, "votes": {}, "tag": tag}
                        errs.append(f"policy {policy} could not be grounded")
                    tried.update(order[:2])
                errs.append("no policy scored and grounded")
                return {"policy": None, "share": 0.0, "sets": [], "errs": errs}
            if self.route_mode == "verify":
                # windows of k_verify policies in retrieval order; within a window, every "yes"
                # (majority of samples) is grounded in order of its yes-share, then rank
                for w in range(self.max_reroutes + 1):
                    window = [p for p in ranked if p not in tried][: self.k_verify]
                    if not window:
                        break
                    tag = tag0 + ("" if w == 0 else f"w{w}")
                    shares = dict(zip(window, self._map_inner(lambda p: verify(mid, p, tag0), window)))
                    yes = sorted((p for p in window if 2 * shares[p] > 1 or (self.samples == 1 and shares[p] == 1)),
                                 key=lambda p: (-shares[p], window.index(p)))
                    for policy in yes:
                        sets, gerrs = voted_ground(mid, policy, tag)
                        errs += gerrs
                        if sets:
                            return {"policy": policy, "share": shares[policy], "sets": sets, "errs": errs,
                                    "votes": {}, "tag": tag}
                        errs.append(f"policy {policy} could not be grounded")
                    tried.update(window)
                errs.append("no policy verified and grounded")
                return {"policy": None, "share": 0.0, "sets": [], "errs": errs}
            for attempt in range(self.max_reroutes + 1):
                tag = tag0 + ("" if attempt == 0 else f"r{attempt}")
                picks = self._samples(lambda k: route(mid, ranked, frozenset(tried), tag, k))
                votes = Counter(p for p in picks if p is not None)
                if not votes:
                    errs.append("no policy routed")
                    break
                for policy, n in votes.most_common():
                    sets, gerrs = voted_ground(mid, policy, tag)
                    errs += gerrs
                    if sets:
                        return {"policy": policy, "share": n / self.samples, "sets": sets, "errs": errs,
                                "votes": dict(votes), "tag": tag}
                    tried.add(policy)
                    errs.append(f"policy {policy} could not be grounded; re-routing")
            return {"policy": None, "share": 0.0, "sets": [], "errs": errs}

        def adjudicate(mid: str) -> dict:
            """Split votes: ground every voted policy and let the model compare them, each with
            the items that satisfy it. Keeps the first choice unless a majority picks another."""
            r = out[mid]
            cands = []
            for policy in sorted(r["votes"], key=lambda p: -r["votes"][p]):
                sets, _ = voted_ground(mid, policy, r["tag"])
                if sets:
                    cands.append((policy, sets))
            if len(cands) < 2:
                return r
            msg = json.dumps({"memory": mems[mid]["text"], "policies": {
                str(n + 1): {"policy": pols[p]["text"],
                             "premises": [(facts.get(x) or mems.get(x))["text"] for x in sorted({x for st in sets for x in st})]}
                for n, (p, sets) in enumerate(cands)}}, indent=1)

            def pick(k):
                try:
                    v = _load_json(self.llm(ADJUDICATE_PROMPT, msg, sample_note(f"{sid} adjudicate.{mid}", k))).get("policy")
                except (json.JSONDecodeError, ValueError, AttributeError):
                    return None
                v = int(v) if isinstance(v, str) and v.strip().isdigit() else v
                return v if isinstance(v, int) and 1 <= v <= len(cands) else None

            votes = Counter(v for v in self._samples(pick) if v is not None)
            if not votes:
                return r
            (best, n), = votes.most_common(1)
            policy, sets = cands[best - 1]
            if policy == r["policy"] or 2 * n <= self.samples:
                return r
            return dict(r, policy=policy, sets=sets, share=n / self.samples,
                        errs=r["errs"] + [f"adjudicated {r['policy']} -> {policy}"])

        todo = [m for m in mems if only is None or m in set(only)]
        out = dict(zip(todo, self._map(one, todo)))
        split = [m for m in todo if out[m]["policy"] and out[m]["share"] < 1] if self.adjudicate and self.samples > 1 else []
        out.update(zip(split, self._map(adjudicate, split)))
        banned: dict[str, set[str]] = {m: set() for m in todo}
        conflict_errs: list[str] = []
        for rnd in range(self.conflict_rounds if self.resolve_conflicts else 0):
            if self.conflict_mode == "entity":
                losers, claimed = self._entity_conflicts(out, mems, pidx)
            else:
                losers, claimed = self._conflict_losers(out, mems, pols), {}
            if not losers:
                break
            for m in losers:
                banned[m].add(out[m]["policy"])
                banned[m] |= claimed.get(m, set())
            redo = self._map(lambda m: one(m, frozenset(banned[m]), f"c{rnd + 1}"), losers)
            for m, r in zip(losers, redo):
                if r["sets"]:
                    conflict_errs.append(f"{m}: conflict on {out[m]['policy']}; re-routed to {r['policy']}")
                    out[m] = r
                else:  # no other policy grounds: keep the original reading rather than nothing
                    conflict_errs.append(f"{m}: conflict on {out[m]['policy']}; no alternative, kept")
        rel, rerr = self._reliability(view)
        justs = {mid: r["sets"] for mid, r in out.items()}
        errors = [f"{mid}: {e}" for mid, r in out.items() for e in r["errs"]] + conflict_errs + rerr + oerr
        break_cycles(justs, errors)
        return Graph(justs, rel, errors, sorted(m for m, sets in justs.items() if not sets),
                     {m: r["share"] for m, r in out.items()})

    @staticmethod
    def _entity_conflicts(out: dict, mems: dict, pidx) -> tuple[list[str], dict[str, set[str]]]:
        """v0.6: for one entity, a policy produces at most one memory. Memories that name a
        common entity form a group; when several in a group hold the same policy, the one with
        the larger vote share keeps it (ties: the one whose retrieval ranks the policy higher)
        and the others lose. Returns the losers and, for each, the policies its group already
        holds (excluded when it is re-routed, so it chooses among unclaimed ones)."""
        names = {m: entity_names(mems[m]["text"]) for m in out}
        parent = {m: m for m in out}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        by_name: dict[str, str] = {}
        for m, ns in names.items():
            for n in ns:
                if n in by_name:
                    parent[find(m)] = find(by_name[n])
                else:
                    by_name[n] = m
        groups: dict[str, list[str]] = {}
        for m in out:
            if out[m]["policy"]:
                groups.setdefault(find(m), []).append(m)
        losers, claimed = [], {}
        for ms in groups.values():
            holders: dict[str, list[str]] = {}
            for m in ms:
                holders.setdefault(out[m]["policy"], []).append(m)
            for policy, hs in holders.items():
                if len(hs) < 2:
                    continue
                rank = {m: (pidx.rank(mems[m]["text"]) + [policy]).index(policy) for m in hs}
                keeper = max(hs, key=lambda m: (out[m]["share"], -rank[m]))
                for m in hs:
                    if m != keeper:
                        losers.append(m)
                        claimed[m] = {out[x]["policy"] for x in ms if x != m}
        return sorted(losers), claimed

    @staticmethod
    def _conflict_losers(out: dict, mems: dict, pols: dict) -> list[str]:
        """Memories that share a policy with another memory on overlapping premises (same
        facts, or one resting on the other): of each such pair, the one with fewer routing votes
        (ties: the one whose text is less like the policy) loses."""
        by_policy: dict[str, list[str]] = {}
        for m, r in out.items():
            if r["policy"]:
                by_policy.setdefault(r["policy"], []).append(m)
        losers = set()
        for policy, ms in by_policy.items():
            if len(ms) < 2:
                continue
            items = {m: {x for st in out[m]["sets"] for x in st} for m in ms}
            for i, a in enumerate(ms):
                for b in ms[i + 1 :]:
                    if not (items[a] & items[b] or a in items[b] or b in items[a]):
                        continue
                    # the memory the other one rests on is the policy's own conclusion
                    if a in items[b]:
                        losers.add(b); continue
                    if b in items[a]:
                        losers.add(a); continue
                    sa, sb = out[a]["share"], out[b]["share"]
                    if sa != sb:
                        losers.add(a if sa < sb else b)
                    else:
                        losers.add(max(a, b, key=lambda m: _tie_rank(mems[m]["text"], pols[policy]["text"])))
        return sorted(losers)

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
