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
    capitalised word are skipped: product, programme and standard names may be shared."""
    def grams(text: str) -> set[tuple[str, ...]]:
        words = re.findall(r"[A-Za-z0-9$%-]+", text)
        out = set()
        for i in range(len(words) - n + 1):
            g = words[i : i + n]
            if any(w[0].isupper() for w in g):
                continue
            low = tuple(w.lower() for w in g)
            if sum(w not in STOP for w in low) >= 2:
                out.add(low)
        return out

    return {" ".join(g) for g in grams(a) & grams(b)}


def echo_flags(system: dict) -> list[Flag]:
    """render-v4 hard rule: no ordinary 3-word phrase shared by a memory and any policy.
    Such echoes let a reader map memory -> policy -> premise memories by string matching
    (smoke test 3, F1 and F2)."""
    flags = []
    for m in system["memories"]:
        for p in system.get("policies", []):
            shared = shared_phrases(m["text"], p["text"])
            if shared:
                flags.append(Flag(system["scenario"], f"{m['id']}~{p['id']}", "policy_echoes_memory",
                                  "; ".join(sorted(shared)), True))
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


def check(pairs: list[tuple[dict, dict]]) -> LeakReport:
    """Run every check over (system_view, eval_view) pairs."""
    rep = LeakReport()
    for system, evaluation in pairs:
        rep.flags += (text_flags(system) + echo_flags(system) + group_flags(system, evaluation)
                      + consistency_flags(system, evaluation) + relation_flags(system, evaluation)
                      + decoy_word_flags(system, evaluation))
        rep.lexical.add(evaluation["justifications"], lexical_justifications(system))
        rep.policy_lexical.add(evaluation["justifications"], policy_assisted_justifications(system))
        rep.aucs[system["scenario"]] = premise_overlap_auc(system, evaluation)
    rep.templates = template_flags([s for s, _ in pairs])
    return rep
