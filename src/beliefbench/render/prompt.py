"""Renderer prompt, input payload and response validation.

The renderer sees the full graph (it has to, to write text that respects it). Its
output is split by ``views.py``: the evaluated system only ever sees the system view.

render-v2 (2026-10-18) adds visible *policies*: one general rule per derived node,
so the AND/OR structure is determinable from what the system sees (smoke test 1, P1).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from beliefbench.render.views import timeline
from beliefbench.schema import Scenario

PROMPT_VERSION = "render-v2"

SYSTEM_PROMPT = """\
You write test data for a research benchmark on how AI assistants revise conclusions \
they stored in memory when new information arrives. You receive an abstract dependency \
graph and a domain. Invent a small, realistic situation in that domain and write text \
for every item so that the logical structure below holds EXACTLY.

ITEM TYPES
- evidence: an observed fact, reported by a source. Write the fact (one or two \
sentences) and a short source description.
- belief: a conclusion the assistant previously drew and saved to memory.
- decision: a recommendation or plan the assistant previously saved to memory.
- policy: for EVERY belief and decision, one general rule that governs it (see POLICIES).

LOGICAL STRUCTURE (the most important rules)
- Each derived item lists one or more justification sets. For EVERY set, the facts in \
that set taken TOGETHER must be sufficient to conclude the item.
- Inside a set, EVERY fact must be necessary: if any one of them were false, that set \
would no longer support the conclusion.
- Different sets for the same item must each be sufficient ON THEIR OWN and rely on \
genuinely different facts, so losing one set leaves the conclusion supported by another.
- Items in different "group" numbers must be about different, separately NAMED \
entities (different people, companies, products, places) and unrelated topics. Never \
leave an entity unnamed ("the customer", "the client"): give every person or company a \
name, and never reuse a name across groups.
- Nothing may support an item except what its justification sets say.

POLICIES (one per belief and decision)
- State the general rule under which the item holds: which KINDS of conditions are \
required together, and which alternatives suffice on their own. Example of the style: \
"An applicant qualifies for Premium Shield either with a clean driving record of five \
years or more together with a credit score of at least 700, or with a vehicle that has \
a top safety rating."
- Write it as a reusable rule about any applicant, account, shipment, traveller, etc. \
Never name the specific person or company from the evidence, never quote evidence \
wording, never mention evidence items, sources or memories.
- The rule must make the AND / OR structure determinable: a reader who knows the rule \
and the facts must be able to tell which facts are jointly needed and which are \
alternatives. Thresholds must be consistent with the facts (a fact meant to satisfy a \
condition must satisfy it).
- For a belief that depends on another belief, the rule may refer to that other \
conclusion in general terms (e.g. "an eligible applicant who also ...").

HOW TO WRITE MEMORY TEXT (beliefs and decisions)
- Write each as a standalone statement of the conclusion only, the way a note in an \
assistant's memory would read. Never explain why it holds.
- Do NOT use: because, since, therefore, thus, hence, so that, as a result, given \
that, based on, according to, due to, which means, supported by, confirmed by.
- Do NOT mention sources, reports, evidence, documents, policies, or how many sources \
there are (e.g. "both", "either", "two reports", "independently").
- Do NOT use stage or sequence words that reveal an order of reasoning: initial, \
preliminary, intermediate, advanced, final, fully, first, second, step, stage, phase.
- Do not copy a fact's wording into the conclusion; vary sentence structure.

SOURCES AND RELIABILITY
- Each evidence item and update has a reliability (high / medium / low). Convey it \
ONLY through a realistic source description: high = authoritative (official record, \
system of record, signed document); medium = generally trustworthy (staff note, \
partner email); low = clearly weak (anonymous post, unverified rumour, secondhand \
hearsay). NEVER write the words high, medium, low or reliability in a source or text.

DATES
- Every evidence item and update has an "observed" date: the day the assistant learned \
it. Avoid calendar dates where possible; prefer relative timing ("last quarter", \
"effective immediately"). If you write a date, it must be on or before that item's \
observed date. Memories and policies contain no dates.

UPDATES (new information arriving later; each targets one evidence item)
- retracts: a later report that the target fact is no longer true. Nothing replaces it.
- supersedes: a later report that the target fact changed to a new, specific value.
- hedges: a later report that casts doubt on the target fact without settling it.
- An update must speak only about its target fact. Never mention any belief, decision \
or policy, and never say what the change implies.

GENERAL
- Never write item ids (E1, B2, D1, U1, ...) or the words node, premise, \
justification, dependency, withdraw, recompute, supersede in any text.
- Keep every text under 45 words. Use concrete names, places and numbers.

