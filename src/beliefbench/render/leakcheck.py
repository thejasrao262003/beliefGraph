"""Automated leakage checks on rendered scenarios. They raise *flags for review*, never
automatic rejections, except hard leaks (ids, schema keys, label words, reliability
labels, impossible dates) in the system view, which trigger a regeneration.

1. Forbidden text: graph ids, label vocabulary, reliability labels, dates after the
   observed date, explicit support language, source counts, stage/sequence words.
2. Cross-group entities: the same name (or an unnamed "the customer") in unrelated groups.
3. Lexical structure recovery: how much of the gold justification structure a
   bag-of-words heuristic recovers from the system view alone, with and without the
   visible policies. If word matching recovers the graph, the benchmark measures
   lexical matching, not inference.
4. Template repetition across scenarios.
"""

from __future__ import annotations

import datetime as dt
import re
from collections import Counter
from dataclasses import dataclass, field

from beliefbench.metrics import ExtractionScore
from beliefbench.render.views import SYSTEM_VIEW_KEYS

HARD = {
    "graph_id": re.compile(r"\b[EBDU]\d{1,2}\b|\b[emup]_[0-9a-f]{4}\b"),
    # "gold" alone is a natural word (Gold card, gold tier): only the label phrase is hard.
    "label_word": re.compile(r"\b(premise|justification|dependenc(y|ies)|withdraw|recompute|supersede[sd]?|node)\b"
                             r"|\bgold[- ](label|action|answer|standard)s?\b", re.I),
    "reliability_word": re.compile(r"\breliability\b", re.I),
}
# Bare reliability labels in a source description: "high", "Site Survey, high", "(low)".
SOURCE_LABEL = re.compile(r"^\s*(high|medium|low)\s*$|,\s*(high|medium|low)\s*$|\(\s*(high|medium|low)\s*\)", re.I)

SOFT_MEMORY = {
    "explains_reason": re.compile(
        r"\b(because|since|therefore|thus|hence|as a result|given that|based on|according to|due to|"
        r"which means|supported by|confirmed by|so that)\b", re.I),
    "mentions_sources": re.compile(
        r"\b(both|either|two|three|several|multiple|independent(ly)?)\s+(sources?|reports?|records?|documents?)\b|"
        r"\b(sources?|reports?|evidence|records? show)\b", re.I),
    "order_cue": re.compile(
        r"\b(initial(ly)?|preliminar(y|ily)|intermediate|advanced|final(ly)?|fully|first|second|third|"
        r"step|stage|phase)\b", re.I),
}
SOFT_UPDATE = {
    "update_mentions_implication": re.compile(
        r"\b(therefore|which means|so (we|you) should|as a result|no longer recommend|eligib\w*|qualif\w*)\b", re.I),
}

MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}
_MON = "|".join(MONTHS)
DATE_PATTERNS = [
    (re.compile(r"\b(20\d\d)-(\d\d)-(\d\d)\b"), lambda m: dt.date(int(m[1]), int(m[2]), int(m[3]))),
    (re.compile(rf"\b({_MON})\s+(\d{{1,2}}),?\s+(20\d\d)\b", re.I),
     lambda m: dt.date(int(m[3]), MONTHS[m[1].lower()], int(m[2]))),
    (re.compile(rf"\b(\d{{1,2}})\s+({_MON})\s+(20\d\d)\b", re.I),
     lambda m: dt.date(int(m[3]), MONTHS[m[2].lower()], int(m[1]))),
    (re.compile(rf"\b({_MON})\s+(20\d\d)\b", re.I), lambda m: dt.date(int(m[2]), MONTHS[m[1].lower()], 1)),
    (re.compile(r"\b(20\d\d)\b"), lambda m: dt.date(int(m[1]), 1, 1)),
]

STOP = set("""a an the of to in on at for from by with and or but not no is are was were be been being has have had
do does did this that these those it its as into than then there their they them he she his her we our you your
i me my will would can could should may might must about over under after before during per via each any all
some more most less least very also only just new now""".split())
CAP_STOP = STOP | {"if", "when", "an", "any", "every", "recommend", "offer", "provision", "approve"}


def tokens(text: str) -> set[str]:
    out = set()
    for w in re.findall(r"[a-z0-9]+", text.lower()):
        if w in STOP or len(w) < 2:
            continue
        out.add(w[:-1] if len(w) > 3 and w.endswith("s") else w)
    return out


def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a | b else 0.0


def dates_in(text: str) -> list[dt.date]:
    out, taken = [], []
    for pat, conv in DATE_PATTERNS:  # most specific first; skip spans already matched
        for m in pat.finditer(text):
            if any(s <= m.start() < e for s, e in taken):
                continue
            try:
                out.append(conv(m))
                taken.append(m.span())
            except ValueError:
                pass
    return out


def names(text: str) -> set[str]:
    """Capitalised words that are not sentence-initial filler: a rough entity detector."""
    out = set()
    for m in re.finditer(r"\b[A-Z][a-zA-Z]{2,}\b", text):
        w = m.group(0)
        if w.lower() in CAP_STOP or w.lower() in MONTHS:
            continue
        out.add(w)
    return out


SUBJECT = re.compile(r"^((?:[A-Z][\w&'.-]*)(?:\s+(?:[A-Z][\w&'.-]*|of|and|&))*)")


