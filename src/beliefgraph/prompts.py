"""Prompts for BeliefGraph's two LLM steps. Versioned; any edit means a new version."""

BUILD_VERSION = "bg-build-v1"
RETRY_VERSION = "bg-build-retry-v1"
READ_VERSION = "bg-read-v2"

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
- "relation", from what the update ASSERTS about that fact:
  - "retracts": it states that the fact is not, or was never, true ("does not hold", \
"lacks", "never had", "no valid figure", "was revoked") and gives no new figure in its place;
  - "supersedes": it gives a new, specific value for the same thing (a different figure, \
count, rate or date);
  - "hedges": it does not assert that the fact is false; it only questions it or reports \
doubt (under review, questions raised, an inquiry, concerns, possible irregularities).
  The relation does not depend on the source: a weak or anonymous source that flatly \
denies the fact ("an unverified post claims X never had Y") still "retracts"; its weakness \
goes in "reliability".
- "reliability" of the update's SOURCE, from its description: "high" (official, \
authoritative, audited, registry, a revised or updated filing or record by the company or \
an authority), "medium" (generally trustworthy but informal: staff note, partner email, \
newsletter) or "low" (anonymous, unverified, forum, blog, rumour).
Judge each update by its wording and source; do not reason about any conclusions.

OUTPUT: a single JSON object, no prose:
{"updates": {"<update id>": {"target": "<fact id>", "relation": "retracts" | "supersedes" | "hedges", \
"reliability": "high" | "medium" | "low"}}}
"""

# v0.1: a memory left without any justification is asked about once more, on its own.
RETRY_NOTE = """\
Your previous answer gave NO justification for the memories listed under "unsupported". \
Every stored memory was derived from something in this snapshot: a fact, another memory, \
or both, under one of the policies. A policy may name the memory's outcome with different \
words (for example "fleet catalog" for "registry listing"); match by meaning. Give the \
justification sets for these memories only, in the same JSON format; leave a memory empty \
only if nothing in the snapshot could have produced it."""

# Large stores: the graph is built in batches of memories (as memories are written over
# time). Every fact and memory stays a candidate premise; only the listed ones are asked for.
BATCH_NOTE = """\
This store is large, so build the graph in parts: give justification sets ONLY for the \
memories listed under "build_for". Every other fact and memory in the snapshot remains a \
valid premise for them. Still rate the reliability of every fact. This overrides "every \
memory id must appear" in the output rules."""

# ── v0.2: policy-anchored decomposition for small models and large stores ──
# Inspired by RAGU (validate candidates, then constrain relations to them), Graphiti
# (deterministic retrieval front-ends, LLM only for the decisions) and classification-
# guided extraction (route first, then extract). Each call is one small, local decision.
ROUTE_VERSION = "bg-route-v2"
GROUND_VERSION = "bg-ground-v2"
RELIABILITY_VERSION = "bg-rel-v1"
OUTCOME_VERSION = "bg-outcome-v1"
ADJUDICATE_VERSION = "bg-adjudicate-v1"
VERIFY_VERSION = "bg-verify-v1"
SCORE_VERSION = "bg-score-v1"
ROUTE_OUTCOME_VERSION = "bg-route-outcome-v1"

ROUTE_PROMPT = """\
You are BeliefGraph. An AI assistant stored a MEMORY (a conclusion or plan). It reached that \
memory by applying one of its POLICIES (general rules). The memory may name the rule's outcome \
in different words (for example "approved for the fleet catalog" for "catalog listing is \
granted"). Some numbered policies are unrelated rules about other things. The right policy has \
an outcome that IS this memory's conclusion, and conditions about the kinds of facts listed \
under "facts_about_it" (or about another conclusion the memory builds on). Decide which \
numbered policy it is. Answer null if none of them is.

OUTPUT: a single JSON object, no prose: {"policy": <number or null>}
"""

GROUND_PROMPT = """\
You are BeliefGraph. An AI assistant stored a MEMORY by applying a POLICY. Work out exactly \
which stored items the memory rests on.

1. Split the policy's requirements into alternatives (OR) of groups of conditions that must \
hold together (AND). A policy with no "or" has a single group. List only the requirements, never
the policy's outcome (that is the memory itself).
2. For every condition, pick the ONE candidate item (a fact or another stored memory) that \
satisfies it: it must be about the same entity as the memory, or state its relation to it, \
and it must meet the condition (check numbers against thresholds). A condition that refers to \
another conclusion ("an approved supplier that ...") is satisfied by the candidate MEMORY that \
states that conclusion. Use null if no candidate satisfies the condition.
Use only candidate ids, exactly as given.

OUTPUT: a single JSON object, no prose:
{"groups": [{"all_of": [{"condition": "<short>", "item": "<candidate id or null>"}]}]}
"""

RELIABILITY_PROMPT = """\
Rate how reliable each fact's SOURCE is, from its description only: "high" (official record, \
registry, signed or audited document, system of record), "medium" (generally trustworthy but \
informal: staff note, partner email, internal log) or "low" (anonymous, unverified, forum post, \
rumour, hearsay).

OUTPUT: a single JSON object, no prose: {"reliability": {"<fact id>": "high" | "medium" | "low"}}
"""

