"""Renderer prompt, input payload and response validation.

The renderer sees the full graph (it has to, to write text that respects it). Its
output is split by ``views.py``: the evaluated system only ever sees the system view.

render-v2 (2026-10-18) adds visible *policies*: one general rule per derived node,
so the AND/OR structure is determinable from what the system sees (smoke test 1, P1).
render-v3 (2026-10-18) keeps v2's text and adds: vocabulary separation between
policies, memories and facts, decoy policies, and an eval-only post-update state per
derived node (smoke test 2, P7). render-v4 adds a hard no-shared-phrase rule between
memories and policies, flat-denial retractions and correct units (review of smoke
test 3). render-v5 adds outcome/quantity naming rules and bans distinctive memory
words in decoys (v4 re-render). render-v6 makes "no fact wording in policies" an explicit
hard rule (fresh F6 render). render-v7 turns that rule into clarity-first guidance and
adds plain-fact wording (F6 failed twice under v6). render-v8 adds subject- and
time-window continuity rules (pilot-2). All versions stay runnable; earlier ones are verbatim.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from beliefbench.render.views import timeline
from beliefbench.schema import Scenario

PROMPT_VERSION = "render-v12"

# Exactly the text used for smoke test 2 (commit 896d366). Do not edit.
SYSTEM_PROMPT_V2 = """\
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


# render-v3 = v2 + the edits below. Each anchor must exist exactly once in v2.
_V3_EDITS = [
    (
        """- For a belief that depends on another belief, the rule may refer to that other \
conclusion in general terms (e.g. "an eligible applicant who also ...").
""",
        """- For a belief that depends on another belief, the rule may refer to that other \
conclusion in general terms (e.g. "an eligible applicant who also ...").
- VOCABULARY SEPARATION (essential). A policy must not reuse the wording of the memory \
it governs or of the facts it relies on. Name the outcome differently from the memory \
(memory "meets enterprise security compliance criteria" -> policy "security clearance \
is granted when ..."). Describe each condition as a requirement CATEGORY with its \
threshold, never in the fact's words (fact "maintains two certified security officers" \
-> condition "a minimum certified security staffing level of two"). Product, programme \
and standard names (ISO 27001, Platinum Partner) may be kept where needed.
- The meaning must still let a careful reader match each policy to the memory it \
governs and each condition to the facts that satisfy it. Separation of wording, not \
of meaning.

DECOY POLICIES (1 or 2 per scenario)
- Also write one or two extra rules from the same domain that govern NOTHING in this \
scenario: they concern outcomes that no memory states, and none of their conditions \
offers an alternative way to reach any memory's conclusion. They must not mention any \
entity from the scenario. Write them in the same style as the real policies.
""",
    ),
    (
        """  "policies": {"<belief or decision id>": "<the general rule>"},
""",
        """  "policies": {"<belief or decision id>": "<the general rule>"},
  "decoy_policies": ["<rule>", "<optional second rule>"],
  "after_updates": {"<belief or decision id>": "holds" | "fails" | "undetermined"},
""",
    ),
    (
        """The rationale is for human reviewers only and is never shown to the system under test.
""",
        """"after_updates" says, for every belief and decision, whether its conclusion still \
holds once ALL updates are taken into account, judged under its policy from the facts \
that remain credible ("undetermined" if the updates leave it genuinely open).
The rationale and after_updates are for human reviewers only and are never shown to \
the system under test.
""",
    ),
]


def _v3_from_v2(v2: str) -> str:
    out = v2
    for old, new in _V3_EDITS:
        assert out.count(old) == 1, f"v3 anchor not found exactly once: {old[:60]!r}"
        out = out.replace(old, new)
    return out


SYSTEM_PROMPT_V3 = _v3_from_v2(SYSTEM_PROMPT_V2)