def subject_names(system: dict) -> set[str]:
    """The entity each evidence sentence is about: its leading run of capitalised words
    ("Apex Tech Solutions maintains ..."). Generic openers ("The", "A") are skipped."""
    out = set()
    for e in system["evidence"]:
        m = SUBJECT.match(e["text"].strip())
        if not m:
            continue
        name = m.group(1).strip()
        first = name.split()[0]
        if first.lower() in CAP_STOP or first.lower() in {"the", "a", "an", "our", "its"}:
            continue
        out.add(name)
    return out


def _mentions(text: str, name: str) -> str | None:
    """Full name, or its distinctive first word, as a whole word in text."""
    for cand in (name, name.split()[0]):
        if len(cand) >= 3 and re.search(rf"\b{re.escape(cand)}\b", text):
            return cand
    return None


@dataclass
class Flag:
    scenario: str
    item: str
    kind: str
    match: str
    hard: bool


def _items(system: dict) -> list[tuple[str, dict]]:
    return ([("evidence", e) for e in system["evidence"]] + [("memory", m) for m in system["memories"]]
            + [("update", u) for u in system["updates"]] + [("policy", p) for p in system.get("policies", [])])


def text_flags(system: dict) -> list[Flag]:
    flags: list[Flag] = []
    sid = system["scenario"]
    extra = set(system) - SYSTEM_VIEW_KEYS
    if extra:
        flags.append(Flag(sid, "-", "unexpected_key", ",".join(sorted(extra)), True))
    last_evidence = max((dt.date.fromisoformat(e["observed"]) for e in system["evidence"]), default=None)
    subjects = subject_names(system)
    for kind, item in _items(system):
        fields = [("text", item["text"])] + ([("source", item["source"])] if "source" in item else [])
        for fname, text in fields:
            for name, pat in HARD.items():
                if m := pat.search(text):
                    flags.append(Flag(sid, item["id"], name, m.group(0), True))
            if fname == "source" and (m := SOURCE_LABEL.search(text)):
                flags.append(Flag(sid, item["id"], "reliability_label", m.group(0).strip(), True))
            soft = SOFT_MEMORY if kind == "memory" else SOFT_UPDATE if kind == "update" else {}
            for name, pat in soft.items():
                if m := pat.search(text):
                    flags.append(Flag(sid, item["id"], name, m.group(0), False))
            # Dates: evidence / updates may not mention a date after they were observed;
            # memories and policies should carry no dates at all.
            for d in dates_in(text):
                if "observed" in item:
                    if d > dt.date.fromisoformat(item["observed"]):
                        flags.append(Flag(sid, item["id"], "date_after_observed", d.isoformat(), True))
                else:
                    hard = last_evidence is not None and d > last_evidence
                    flags.append(Flag(sid, item["id"], "date_in_" + kind, d.isoformat(), hard))
        if kind == "policy":
            hits = sorted({h for n in subjects if (h := _mentions(item["text"], n))})
            if hits:
                flags.append(Flag(sid, item["id"], "policy_names_subject", ",".join(hits), False))
    return flags


def shared_phrases(a: str, b: str, n: int = 3) -> set[str]:
    """Lower-case word n-grams (>= 2 content words) present in both texts. Spans with a
    capitalised word (product, programme, standard names) or a number are skipped."""
    def grams(text: str) -> set[tuple[str, ...]]:
        words = re.findall(r"[A-Za-z0-9$%-]+", text)
        out = set()
        for i in range(len(words) - n + 1):
            g = words[i : i + n]
            if any(w[0].isupper() for w in g):
                continue
            # Quantity phrases ("500 square meters") are exempt: since render-v4 a threshold
            # must use the same unit as its fact, so number+unit overlap is mandated.
            if any(any(ch.isdigit() for ch in w) for w in g):
                continue
            low = tuple(w.lower() for w in g)
            if sum(w not in STOP for w in low) >= 2:
                out.add(low)
        return out

    return {" ".join(g) for g in grams(a) & grams(b)}


# Prompt versions under which a policy<->evidence echo is a hard (regenerating) flag.
# From render-v7 it is a soft flag for human C7/C11 review: shared technical terms
# ("carbon offsets", "g/km") are not structural leaks by themselves, and the hard rule
# pushed F6 into vague substitutes (approved 2026-10-20; v5/v6 results keep the strict rule).
STRICT_EVIDENCE_ECHO_VERSIONS = {"render-v2", "render-v3", "render-v4", "render-v5", "render-v6"}


def evidence_echo_hard(prompt_version: str) -> bool:
    return prompt_version in STRICT_EVIDENCE_ECHO_VERSIONS


def echo_flags(system: dict, evidence_hard: bool = True) -> list[Flag]:
    """No ordinary 3-word phrase shared by a policy and any memory (hard, render-v4,
    smoke test 3) or any evidence item (added 2026-10-18 after v5 F6: "state
    pharmaceutical distribution license", "organic processing certification"). Such
    echoes let a reader map memory -> policy -> premises by string matching. Proper
    names (capitalised spans: products, programmes, standards) are exempt. The evidence
    echo is hard unless ``evidence_hard`` is False (render-v7 onward)."""
    flags = []
    for kind, items, hard in (("policy_echoes_memory", system["memories"], True),
                              ("policy_echoes_evidence", system["evidence"], evidence_hard)):
        for it in items:
            for p in system.get("policies", []):
                shared = shared_phrases(it["text"], p["text"])
                if shared:
                    flags.append(Flag(system["scenario"], f"{it['id']}~{p['id']}", kind, "; ".join(sorted(shared)), hard))
    return flags