OUTPUT: a single JSON object, no prose, with exactly these keys:
{
  "world": "<one sentence describing the situation>",
  "nodes": {"<item id>": {"text": "...", "source": "... (evidence only)"}},
  "updates": {"<update id>": {"text": "...", "source": "..."}},
  "policies": {"<belief or decision id>": "<the general rule>"},
  "rationale": {"<belief or decision id>": ["<one sentence per justification set, in \
order, explaining why that set entails the item under its policy>"]}
}
The rationale is for human reviewers only and is never shown to the system under test.
"""


def _groups(s: Scenario) -> dict[str, int]:
    """Weakly connected components, numbered in node order."""
    adj: dict[str, set[str]] = {n.id: set() for n in s.nodes}
    for nid, justs in s.justifications().items():
        for j in justs:
            for p in j:
                adj[nid].add(p)
                adj[p].add(nid)
    group: dict[str, int] = {}
    for n in s.nodes:
        if n.id in group:
            continue
        k = len(set(group.values())) + 1
        stack = [n.id]
        while stack:
            cur = stack.pop()
            if cur not in group:
                group[cur] = k
                stack.extend(adj[cur])
    return group


def renderer_payload(s: Scenario, seed: int = 0) -> dict:
    """The graph as the renderer sees it, with the observed dates the system will see.
    No gold labels, family name or meta."""
    group = _groups(s)
    observed = timeline(s, seed)
    return {
        "domain": s.domain.replace("_", " "),
        "evidence": [
            {"id": n.id, "reliability": n.reliability, "group": group[n.id], "observed": observed[n.id]}
            for n in s.nodes if n.is_evidence
        ],
        "derived": [
            {"id": n.id, "kind": n.kind.value, "group": group[n.id], "justification_sets": n.justifications}
            for n in s.nodes
            if not n.is_evidence
        ],
        "updates": [
            {"id": u.id, "target": u.target, "relation": u.relation.value, "reliability": u.reliability,
             "observed": observed[u.id]}
            for u in s.updates
        ],
    }


def user_message(s: Scenario, seed: int = 0) -> str:
    return "Render this graph.\n" + json.dumps(renderer_payload(s, seed), indent=1)


@dataclass
class Rendering:
    """Renderer output, keyed by the scenario's original ids."""

    world: str
    texts: dict[str, str]
    sources: dict[str, str]  # evidence and update ids
    update_texts: dict[str, str]
    rationale: dict[str, list[str]]
    errors: list[str] = field(default_factory=list)
    policies: dict[str, str] = field(default_factory=dict)  # derived id -> rule (render-v2)

    @property
    def ok(self) -> bool:
        return not self.errors


def parse_response(s: Scenario, raw: str, require_policies: bool = True) -> Rendering:
    """Parse and structurally validate a renderer response. Problems go to ``errors``."""
    errors: list[str] = []
    try:
        obj = json.loads(raw.strip().removeprefix("```json").removesuffix("```").strip())
    except json.JSONDecodeError as e:
        return Rendering("", {}, {}, {}, {}, [f"invalid JSON: {e}"])
    nodes, updates, rationale = obj.get("nodes", {}), obj.get("updates", {}), obj.get("rationale", {})
    policies = obj.get("policies", {}) or {}
    texts, sources, update_texts = {}, {}, {}
    for n in s.nodes:
        item = nodes.get(n.id) or {}
        text = (item.get("text") or "").strip()
        if not text:
            errors.append(f"{n.id}: missing text")
        texts[n.id] = text
        if n.is_evidence:
            src = (item.get("source") or "").strip()
            if not src:
                errors.append(f"{n.id}: missing source")
            sources[n.id] = src
        else:
            if len(rationale.get(n.id) or []) != len(n.justifications):
                errors.append(f"{n.id}: expected {len(n.justifications)} rationale sentences")
            if require_policies and not (policies.get(n.id) or "").strip():
                errors.append(f"{n.id}: missing policy")
    for u in s.updates:
        item = updates.get(u.id) or {}
        update_texts[u.id] = (item.get("text") or "").strip()
        sources[u.id] = (item.get("source") or "").strip()
        if not update_texts[u.id] or not sources[u.id]:
            errors.append(f"{u.id}: missing text or source")
    derived = {n.id for n in s.nodes if not n.is_evidence}
    extra = (set(nodes) - {n.id for n in s.nodes}) | (set(updates) - {u.id for u in s.updates}) | (set(policies) - derived)
    if extra:
        errors.append(f"unknown ids in response: {sorted(extra)}")
    return Rendering(
        (obj.get("world") or "").strip(), texts, sources, update_texts,
        {k: list(v) for k, v in rationale.items()}, errors,
        {k: str(v).strip() for k, v in policies.items() if k in derived},
    )