# render-v4 = v3 + the edits below (external review of smoke test 3: F1 C7/C11, F6 C4/C10).
_V4_EDITS = [
    (
        """- The meaning must still let a careful reader match each policy to the memory it \
governs and each condition to the facts that satisfy it. Separation of wording, not \
of meaning.
""",
        """- The meaning must still let a careful reader match each policy to the memory it \
governs and each condition to the facts that satisfy it. Separation of wording, not \
of meaning.
- HARD RULE: no phrase of three or more consecutive ordinary (lower-case) words may \
appear both in any memory and in any policy. This includes a policy that uses another \
conclusion as a condition: paraphrase that conclusion too (memory "meets the operational \
risk threshold" -> condition "an applicant cleared on risk grounds"). Proper names of \
products, programmes and standards are exempt. Responses that break this are rejected.
""",
    ),
    (
        """- retracts: a later report that the target fact is no longer true. Nothing replaces it.
""",
        """- retracts: a later report that flatly states the target fact is not, or is no \
longer, true (e.g. "X never held that certification", "X's licence was withdrawn"). \
Nothing replaces it. Even when the source is weak, a retraction asserts falsity; it \
does not merely question or allege. Questioning, alleging or casting doubt is "hedges".
""",
    ),
    (
        """- Keep every text under 45 words. Use concrete names, places and numbers.
""",
        """- Keep every text under 45 words. Use concrete names, places and numbers.
- Quantities must be realistic and use dimensionally correct units (power in MW, \
energy in MWh, money with a currency); a policy threshold must use the same unit as \
the fact it is compared with.
""",
    ),
]


def _v4_from_v3(v3: str) -> str:
    out = v3
    for old, new in _V4_EDITS:
        assert out.count(old) == 1, f"v4 anchor not found exactly once: {old[:60]!r}"
        out = out.replace(old, new)
    return out


SYSTEM_PROMPT_V4 = _v4_from_v3(SYSTEM_PROMPT_V3)

# render-v5 = v4 + the edits below (v4 re-render: over-paraphrase in F1, decoy closer
# to a memory than its real policy in F6).
_V5_EDITS = [
    (
        """products, programmes and standards are exempt. Responses that break this are rejected.
""",
        """products, programmes and standards are exempt. Responses that break this are rejected.
- OUTCOME NAMING: a policy must name its outcome with a clear synonym or close \
paraphrase of the memory's conclusion, recognisably the SAME concept (memory "holds \
Gold-tier partner status" -> policy "partnership at the Gold level"), never a \
different concept name (not "premier merchant designation" for "Qualified Enterprise \
Status"). The same applies when a condition refers to another conclusion.
- QUANTITY NAMING: a condition must name the same measured quantity as the fact that \
satisfies it. Revenue, spending and billing are different quantities; never swap them.
""",
    ),
    (
        """entity from the scenario. Write them in the same style as the real policies.
""",
        """entity from the scenario. Write them in the same style as the real policies.
- A decoy must not use any distinctive content word that appears in any memory (if a \
memory mentions "organic", no decoy may), so that no decoy is a plausible match for a \
memory. Generic rule words (status, eligible, annual, vendor, client, ...) are fine. \
Responses that break this are rejected.
""",
    ),
]


def _v5_from_v4(v4: str) -> str:
    out = v4
    for old, new in _V5_EDITS:
        assert out.count(old) == 1, f"v5 anchor not found exactly once: {old[:60]!r}"
        out = out.replace(old, new)
    return out


SYSTEM_PROMPT_V5 = _v5_from_v4(SYSTEM_PROMPT_V4)

# render-v6 = v5 + one edit (fresh F6 render reused fact wording in 5 policy conditions).
_V6_EDITS = [
    (
        """- QUANTITY NAMING: a condition must name the same measured quantity as the fact that \
satisfies it. Revenue, spending and billing are different quantities; never swap them.
""",
        """- QUANTITY NAMING: a condition must name the same measured quantity as the fact that \
satisfies it. Revenue, spending and billing are different quantities; never swap them.
- HARD RULE (facts): no phrase of three or more consecutive ordinary (lower-case) words \
may appear both in any evidence item and in any policy. Refer to the fact's quantity or \
credential by a clear equivalent that still identifies it unambiguously (fact "gross \
annual revenue" -> condition "yearly turnover"; fact "fleet-wide average carbon emission \
level" -> condition "mean CO2 output per km across the fleet"). Never replace a clear \
quantity with a vague one. Proper names and number+unit phrases ("90 g/km") are \
exempt. Responses that break this are rejected.
""",
    ),
]


def _v6_from_v5(v5: str) -> str:
    out = v5
    for old, new in _V6_EDITS:
        assert out.count(old) == 1, f"v6 anchor not found exactly once: {old[:60]!r}"
        out = out.replace(old, new)
    return out