# Words that are generic in eligibility rules; sharing them does not make a decoy a
# plausible match for a memory (calibrated on smoke tests 3-4).
GENERIC_RULE_WORDS = {
    "statu", "status", "receive", "receiv", "grant", "granted", "approved", "approval", "qualify", "qualifie",
    "qualified", "eligible", "eligibility", "program", "programme", "requirement", "criteria", "standard",
    "commercial", "business", "company", "vendor", "supplier", "client", "customer", "account", "applicant",
    "firm", "organization", "organisation", "entity", "annual", "year", "month", "quarter", "active", "valid",
    "certified", "certification", "minimum", "least", "maintain", "hold", "holding", "level", "designation",
    "product", "service", "meet", "meets", "achieve", "achieves", "fulfill", "fulfil", "secure",
}


def decoy_word_flags(system: dict, evaluation: dict) -> list[Flag]:
    """render-v5 hard rule: a decoy policy may not share a distinctive content word with
    any memory (numbers and generic rule words excepted). Otherwise the decoy can be a
    plausible competing match for that memory (v4 re-render, F6 'organic')."""
    decoys = set(evaluation.get("decoy_policies") or [])
    # Entity names are identity, not outcome concepts: strip the subject-name spans from
    # each memory before taking its vocabulary ("Apex Logistics" vs "a logistics firm").
    # A word that also occurs in the memory's outcome wording still counts, because only
    # the name span is removed (refinement approved 2026-10-18, after v5 F2).
    names = sorted(subject_names(system), key=len, reverse=True)

    def outcome_words(text: str) -> set[str]:
        for name in names:
            text = re.sub(rf"\b{re.escape(name)}\b", " ", text)
        return tokens(text)

    mem = set().union(*(outcome_words(m["text"]) for m in system["memories"])) if system["memories"] else set()
    flags = []
    for p in system.get("policies", []):
        if p["id"] not in decoys:
            continue
        shared = sorted(w for w in tokens(p["text"]) & mem if not w.isdigit() and w not in GENERIC_RULE_WORDS)
        if shared:
            flags.append(Flag(system["scenario"], p["id"], "decoy_shares_memory_word", ",".join(shared), True))
    return flags


UNNAMED = re.compile(r"\bthe (customer|client|applicant|user|traveller|traveler|company|business|account holder)\b", re.I)


def group_flags(system: dict, evaluation: dict) -> list[Flag]:
    """Same name, or an unnamed generic subject, used in texts of different groups."""
    sid, groups = system["scenario"], evaluation.get("groups", {})
    by_group_names: dict[int, set[str]] = {}
    by_group_unnamed: dict[int, set[str]] = {}
    for kind, item in _items(system):
        g = groups.get(item["id"])
        if g is None:  # updates take their target's group; policies their memory's
            target = evaluation.get("update_targets", {}).get(item["id"], {}).get("target")
            target = target or evaluation.get("policy_of", {}).get(item["id"])
            g = groups.get(target)
        if g is None:
            continue
        by_group_names.setdefault(g, set()).update(names(item["text"]))
        by_group_unnamed.setdefault(g, set()).update(m.group(0).lower() for m in UNNAMED.finditer(item["text"]))
    flags = []
    gs = sorted(by_group_names)
    for i, a in enumerate(gs):
        for b in gs[i + 1:]:
            shared = by_group_names[a] & by_group_names[b]
            if shared:
                flags.append(Flag(sid, f"groups {a}/{b}", "cross_group_entity", ",".join(sorted(shared)), False))
            generic = by_group_unnamed[a] & by_group_unnamed[b]
            if generic:
                flags.append(Flag(sid, f"groups {a}/{b}", "unnamed_entity_in_groups", ",".join(sorted(generic)), False))
    return flags


_EXPECTED_FINAL = {"keep": "holds", "withdraw": "fails", "uncertain": "undetermined"}
HEDGE_LANGUAGE = re.compile(r"\b(claims?|claimed|alleg\w*|may|might|possibly|reportedly|rumou?r\w*|suggest\w*|"
                            r"question\w*|doubt\w*|unconfirmed|could)\b", re.I)


def relation_flags(system: dict, evaluation: dict) -> list[Flag]:
    """An update's wording should match its formal relation: a `retracts` update asserts
    falsity, so hedging language there is flagged (smoke test 3, F6 C4)."""
    flags = []
    rel = {u: t["relation"] for u, t in (evaluation.get("update_targets") or {}).items()}
    for u in system["updates"]:
        if rel.get(u["id"]) == "retracts" and (m := HEDGE_LANGUAGE.search(u["text"])):
            flags.append(Flag(system["scenario"], u["id"], "retraction_reads_as_hedge", m.group(0), False))
    return flags


# ── render-v8: reference continuity (approved 2026-10-20 after pilot-2) ──
# Pilot-2 failed on reference, not wording: F6 supported a product's memories with facts
# about another company (its maker, never stated), and F2 replaced an annual count with
# one "during the evaluation period". Both checks report uncertainty as a soft flag
# rather than guessing a match or a mismatch.

_NAME_TOKEN = r"(?:[A-Z][\w&.-]*|\d[\w-]*)"
# Leading run of capitalised tokens; digits may follow ("Kestrel 800", "Orion Drone 4").
_ENTITY_HEAD = re.compile(rf"^(?:The\s+)?([A-Z][\w&.-]*(?:'s?)?(?:\s+(?:{_NAME_TOKEN}|of|and|&)(?:'s?)?)*)")
_CORP_SUFFIX = re.compile(r"\s+(Inc|Corp|Corporation|LLC|Ltd|Co|Group|Plc|GmbH)\.?$")


