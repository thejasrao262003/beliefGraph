"""Renderer prompt, input payload and response validation.

The renderer sees the full graph (it has to, to write text that respects it). Its
output is split by ``views.py``: the evaluated system only ever sees the system view.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from beliefbench.schema import Scenario

PROMPT_VERSION = "render-v1"

SYSTEM_PROMPT = """\
You write test data for a research benchmark on how AI assistants revise conclusions \
they stored in memory when new information arrives. You receive an abstract dependency \
graph and a domain. Invent a small, realistic situation in that domain and write one \
piece of text per node so that the logical structure below holds EXACTLY.

NODE TYPES
- evidence: an observed fact, reported by a source. Write the fact (one or two \
sentences) and a short source description. The source description must match the \
node's reliability: "high" = authoritative (official record, system of record, \
signed document); "medium" = generally trustworthy; "low" = clearly weak (anonymous \
post, unverified rumour, secondhand hearsay).
- belief: a conclusion the assistant previously drew and saved to memory.
- decision: a recommendation or plan the assistant previously saved to memory.

LOGICAL STRUCTURE (the most important rules)
- Each derived node lists one or more justification sets. For EVERY set, the facts in \
that set taken TOGETHER must be sufficient to conclude the node.
- Inside a set, EVERY fact must be necessary: if any one of them were false, that set \
would no longer support the conclusion.
- Different sets for the same node must each be sufficient ON THEIR OWN, and must rely \
on genuinely different facts, so losing one set leaves the conclusion supported by \
another.
- Nodes in different "group" numbers must be about unrelated entities and topics. No \
fact in one group may bear on any node in another group.
- Nothing may support a node except what its justification sets say.

HOW TO WRITE MEMORY TEXT (beliefs and decisions)
- Write each as a standalone statement of the conclusion only, the way a note in an \
assistant's memory would read. Never explain why it holds.
- Do NOT use: because, since, therefore, thus, hence, so that, as a result, given \
that, based on, according to, due to, which means, supported by, confirmed by.
- Do NOT mention sources, reports, evidence, documents, or how many sources there are \
(e.g. "both", "either", "two reports", "independently").
- Do not copy a fact's wording into the conclusion. Refer to the same entities \
naturally, and vary sentence structure across nodes.

UPDATES (new information arriving later; each targets one evidence node)
- retracts: a later report that the target fact is no longer true. Nothing replaces it.
- supersedes: a later report that the target fact changed to a new, specific value.
- hedges: a later report that casts doubt on the target fact without settling it.
- Give each update a source description matching its reliability, as above.
- An update must speak only about its target fact. Never mention any belief or \
decision, and never say what the change implies.

GENERAL
- Never write node ids (E1, B2, D1, U1, ...) or the words node, premise, \
justification, dependency, gold, withdraw, recompute, supersede in any text.
- Keep every text under 40 words. Use concrete names, places, numbers and dates.

OUTPUT: a single JSON object, no prose, with exactly these keys:
{
  "world": "<one sentence describing the situation>",
  "nodes": {"<node id>": {"text": "...", "source": "... (evidence nodes only)"}},
  "updates": {"<update id>": {"text": "...", "source": "..."}},
  "rationale": {"<derived node id>": ["<one sentence per justification set, in order, \
explaining why that set entails the node>"]}
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


def renderer_payload(s: Scenario) -> dict:
    """The graph as the renderer sees it. No gold labels, family name or meta."""
    group = _groups(s)
    return {
        "domain": s.domain.replace("_", " "),
        "evidence": [
            {"id": n.id, "reliability": n.reliability, "group": group[n.id]} for n in s.nodes if n.is_evidence
        ],
        "derived": [
            {"id": n.id, "kind": n.kind.value, "group": group[n.id], "justification_sets": n.justifications}
            for n in s.nodes
            if not n.is_evidence
        ],
        "updates": [
            {"id": u.id, "target": u.target, "relation": u.relation.value, "reliability": u.reliability}
            for u in s.updates
        ],
    }


def user_message(s: Scenario) -> str:
    return "Render this graph.\n" + json.dumps(renderer_payload(s), indent=1)


@dataclass
class Rendering:
    """Renderer output, keyed by the scenario's original ids."""

    world: str
    texts: dict[str, str]
    sources: dict[str, str]  # evidence and update ids
    update_texts: dict[str, str]
    rationale: dict[str, list[str]]
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def parse_response(s: Scenario, raw: str) -> Rendering:
    """Parse and structurally validate a renderer response. Problems go to ``errors``."""
    errors: list[str] = []
    try:
        obj = json.loads(raw.strip().removeprefix("```json").removesuffix("```").strip())
    except json.JSONDecodeError as e:
        return Rendering("", {}, {}, {}, {}, [f"invalid JSON: {e}"])
    nodes, updates, rationale = obj.get("nodes", {}), obj.get("updates", {}), obj.get("rationale", {})
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
        elif len(rationale.get(n.id) or []) != len(n.justifications):
            errors.append(f"{n.id}: expected {len(n.justifications)} rationale sentences")
    for u in s.updates:
        item = updates.get(u.id) or {}
        update_texts[u.id] = (item.get("text") or "").strip()
        sources[u.id] = (item.get("source") or "").strip()
        if not update_texts[u.id] or not sources[u.id]:
            errors.append(f"{u.id}: missing text or source")
    extra = (set(nodes) - {n.id for n in s.nodes}) | (set(updates) - {u.id for u in s.updates})
    if extra:
        errors.append(f"unknown ids in response: {sorted(extra)}")
    return Rendering(
        (obj.get("world") or "").strip(), texts, sources, update_texts,
        {k: list(v) for k, v in rationale.items()}, errors,
    )