SYSTEM_PROMPT_V6 = _v6_from_v5(SYSTEM_PROMPT_V5)

# render-v7 = v6 + the edits below (F6 failed twice under v6: the hard fact-wording rule
# pushed the renderer into echoes or vague substitutes, "balance credits" for "carbon
# offsets"). Policy<->evidence overlap becomes a soft flag for human C7/C11 review
# (leakcheck.evidence_echo_hard); clarity of reference comes first (C8/C10).
_V7_EDITS = [
    (
        """- HARD RULE (facts): no phrase of three or more consecutive ordinary (lower-case) words \
may appear both in any evidence item and in any policy. Refer to the fact's quantity or \
credential by a clear equivalent that still identifies it unambiguously (fact "gross \
annual revenue" -> condition "yearly turnover"; fact "fleet-wide average carbon emission \
level" -> condition "mean CO2 output per km across the fleet"). Never replace a clear \
quantity with a vague one. Proper names and number+unit phrases ("90 g/km") are \
exempt. Responses that break this are rejected.
""",
        """- FACT WORDING IN POLICIES (clarity first). A condition must identify the quantity or \
credential of its fact unambiguously. Prefer a clear equivalent to the fact's own \
phrasing (fact "gross annual revenue" -> condition "yearly turnover"), but if the only \
clear name is the standard term (carbon offsets, CO2 per km, headcount, gross revenue), \
use that term. NEVER substitute a vague or invented name (not "balance credits" for \
carbon offsets). Do not copy any other wording of the fact (its verbs, qualifiers or \
sentence) into the policy. Shared wording is reviewed by a human, not rejected; a \
vague condition fails review.
- PLAIN FACTS. Each evidence item states ONE measurable value or ONE held credential, \
named in one or two common words, with no stacked qualifiers (not "a certified annual \
carbon offset plan valued at $50,000"; write "verified carbon offsets of 10,000 \
metric tons this year"). Use a numeric threshold only where a fact is naturally a \
number; a credential, licence or membership is a yes/no condition.
""",
    ),
    (
        """- A decoy must not use any distinctive content word that appears in any memory (if a \
memory mentions "organic", no decoy may), so that no decoy is a plausible match for a \
memory.""",
        """- A decoy must not use any distinctive content word that appears in any memory (if a \
memory mentions "organic", no decoy may), even in a different sense ("security \
deposit" vs "IT security"), so that no decoy is a plausible match for a \
memory.""",
    ),
]


def _v7_from_v6(v6: str) -> str:
    out = v6
    for old, new in _V7_EDITS:
        assert out.count(old) == 1, f"v7 anchor not found exactly once: {old[:60]!r}"
        out = out.replace(old, new)
    return out


SYSTEM_PROMPT_V7 = _v7_from_v6(SYSTEM_PROMPT_V6)
# render-v8 = v7 + the edits below (pilot-2 human review: F6 supported a product's
# memories with facts about its never-named maker; F2 replaced an annual count with one
# "during the evaluation period"). Enforced by leakcheck.subject_flags / window_flags.
_V8_EDITS = [
    (
        """- Nothing may support an item except what its justification sets say.
""",
        """- Nothing may support an item except what its justification sets say.
- SUBJECT CONTINUITY: every fact or conclusion in a justification set must name the \
entity of the item it supports. Prefer facts directly about that entity. If a fact is \
about a related entity (its maker, parent company, owner), state the relation inside \
that same fact ("Norland Labs, maker of the Vira Test Kit, holds ..."); \
a relation stated only in another fact does not count. Responses that break this are \
rejected.
""",
    ),
    (
        """- QUANTITY NAMING: a condition must name the same measured quantity as the fact that \
satisfies it. Revenue, spending and billing are different quantities; never swap them.
""",
        """- QUANTITY NAMING: a condition must name the same measured quantity as the fact that \
satisfies it. Revenue, spending and billing are different quantities; never swap them.
- TIME WINDOWS: a quantity accumulated over time (revenue, purchases, audits, \
incidents) states the window it covers ("annual", "last quarter"), and the condition it \
is compared with uses the same window. Point-in-time values (a fleet size, a rating, an \
age, a warranty length) need no window. An update that replaces an accumulated value \
states it over the same window as the original fact. A window that differs between a \
fact, its condition or its update is rejected; a vague one ("during the evaluation \
period") fails review.
""",
    ),
]