def _clean_name(name: str) -> str:
    name = re.sub(r"\s+(of|and|&)$", "", name.strip().rstrip(".,"))
    return name


def evidence_entities(system: dict) -> set[str]:
    """Named subjects of the evidence sentences, conservatively: the leading run of
    capitalised words (a leading "The" is skipped), with possessives split into owner
    and item ("Vortex Solar Inc's Helios Panel" -> both). Sentences that open with a
    generic word give no name, so their subject stays unknown."""
    out = set()
    for e in system["evidence"]:
        m = _ENTITY_HEAD.match(e["text"].strip())
        if not m:
            continue
        head = m.group(1)
        if head.split()[0].lower() in CAP_STOP | {"a", "an", "our", "its", "this", "these", "all", "each"}:
            continue
        for part in re.split(r"'s?(?:\s+|$)", head):
            part = _clean_name(part)
            if len(part) >= 3 and not part.isdigit():
                out.add(part)
    return out


def _named(text: str, names: set[str]) -> set[str]:
    """Which known entity names occur in text (whole words; corporate suffix optional)."""
    found = set()
    for n in names:
        variants = {n, _CORP_SUFFIX.sub("", n)}
        if any(len(v) >= 3 and re.search(rf"(?<![\w-]){re.escape(v)}(?![\w-])", text) for v in variants):
            found.add(n)
    return found


def subject_flags(system: dict, evaluation: dict) -> list[Flag]:
    """Every premise of a memory must be about the memory's entity: it names an entity the
    memory names, or states the relation itself ("Apex Medical Corp, maker of the BioGlow
    Diagnostic Kit, ..."), which also names it. Hard when both sides name known entities
    and share none; soft when either side names none (the detector is unsure)."""
    names = evidence_entities(system)
    text = {x["id"]: x["text"] for x in system["evidence"] + system["memories"]}
    flags = []
    for mid, justs in evaluation["justifications"].items():
        if mid not in text:
            continue
        m_names = _named(text[mid], names)
        for p in sorted({p for j in justs for p in j}):
            if p not in text:
                continue
            p_names = _named(text[p], names)
            item = f"{p}->{mid}"
            if not m_names or not p_names:
                side = "memory" if not m_names else "premise"
                flags.append(Flag(system["scenario"], item, "subject_uncertain", f"no known entity named in {side}", False))
            elif not m_names & p_names:
                flags.append(Flag(system["scenario"], item, "premise_about_other_entity",
                                  f"{', '.join(sorted(p_names))} vs {', '.join(sorted(m_names))}", True))
    return flags


_NUM = r"(\d+|two|three|four|five|six|seven|eight|nine|ten)"
_WORDNUM = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
_REL = r"(?:previous|preceding|past|prior|last|current|latest|most recent)"
# Windows over which a count or amount is aggregated. A duration that is itself the
# measured value ("a warranty period of 24 months", "fleet age of 5.8 years") matches
# none of these: every pattern needs a window word (annual, per, during/over the ...).
WINDOW_PATTERNS = [
    ("year", re.compile(rf"\b(annual(ly)?|yearly|per year|a year|each year|every year|per annum|this year|"
                        rf"last year|year-to-date|(the )?{_REL} (calendar |fiscal |financial )?year|"
                        rf"(calendar|fiscal|financial) year)\b", re.I)),
    ("quarter", re.compile(rf"\b(quarterly|per quarter|each quarter|this quarter|last quarter|"
                           rf"(the )?{_REL} (fiscal )?quarter|Q[1-4])\b", re.I)),
    ("month", re.compile(rf"\b(monthly|per month|each month|this month|last month|(the )?{_REL} month)\b", re.I)),
    ("week", re.compile(rf"\b(weekly|per week|this week|last week|(the )?{_REL} week)\b", re.I)),
]
MULTI_YEAR = re.compile(rf"\b(?:during|over|in|within|for|across) (?:the )?(?:{_REL} )?{_NUM} years\b", re.I)
VAGUE_WINDOW = re.compile(r"\b(?:during|over|in|for|within|across) the (?:\w+ )?period\b|\brecently\b|"
                          r"\bin recent (?:months|years)\b", re.I)


def windows(text: str) -> set[str]:
    """Normalised aggregation windows in text: year, quarter, month, week, "N years",
    or "unknown" for a vague one ("during the evaluation period")."""
    out = {w for w, pat in WINDOW_PATTERNS if pat.search(text)}
    for m in MULTI_YEAR.finditer(text):
        n = m.group(1).lower()
        out.add(f"{_WORDNUM.get(n, n)} years")
    if VAGUE_WINDOW.search(text):
        out.add("unknown")
    return out


_CLAUSE_SPLIT = re.compile(r",|;|\b(?:or|and|alongside|together with|plus|while|either)\b", re.I)


def condition_windows(fact: str, policy: str) -> set[str]:
    """Windows of the policy condition that this fact satisfies. A policy usually has
    several conditions, and a window ("annual") belongs to one of them, so the policy is
    split into clauses and the clause sharing the most content words with the fact is
    used. No clear best clause (no overlap, or a tie) means no window is attributed."""
    fact_words = tokens(fact) - set(GENERIC_RULE_WORDS)
    scored = [(len(fact_words & (tokens(c) - set(GENERIC_RULE_WORDS))), c) for c in _CLAUSE_SPLIT.split(policy) if c.strip()]
    scored.sort(key=lambda x: -x[0])
    if not scored or scored[0][0] == 0 or (len(scored) > 1 and scored[1][0] == scored[0][0]):
        return set()
    return windows(scored[0][1]) - {"unknown"}