# v0.3: route on what a policy GIVES, not on everything it mentions. A rule whose condition
# names a memory's concept ("... requires priority dispatch rights") is not that memory's rule;
# the rule that grants it is.
OUTCOME_PROMPT = """\
For each POLICY (a general rule), separate what it GIVES from what it REQUIRES:
- "gives": the status, decision or action the rule grants or produces, in a few words \
("top-tier service rating", "selected for high-priority corporate bookings");
- "requires": the conditions it checks, in a few words.

OUTPUT: a single JSON object, no prose:
{"policies": {"<policy id>": {"gives": "<short>", "requires": "<short>"}}}
"""

ROUTE_OUTCOME_PROMPT = """\
You are BeliefGraph. An AI assistant stored a MEMORY (a conclusion or plan). It reached that \
memory by applying one of its POLICIES (general rules). Each numbered policy is shown as what \
it GIVES and what it REQUIRES. The right policy is the one whose "gives" IS this memory's \
conclusion, possibly in other words ("approved for the fleet catalog" for "catalog listing"). \
A policy that merely REQUIRES the memory's conclusion, or something close to it, is a different \
rule that builds on it: never pick it for that reason. Use "facts_about_it" only to break a tie \
between policies that give the same thing. Answer null if no policy gives this conclusion.

OUTPUT: a single JSON object, no prose: {"policy": <number or null>}
"""

# v0.4: when routing samples disagree, the candidate policies are compared side by side, each
# with the stored items that satisfy it.
ADJUDICATE_PROMPT = """\
You are BeliefGraph. An AI assistant stored a MEMORY (a conclusion or plan) by applying one of \
its POLICIES (general rules) to stored facts and conclusions. Several candidate policies are \
numbered below, each with the stored items that satisfy its conditions ("premises").

Pick the policy the assistant applied:
- its outcome must BE the memory's conclusion, possibly in other words;
- a policy whose outcome is one of this memory's premises (a conclusion it builds on) is NOT \
it: that rule produced the premise, not the memory;
- a policy whose conditions merely mention the same topic as the memory is not it either;
- between policies with the same outcome, prefer the one whose premises are complete.

OUTPUT: a single JSON object, no prose: {"policy": <number>}
"""

# v0.5 (small models): routing as independent yes/no checks of the few nearest policies,
# instead of one choice among many.
VERIFY_PROMPT = """\
You are BeliefGraph. An AI assistant stored a MEMORY (a conclusion or plan). Decide whether \
the assistant reached this memory by applying the given RULE.

Answer yes only if the rule's outcome IS the memory's conclusion, possibly in other words \
(for example "approved for the fleet catalog" for "catalog listing is granted"). Answer no if \
the rule is about something else, or if it merely REQUIRES something like the memory, or if it \
grants one of the memory's own premises.

OUTPUT: a single JSON object, no prose: {"answer": "yes" | "no"}
"""

# v0.5: relative scoring. A yes/no check is biased to "no" on small models when wording
# differs (Qwen3.5-9B said yes to 32 of 1800 checks); a score is only compared with the other
# candidates' scores, so a uniformly strict model still ranks the right rule first.
SCORE_PROMPT = """\
You are BeliefGraph. An AI assistant stored a MEMORY (a conclusion or plan) by applying one of \
its rules. Rate how likely it is that the given RULE is the one that produced this memory, \
from 0 (unrelated) to 10 (certainly this rule).

High: the rule's outcome is what the memory states, possibly in other words (for example \
"approved for the fleet catalog" for "catalog listing is granted").
Low: the rule is about something else, or it only REQUIRES something like the memory, or it \
grants one of the memory's own premises.

OUTPUT: a single JSON object, no prose: {"score": <0-10>}
"""

# v0.7: each rule is parsed once (per rule, not per memory) into what it produces (THEN) and
# what it requires (IF, as OR-of-AND condition groups), as VERBATIM spans of the rule text.
# Routing then matches a memory to THEN clauses, and a memory that matches a rule's IF is
# evidence that the rule is downstream of it, not its source.
RULE_PARSE_VERSION = "bg-rule-parse-v1"
RULE_PARSE_PROMPT = """\
Split the RULE into what it produces and what it requires. Copy the words of the rule; do not \
paraphrase or summarise.

- "then": the part of the rule that states the outcome it grants, produces or decides (a status, \
an approval, a selection, a classification);
- "if": the conditions it checks, as a list of alternatives; each alternative is a list of \
conditions that must ALL hold. A rule with no "or" has one alternative.

OUTPUT: a single JSON object, no prose:
{"then": "<span of the rule>", "if": [["<span>", "<span>"], ["<span>"]]}
"""

# v0.8: routing read from token probabilities. Candidates are lettered and the answer is
# prefilled up to the letter, so one forward pass gives a distribution over all candidates.
ROUTE_LETTER_PROMPT = ROUTE_PROMPT.replace('{"policy": <number or null>}', '{"policy": "<letter>"}').replace(
    "Decide which numbered policy it is. Answer null if none of them is.", "Decide which lettered policy it is.")