def _v8_from_v7(v7: str) -> str:
    out = v7
    for old, new in _V8_EDITS:
        assert out.count(old) == 1, f"v8 anchor not found exactly once: {old[:60]!r}"
        out = out.replace(old, new)
    return out


SYSTEM_PROMPT_V8 = _v8_from_v7(SYSTEM_PROMPT_V7)
# render-v9 = v8 + per-fact and per-condition records (eval only), checked by code
# against each other and against the text (leakcheck.record_flags). All three human
# "revise" verdicts so far were fact/condition reference mismatches (entity, time
# window, scope) that lexical checks cannot see.
_V9_EDITS = [
    (
        """  "after_updates": {"<belief or decision id>": "holds" | "fails" | "undetermined"},
""",
        """  "after_updates": {"<belief or decision id>": "holds" | "fails" | "undetermined"},
  "facts": {"<evidence or update id>": {"entity": "...", "kind": "number" | "credential", \
"quantity": "...", "value": <number | true | false | null>, "unit": "<unit or null>", \
"window": "none" | "year" | "quarter" | "month" | "week" | "<N> years", \
"scope": "none" | "local" | "regional" | "national" | "international" | "global"}},
  "conditions": {"<belief or decision id>": [{"premise": "<id in its justification sets>", \
"kind": "number" | "credential" | "conclusion", "entity": "<the conclusion's entity>", \
"relation": null | "<e.g. maker of>", "quantity": "...", \
"comparator": ">=" | ">" | "<=" | "<" | "==" | null, "threshold": <number or null>, \
"unit": "<unit or null>", "window": "...", "scope": "..."}]},
""",
    ),
    (
        """The rationale and after_updates are for human reviewers only and are never shown to \
the system under test.
""",
        """RECORDS ("facts" and "conditions") are checked by code against each other and \
against your text. "facts" has one record per evidence item and update: the entity it is \
about, written exactly as in its text; whether it is a number or a credential; the \
quantity or credential name; its value (a number; true or false for a credential; null \
for an update that only retracts or hedges); the unit; the window over which it is \
accumulated ("none" for point-in-time values); and its scope ("none" unless the text \
states one). "conditions" has, for every belief and decision, one record per premise in \
its justification sets, describing the condition in its policy that this premise \
satisfies: the conclusion's entity; the relation if the premise is about a related \
entity (null otherwise; the relation must be stated inside that fact); the same quantity \
name as the fact; comparator and threshold (null for credentials and conclusions); unit; \
window and scope ("none" means the condition sets no window or scope). Every number, \
entity name, window and scope word in a record must appear in the matching text. A \
record that disagrees with its fact, its condition or its own text is rejected.
The rationale, after_updates and records are for human reviewers and checks only and \
are never shown to the system under test.
""",
    ),
]


def _v9_from_v8(v8: str) -> str:
    out = v8
    for old, new in _V9_EDITS:
        assert out.count(old) == 1, f"v9 anchor not found exactly once: {old[:60]!r}"
        out = out.replace(old, new)
    return out


SYSTEM_PROMPT_V9 = _v9_from_v8(SYSTEM_PROMPT_V8)
RECORD_VERSIONS = {"render-v9", "render-v10", "render-v11", "render-v12"}
WINDOWS_ALLOWED = {"none", "year", "quarter", "month", "week"}
SCOPES_ALLOWED = {"none", "local", "regional", "national", "international", "global"}
COMPARATORS = {">=", ">", "<=", "<", "=="}


def _window_ok(w) -> bool:
    import re as _re

    return isinstance(w, str) and (w in WINDOWS_ALLOWED or bool(_re.fullmatch(r"\d+ years", w)))