def window_flags(system: dict, evaluation: dict) -> list[Flag]:
    """Time-window continuity (render-v8). For each superseding update, its new value must
    cover the window of the target fact and of the policy condition it satisfies: hard if
    it states a different window, soft if it states none or a vague one. Also hard if a
    premise and its policy condition state disjoint windows. Only stated windows count."""
    text = {x["id"]: x["text"] for x in system["evidence"] + system["updates"] + system.get("policies", [])}
    policy_for = {m: p for p, m in (evaluation.get("policy_of") or {}).items()}
    governing: dict[str, set[str]] = {}  # evidence id -> policies of the memories it supports
    for mid, justs in evaluation["justifications"].items():
        for j in justs:
            for p in j:
                if mid in policy_for:
                    governing.setdefault(p, set()).add(policy_for[mid])
    flags = []
    sid = system["scenario"]
    for e in system["evidence"]:
        ew = windows(e["text"]) - {"unknown"}
        for pid in sorted(governing.get(e["id"], ())):
            pw = condition_windows(e["text"], text.get(pid, ""))
            if ew and pw and not ew & pw:
                flags.append(Flag(sid, f"{e['id']}~{pid}", "fact_policy_window_mismatch",
                                  f"{'/'.join(sorted(ew))} vs {'/'.join(sorted(pw))}", True))
    for uid, u in (evaluation.get("update_targets") or {}).items():
        if u["relation"] != "supersedes" or uid not in text:
            continue
        ref = windows(text.get(u["target"], ""))
        for pid in governing.get(u["target"], ()):
            ref |= condition_windows(text.get(u["target"], ""), text.get(pid, ""))
        ref -= {"unknown"}
        if not ref:
            continue
        uw = windows(text[uid])
        known = uw - {"unknown"}
        if known and not known & ref:
            flags.append(Flag(sid, uid, "update_window_mismatch",
                              f"{'/'.join(sorted(known))} vs {'/'.join(sorted(ref))}", True))
        elif not known:
            flags.append(Flag(sid, uid, "update_window_unclear",
                              f"{'vague' if uw else 'none'} vs {'/'.join(sorted(ref))}", False))
    return flags


# Prompt versions rendered before these checks existed; their results are not re-judged.
PRE_CONTINUITY_VERSIONS = STRICT_EVIDENCE_ECHO_VERSIONS | {"render-v7"}


def continuity_enforced(prompt_version: str) -> bool:
    return prompt_version not in PRE_CONTINUITY_VERSIONS


def continuity_flags(system: dict, evaluation: dict) -> list[Flag]:
    return subject_flags(system, evaluation) + window_flags(system, evaluation)


def consistency_flags(system: dict, evaluation: dict) -> list[Flag]:
    """render-v3: the renderer's own post-update judgement per memory must agree with the
    gold action (keep -> holds, withdraw -> fails, uncertain -> undetermined), and a
    recompute must resolve to holds or fails. Disagreement means the rendered world and
    the gold labels diverge: a semantic problem for review, not a leak."""
    after = evaluation.get("after_updates") or {}
    if not after:
        return []
    flags = []
    for mid, action in evaluation["gold"].items():
        if not mid.startswith("m_"):
            continue
        got = after.get(mid)
        if action == "recompute":
            if got not in ("holds", "fails"):
                flags.append(Flag(system["scenario"], mid, "recompute_unresolved", str(got), False))
        elif got != _EXPECTED_FINAL[action]:
            flags.append(Flag(system["scenario"], mid, "final_state_mismatch", f"gold {action}, renderer {got}", False))
    return flags


def _texts(system: dict) -> dict[str, set[str]]:
    return {e["id"]: tokens(e["text"]) for e in system["evidence"]} | \
           {m["id"]: tokens(m["text"]) for m in system["memories"]}


def _predict(target: set[str], candidates: dict[str, set[str]], abs_threshold: float, rel_threshold: float) -> list:
    scores = {c: jaccard(target, t) for c, t in candidates.items()}
    best = max(scores.values(), default=0.0)
    chosen = sorted(c for c, v in scores.items() if v >= abs_threshold and v >= rel_threshold * best)
    return [chosen] if chosen else []


def lexical_justifications(system: dict, abs_threshold: float = 0.15, rel_threshold: float = 0.6) -> dict:
    """Bag-of-words structure guess: for each memory, the candidates (all evidence and
    other memories) whose token overlap is >= rel_threshold * best and >= abs_threshold,
    as one AND-set. A deliberately simple floor that any real extractor must beat."""
    texts = _texts(system)
    return {m["id"]: _predict(texts[m["id"]], {c: t for c, t in texts.items() if c != m["id"]},
                              abs_threshold, rel_threshold) for m in system["memories"]}


def policy_assisted_justifications(system: dict, abs_threshold: float = 0.10, rel_threshold: float = 0.6) -> dict:
    """Same heuristic, but each memory is first matched to its most similar visible
    policy, and candidates are scored against memory + policy words. Tests whether the
    policies' wording hands over the graph."""
    texts = _texts(system)
    pol = {p["id"]: tokens(p["text"]) for p in system.get("policies", [])}
    out = {}
    for m in system["memories"]:
        mt = texts[m["id"]]
        best_pol = max(pol.values(), key=lambda t: jaccard(mt, t), default=set())
        out[m["id"]] = _predict(mt | best_pol, {c: t for c, t in texts.items() if c != m["id"]},
                                abs_threshold, rel_threshold)
    return out


