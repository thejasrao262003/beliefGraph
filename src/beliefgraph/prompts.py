"""Prompts for BeliefGraph's two LLM steps. Versioned; any edit means a new version."""

BUILD_VERSION = "bg-build-v1"
READ_VERSION = "bg-read-v1"

BUILD_PROMPT = """\
You are BeliefGraph. You maintain an AI assistant's memory as a dependency graph.

You receive the assistant's memory: observed FACTS (each with an id, the date it was \
observed, its source and its text), stored MEMORIES (conclusions or plans the assistant \
saved earlier) and the POLICIES (general rules) the assistant applies.

For every memory, work out what it rests on, as an OR of AND sets:
- A justification set is a group of items (facts and/or other memories) that TOGETHER \
establish the memory under one of the policies. Every item in a set is necessary: drop \
any one and the set no longer establishes the memory.
- Different sets are independent alternatives: each one alone establishes the memory.
- A memory can rest on another memory (a chain). Use the policies to decide which facts \
and memories a conclusion needs, whether they are needed jointly (AND) or are \
alternatives (OR), and whether a fact actually meets a policy's threshold.
- Use only ids that appear in the input. Never include a memory in its own sets. Do not \
add items that merely mention the same entity but play no role in the policy.
- A memory that nothing in the input supports gets an empty list.

Also rate how reliable each fact's SOURCE is, from its description only: "high" \
(official record, registry, signed or audited document, system of record), "medium" \
(generally trustworthy but informal: staff note, partner email, internal log) or "low" \
(anonymous, unverified, forum post, rumour, hearsay).

OUTPUT: a single JSON object, no prose:
{"justifications": {"<memory id>": [["<id>", "<id>"], ["<id>"]]},
 "reliability": {"<fact id>": "high" | "medium" | "low"}}
Every memory id and every fact id must appear exactly once.
"""

READ_PROMPT = """\
You are BeliefGraph. New information has arrived for an AI assistant's memory.

You receive the facts the assistant had observed (id, observed date, source, text) and \
the UPDATES that arrived later (id, observed date, source, text). For every update decide:
- "target": the id of the ONE fact it is about;
- "relation":
  - "retracts": it states that the fact is not, or was never, true, and gives no new value;
  - "supersedes": it gives a new value or state for the same thing (a new figure, a \
revocation or expiry, a corrected status);
  - "hedges": it questions or casts doubt on the fact without settling it (under review, \
allegations, irregularities, unconfirmed concerns);
- "reliability" of the update's SOURCE, from its description: "high" (official, \
authoritative, audited, registry), "medium" (generally trustworthy but informal) or \
"low" (anonymous, unverified, forum, blog, rumour).
Judge each update by its wording and source; do not reason about any conclusions.

OUTPUT: a single JSON object, no prose:
{"updates": {"<update id>": {"target": "<fact id>", "relation": "retracts" | "supersedes" | "hedges", \
"reliability": "high" | "medium" | "low"}}}
"""