def validate_records(s: Scenario, facts: dict, conditions: dict) -> list[str]:
    """Structure of the render-v9 records: one fact record per evidence item and update,
    one condition record per premise of every derived item, with allowed field values."""
    errors = []
    expected_facts = {n.id for n in s.nodes if n.is_evidence} | {u.id for u in s.updates}
    if set(facts) != expected_facts:
        errors.append(f"facts must cover exactly {sorted(expected_facts)}, got {sorted(facts)}")
    for fid, f in facts.items():
        if not isinstance(f, dict):
            errors.append(f"facts.{fid}: must be an object")
            continue
        if f.get("kind") not in ("number", "credential"):
            errors.append(f"facts.{fid}.kind must be number or credential")
        if not str(f.get("entity") or "").strip() or not str(f.get("quantity") or "").strip():
            errors.append(f"facts.{fid}: entity and quantity are required")
        if not _window_ok(f.get("window")) or f.get("scope") not in SCOPES_ALLOWED:
            errors.append(f"facts.{fid}: window/scope not in the allowed values")
        v = f.get("value")
        if f.get("kind") == "number" and not (v is None or isinstance(v, (int, float)) and not isinstance(v, bool)):
            errors.append(f"facts.{fid}.value must be a number or null")
        if f.get("kind") == "credential" and v not in (True, False, None):
            errors.append(f"facts.{fid}.value must be true, false or null")
    derived = {n.id: n for n in s.nodes if not n.is_evidence}
    if set(conditions) != set(derived):
        errors.append(f"conditions must cover exactly {sorted(derived)}, got {sorted(conditions)}")
    for nid, conds in conditions.items():
        if nid not in derived or not isinstance(conds, list):
            continue
        premises = {p for j in derived[nid].justifications for p in j}
        got = [c.get("premise") for c in conds if isinstance(c, dict)]
        if sorted(got) != sorted(premises):
            errors.append(f"conditions.{nid}: premises must be exactly {sorted(premises)}, got {sorted(map(str, got))}")
        for c in conds:
            if not isinstance(c, dict):
                continue
            kind = c.get("kind")
            want = "conclusion" if c.get("premise") in derived else ("number", "credential")
            if (kind != want) if isinstance(want, str) else (kind not in want):
                errors.append(f"conditions.{nid}.{c.get('premise')}: kind {kind!r} does not fit the premise")
            if not str(c.get("entity") or "").strip():
                errors.append(f"conditions.{nid}.{c.get('premise')}: entity is required")
            if kind == "number" and (c.get("comparator") not in COMPARATORS
                                     or not isinstance(c.get("threshold"), (int, float))):
                errors.append(f"conditions.{nid}.{c.get('premise')}: a number condition needs comparator and threshold")
            if kind in ("number", "credential") and (not _window_ok(c.get("window"))
                                                     or c.get("scope") not in SCOPES_ALLOWED):
                errors.append(f"conditions.{nid}.{c.get('premise')}: window/scope not in the allowed values")
    return errors


# render-v10 = v9 + one clarification (pilot-4: v9's "same quantity name" for records leaked
# into policy text; policy<->evidence echoes went from 4 in pilot-2 to 12, gate 0.59).
_V10_EDITS = [
    (
        """record that disagrees with its fact, its condition or its own text is rejected.
""",
        """record that disagrees with its fact, its condition or its own text is rejected.
Records are labels for checking only; they never change how the texts are worded. The \
"quantity" label is shared between a fact and its condition record, but the policy TEXT \
still follows FACT WORDING IN POLICIES: name the condition with a clear equivalent of \
the fact's quantity (fact "customer safety score" -> condition "safety rating given by \
customers"; fact "research spending" -> condition "R&D outlay"), and copy the fact's \
phrase only when the standard term is the only clear name.
""",
    ),
]


def _v10_from_v9(v9: str) -> str:
    out = v9
    for old, new in _V10_EDITS:
        assert out.count(old) == 1, f"v10 anchor not found exactly once: {old[:60]!r}"
        out = out.replace(old, new)
    return out


SYSTEM_PROMPT_V10 = _v10_from_v9(SYSTEM_PROMPT_V9)

# render-v11 = v10 + two semantic rules (40-scenario run: F6-005/F6-009 judged a weak-source
# challenge to the only support as "fails"; F2-001 updated "15 transfers" to "8 this quarter").
_V11_EDITS = [
    (
        """that remain credible ("undetermined" if the updates leave it genuinely open).
""",
        """that remain credible ("undetermined" if the updates leave it genuinely open). A \
retraction or hedge from a weak source (anonymous, unverified, hearsay) does not make a \
fact false; it only casts doubt on it. If such an update challenges the ONLY support of \
a conclusion, the conclusion is "undetermined", never "fails"; if another support \
remains, it "holds". Only a credible source can make a conclusion "fail".
""",
    ),
    (
        """vague one ("during the evaluation \
period") fails review.
""",
        """vague one ("during the evaluation \
period") fails review. If the original fact states no window, an update that replaces it \
states none either ("a corrected count of 8 transfers", not "8 transfers this quarter"), \
so it reads unmistakably as a replacement of the same figure; an update that introduces \
a window is rejected.
""",
    ),
]