def premise_overlap_auc(system: dict, evaluation: dict) -> float | None:
    """P(a true premise has higher overlap with its conclusion than a non-premise), over
    all memories. 0.5 = no lexical signal; 1.0 = wording fully separates premises.
    Shared entity names legitimately push this above 0.5, so it is only a review flag."""
    texts = _texts(system)
    wins = total = 0.0
    for mid, justs in evaluation["justifications"].items():
        premises = {p for j in justs for p in j}
        scores = {c: jaccard(texts[mid], t) for c, t in texts.items() if c != mid}
        pos = [scores[p] for p in premises if p in scores]
        neg = [v for c, v in scores.items() if c not in premises]
        for a in pos:
            for b in neg:
                total += 1
                wins += 1.0 if a > b else 0.5 if a == b else 0.0
    return wins / total if total else None


def template_flags(systems: list[dict], max_share: float = 0.25, min_scenarios: int = 8) -> list[tuple[str, float]]:
    """Content-word trigrams that recur in more than ``max_share`` of all memory texts,
    across at least ``min_scenarios`` scenarios: signs of a repeated template."""
    gram_count: Counter = Counter()
    gram_scen: dict[tuple, set] = {}
    n_mem = 0
    for sv in systems:
        for m in sv["memories"]:
            n_mem += 1
            words = re.findall(r"[a-z]+", m["text"].lower())
            for g in {tuple(words[i : i + 3]) for i in range(len(words) - 2)}:
                if all(w in STOP for w in g):
                    continue
                gram_count[g] += 1
                gram_scen.setdefault(g, set()).add(sv["scenario"])
    return sorted(
        ((" ".join(g), c / n_mem) for g, c in gram_count.items()
         if n_mem and c / n_mem > max_share and len(gram_scen[g]) >= min_scenarios),
        key=lambda x: -x[1],
    )


# ── render-v9: structured condition records (eval only) ──
# The renderer declares, per fact and per condition, the entity, quantity, value or
# threshold, unit, window and scope. Code checks the two records against each other
# (agreement), checks the arithmetic (satisfaction, and the post-update outcome), and
# checks each record against its own text (grounding), so a record cannot quietly
# disagree with what the system is shown.

_WORD_NUM = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve".split())}
_MULT = {"thousand": 1e3, "million": 1e6, "billion": 1e9}
_NUM_RE = re.compile(r"(\d[\d,]*(?:\.\d+)?)(?:\s*(thousand|million|billion))?|\b(" + "|".join(_WORD_NUM) + r")\b", re.I)
SCOPE_WORDS = {"local": "local", "regional": "regional", "national": "national", "nationwide": "national",
               "international": "international", "global": "global", "worldwide": "global"}
_SCOPE_RE = re.compile(r"\b(" + "|".join(SCOPE_WORDS) + r")\b", re.I)


def numbers_in(text: str) -> list[float]:
    out = []
    for m in _NUM_RE.finditer(text):
        if m.group(3):
            out.append(float(_WORD_NUM[m.group(3).lower()]))
            continue
        v = float(m.group(1).replace(",", ""))
        out.append(v * _MULT[m.group(2).lower()] if m.group(2) else v)
    return out


def scopes_in(text: str) -> set[str]:
    return {SCOPE_WORDS[m.lower()] for m in _SCOPE_RE.findall(text)}


def _has_number(text: str, v) -> bool:
    return any(abs(x - float(v)) <= 1e-6 * max(1.0, abs(float(v))) for x in numbers_in(text))


# Finer than _CLAUSE_SPLIT (kept as is for the v8 window check): also splits the outcome
# from its conditions at "provided", "if", "through", ... so an outcome name such as
# "international commercial readiness" is not read as a condition's scope.
_RECORD_CLAUSE_SPLIT = re.compile(r",|;|\b(?:or|and|alongside|together with|plus|while|either|provided|if|when|"
                                  r"whenever|once|upon|requires?|via|through|by)\b", re.I)


def condition_clause(fact: str, policy: str) -> str | None:
    """The policy clause this fact satisfies (most shared content words), or None if unclear."""
    fact_words = tokens(fact) - set(GENERIC_RULE_WORDS)
    scored = sorted(((len(fact_words & (tokens(c) - set(GENERIC_RULE_WORDS))), c)
                     for c in _RECORD_CLAUSE_SPLIT.split(policy) if c.strip()), key=lambda x: -x[0])
    if not scored or scored[0][0] == 0 or (len(scored) > 1 and scored[1][0] == scored[0][0]):
        return None
    return scored[0][1]


_CMP = {">=": lambda a, b: a >= b, ">": lambda a, b: a > b, "<=": lambda a, b: a <= b,
        "<": lambda a, b: a < b, "==": lambda a, b: a == b}


def _norm(x) -> str:
    return re.sub(r"\s+", " ", str(x or "")).strip().lower()


def satisfies(fact: dict, cond: dict) -> bool | None:
    """Does this fact record meet this condition record? None if the value is unknown."""
    if fact.get("value") is None:
        return None
    if cond["kind"] == "credential":
        return fact["value"] is True
    return _CMP[cond["comparator"]](float(fact["value"]), float(cond["threshold"]))