def _v11_from_v10(v10: str) -> str:
    out = v10
    for old, new in _V11_EDITS:
        assert out.count(old) == 1, f"v11 anchor not found exactly once: {old[:60]!r}"
        out = out.replace(old, new)
    return out


SYSTEM_PROMPT_V11 = _v11_from_v10(SYSTEM_PROMPT_V10)

# render-v12 = v11 + two rules (fresh v11 validation: F2-002's OR routes were lab and field
# measurements of one efficiency; F1-008's retraction added "this year" to an unwindowed fact).
_V12_EDITS = [
    (
        """genuinely different facts, so losing one set leaves the conclusion supported by another.
""",
        """genuinely different facts, so losing one set leaves the conclusion supported by another.
- Alternative sets must concern different quantities or credentials, never two \
measurements of the same quantity against the same condition (not a "lab efficiency" and \
a "field efficiency" both compared with one efficiency threshold).
""",
    ),
    (
        """an update that introduces a window is rejected.
""",
        """an update that introduces a window is rejected. The same holds for a retraction: it \
denies the fact as stated, without adding a window the fact did not have.
""",
    ),
]


def _v12_from_v11(v11: str) -> str:
    out = v11
    for old, new in _V12_EDITS:
        assert out.count(old) == 1, f"v12 anchor not found exactly once: {old[:60]!r}"
        out = out.replace(old, new)
    return out


SYSTEM_PROMPT_V12 = _v12_from_v11(SYSTEM_PROMPT_V11)

PROMPTS = {"render-v2": SYSTEM_PROMPT_V2, "render-v3": SYSTEM_PROMPT_V3, "render-v4": SYSTEM_PROMPT_V4,
           "render-v5": SYSTEM_PROMPT_V5, "render-v6": SYSTEM_PROMPT_V6, "render-v7": SYSTEM_PROMPT_V7,
           "render-v8": SYSTEM_PROMPT_V8, "render-v9": SYSTEM_PROMPT_V9,
           "render-v10": SYSTEM_PROMPT_V10, "render-v11": SYSTEM_PROMPT_V11,
           "render-v12": SYSTEM_PROMPT_V12}
SYSTEM_PROMPT = PROMPTS[PROMPT_VERSION]
AFTER_UPDATE_STATES = {"holds", "fails", "undetermined"}


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
    decoy_policies: list[str] = field(default_factory=list)  # render-v3
    after_updates: dict[str, str] = field(default_factory=dict)  # derived id -> holds|fails|undetermined (v3, eval only)
    records: dict = field(default_factory=dict)  # render-v9: {"facts": {...}, "conditions": {...}}, eval only

    @property
    def ok(self) -> bool:
        return not self.errors


def parse_response(s: Scenario, raw: str, require_policies: bool = True, version: str = PROMPT_VERSION) -> Rendering:
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
    decoys = [str(d).strip() for d in (obj.get("decoy_policies") or []) if str(d).strip()]
    after = {k: str(v).strip().lower() for k, v in (obj.get("after_updates") or {}).items()}
    if version != "render-v2":
        if not 1 <= len(decoys) <= 2:
            errors.append(f"expected 1-2 decoy policies, got {len(decoys)}")
        for nid in sorted(derived):
            if after.get(nid) not in AFTER_UPDATE_STATES:
                errors.append(f"{nid}: after_updates must be one of {sorted(AFTER_UPDATE_STATES)}")
    records = {}
    if version in RECORD_VERSIONS:
        facts, conds = obj.get("facts") or {}, obj.get("conditions") or {}
        errors += validate_records(s, facts, conds)
        records = {"facts": facts, "conditions": conds}
    return Rendering(
        (obj.get("world") or "").strip(), texts, sources, update_texts,
        {k: list(v) for k, v in rationale.items()}, errors,
        {k: str(v).strip() for k, v in policies.items() if k in derived},
        decoys, {k: v for k, v in after.items() if k in derived}, records,
    )