def record_flags(system: dict, evaluation: dict) -> list[Flag]:
    recs = evaluation.get("records")
    if not recs:
        return []
    sid = system["scenario"]
    facts, conds = recs["facts"], recs["conditions"]
    text = {x["id"]: x["text"] for x in system["evidence"] + system["memories"] + system["updates"]}
    policy_for = {m: p for p, m in (evaluation.get("policy_of") or {}).items()}
    ptext = {p["id"]: p["text"] for p in system.get("policies", [])}
    flags: list[Flag] = []

    def hard(item, kind, match):
        flags.append(Flag(sid, item, kind, match, True))

    def soft(item, kind, match):
        flags.append(Flag(sid, item, kind, match, False))

    # Grounding: each fact record against its own text. A stated contradiction is hard; a
    # window or scope the record declares but the text leaves vague or unstated is soft
    # (the reviewer judges it, as approved for windows on 2026-10-20).
    for fid, f in facts.items():
        t = text.get(fid, "")
        if _norm(f["entity"]) not in _norm(t):
            hard(fid, "record_entity_not_in_text", f["entity"])
        if f["kind"] == "number":  # credentials have no value or accumulation window to ground
            if f.get("value") is not None and not _has_number(t, f["value"]):
                hard(fid, "record_value_not_in_text", str(f["value"]))
            tw = windows(t)
            known = tw - {"unknown"}
            if f["window"] == "none" and known:
                hard(fid, "record_window_not_in_text", f"record none, text {'/'.join(sorted(known))}")
            elif f["window"] != "none" and known and f["window"] not in known:
                hard(fid, "record_window_not_in_text", f"record {f['window']}, text {'/'.join(sorted(known))}")
            elif "unknown" in tw or (f["window"] != "none" and not known):
                soft(fid, "record_window_vague_in_text", f"record {f['window']}, text {'vague' if 'unknown' in tw else 'none'}")
        ts = scopes_in(t)
        if f["scope"] == "none" and ts:
            hard(fid, "record_scope_not_in_text", f"record none, text {'/'.join(sorted(ts))}")
        elif f["scope"] != "none" and ts and f["scope"] not in ts:
            hard(fid, "record_scope_not_in_text", f"record {f['scope']}, text {'/'.join(sorted(ts))}")
        elif f["scope"] != "none" and not ts:
            soft(fid, "record_scope_unstated_in_text", f"record {f['scope']}")

    # Agreement and condition grounding, per premise.
    for mid, clist in conds.items():
        pol = ptext.get(policy_for.get(mid, ""), "")
        for c in clist:
            item = f"{c['premise']}->{mid}"
            if _norm(c["entity"]) not in _norm(text.get(mid, "")):
                hard(item, "record_entity_not_in_memory", c["entity"])
            if c["kind"] == "conclusion":
                if _norm(c["entity"]) not in _norm(text.get(c["premise"], "")):
                    hard(item, "conclusion_about_other_entity", c["entity"])
                continue
            f = facts.get(c["premise"])
            if f is None:
                continue
            if c.get("relation"):
                if _norm(c["entity"]) not in _norm(text.get(c["premise"], "")):
                    hard(item, "relation_not_stated_in_fact", f"{c['relation']} {c['entity']}")
            elif _norm(f["entity"]) != _norm(c["entity"]):
                hard(item, "record_entity_mismatch", f"{f['entity']} vs {c['entity']}")
            for fld in ("kind", "quantity", "unit"):
                if _norm(f.get(fld)) != _norm(c.get(fld)):
                    hard(item, f"record_{fld}_mismatch", f"{f.get(fld)} vs {c.get(fld)}")
            for fld in ("window", "scope"):  # "none" in a condition means no restriction
                if c[fld] != "none" and f[fld] != c[fld]:
                    hard(item, f"record_{fld}_mismatch", f"fact {f[fld]} vs condition {c[fld]}")
            if satisfies(f, c) is False:
                hard(item, "record_condition_not_met", f"{f.get('value')} {c.get('comparator') or ''} {c.get('threshold')}")
            # Condition grounding against the policy text.
            if c["kind"] == "number" and not _has_number(pol, c["threshold"]):
                hard(item, "record_threshold_not_in_policy", str(c["threshold"]))
            clause = condition_clause(text.get(c["premise"], ""), pol)
            if c["window"] != "none" and c["window"] not in windows(pol):
                hard(item, "record_window_not_in_policy", c["window"])
            elif c["window"] == "none" and clause is not None and windows(clause) - {"unknown"}:
                hard(item, "record_window_not_in_policy", f"record none, clause {'/'.join(sorted(windows(clause)))}")
            if c["scope"] != "none" and c["scope"] not in scopes_in(pol):
                hard(item, "record_scope_not_in_policy", c["scope"])
            elif c["scope"] == "none" and clause is not None and scopes_in(clause):
                # Soft (2026-10-20, pilot-4b F6 attempt 1): outcome names often carry scope
                # words ("Listing in national inventory schedules"), which clause splitting
                # cannot always separate from the condition. A stated different scope stays hard.
                soft(item, "record_scope_word_in_policy_clause",
                     f"record none, clause {'/'.join(sorted(scopes_in(clause)))}")

    # Updates: a superseding value keeps the target's quantity, unit, window and scope.
    targets = evaluation.get("update_targets") or {}
    for uid, u in targets.items():
        uf, tf = facts.get(uid), facts.get(u["target"])
        if not uf or not tf or u["relation"] != "supersedes":
            continue
        for fld in ("entity", "kind", "quantity", "unit"):
            if _norm(uf.get(fld)) != _norm(tf.get(fld)):
                hard(uid, f"update_{fld}_mismatch", f"{tf.get(fld)} -> {uf.get(fld)}")
        for fld in ("window", "scope"):  # different stated values are hard; one unstated is soft
            a, b = tf.get(fld), uf.get(fld)
            if a != b and "none" not in (a, b):
                hard(uid, f"update_{fld}_mismatch", f"{a} -> {b}")
            elif a != b:
                soft(uid, f"update_{fld}_unstated", f"{a} -> {b}")

    # Outcome: with superseding updates only, recompute every memory and compare with the
    # renderer's own after-update judgement (which consistency_flags ties to gold).
    if targets and all(u["relation"] == "supersedes" for u in targets.values()):
        after = dict(facts)
        for uid, u in targets.items():
            if uid in facts:
                after[u["target"]] = facts[uid]
        memo: dict[str, bool | None] = {}

        def holds(mid: str) -> bool | None:
            if mid in memo:
                return memo[mid]
            memo[mid] = None
            best: bool | None = False
            for j in evaluation["justifications"].get(mid, []):
                ok: bool | None = True
                for p in j:
                    c = next((c for c in conds.get(mid, []) if c["premise"] == p), None)
                    r = holds(p) if p in conds else (satisfies(after[p], c) if c and p in after else None)
                    ok = False if r is False or ok is False else (None if r is None else ok)
                best = True if ok is True or best is True else (None if ok is None else best)
            memo[mid] = best
            return best

        expected = {True: "holds", False: "fails"}
        for mid in conds:
            got, said = holds(mid), (evaluation.get("after_updates") or {}).get(mid)
            if got is not None and said is not None and expected[got] != said:
                hard(mid, "record_outcome_mismatch", f"records give {expected[got]}, renderer says {said}")
    return flags


def hard_flags(system: dict, evaluation: dict, prompt_version: str) -> list[Flag]:
    """The hard checks a rendering under ``prompt_version`` must pass to be accepted (the
    same set for a fresh rendering and for a targeted repair)."""
    flags = (text_flags(system) + echo_flags(system, evidence_echo_hard(prompt_version))
             + decoy_word_flags(system, evaluation)
             + (continuity_flags(system, evaluation) if continuity_enforced(prompt_version) else [])
             + record_flags(system, evaluation))
    return [f for f in flags if f.hard]


LEXICAL_GATE = 0.50  # prespecified: max justification-set F1 of either heuristic


def _pr(score: ExtractionScore) -> dict:
    def p(c):
        return c["tp"] / (c["tp"] + c["fp"]) if c["tp"] + c["fp"] else None

    def r(c):
        return c["tp"] / (c["tp"] + c["fn"]) if c["tp"] + c["fn"] else None

    return {"edge_precision": p(score.edge), "edge_recall": r(score.edge),
            "justification_set_precision": p(score.jset), "justification_set_recall": r(score.jset)}


@dataclass
class LeakReport:
    flags: list[Flag] = field(default_factory=list)
    lexical: ExtractionScore = field(default_factory=ExtractionScore)
    policy_lexical: ExtractionScore = field(default_factory=ExtractionScore)
    aucs: dict[str, float | None] = field(default_factory=dict)
    templates: list[tuple[str, float]] = field(default_factory=list)

    @property
    def hard_flags(self) -> list[Flag]:
        return [f for f in self.flags if f.hard]

    def summary(self) -> dict:
        aucs = [a for a in self.aucs.values() if a is not None]
        lex = self.lexical.summary() | _pr(self.lexical)
        pol = self.policy_lexical.summary() | _pr(self.policy_lexical)
        worst = max(lex["justification_set_f1"], pol["justification_set_f1"])
        return {
            "scenarios": len(self.aucs),
            "hard_flags": len(self.hard_flags),
            "soft_flags": len(self.flags) - len(self.hard_flags),
            "soft_flag_kinds": dict(Counter(f.kind for f in self.flags if not f.hard)),
            "lexical_heuristic": lex,
            "policy_assisted_heuristic": pol,
            "lexical_gate": {"threshold": LEXICAL_GATE, "worst_set_f1": worst, "pass": worst <= LEXICAL_GATE},
            "premise_overlap_auc_mean": sum(aucs) / len(aucs) if aucs else None,
            "template_trigrams": self.templates,
        }


def check(pairs: list[tuple[dict, dict]], evidence_hard: bool = True, continuity: bool = False) -> LeakReport:
    """Run every check over (system_view, eval_view) pairs. ``continuity`` adds the
    render-v8 reference checks (off for versions rendered before they existed)."""
    rep = LeakReport()
    for system, evaluation in pairs:
        rep.flags += (text_flags(system) + echo_flags(system, evidence_hard) + group_flags(system, evaluation)
                      + consistency_flags(system, evaluation) + relation_flags(system, evaluation)
                      + decoy_word_flags(system, evaluation))
        if continuity:
            rep.flags += continuity_flags(system, evaluation)
        rep.lexical.add(evaluation["justifications"], lexical_justifications(system))
        rep.policy_lexical.add(evaluation["justifications"], policy_assisted_justifications(system))
        rep.aucs[system["scenario"]] = premise_overlap_auc(system, evaluation)
    rep.templates = template_flags([s for s, _ in pairs])
    return rep
