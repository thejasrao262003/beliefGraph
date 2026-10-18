"""Automated leakage checks on rendered scenarios. They raise *flags for review*, never
automatic rejections, except hard leaks (ids, schema keys, label words) in the system view.

1. Forbidden text: graph ids, label vocabulary, explicit support language, source counts.
2. Lexical structure recovery: how much of the gold justification structure a
   bag-of-words heuristic recovers from the system view alone. If word matching
   recovers the graph, the benchmark measures lexical matching, not inference.
3. Template repetition across scenarios.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from beliefbench.metrics import ExtractionScore
from beliefbench.render.views import SYSTEM_VIEW_KEYS

HARD = {
    "graph_id": re.compile(r"\b[EBDU]\d{1,2}\b|\b[emu]_[0-9a-f]{4}\b"),
    "label_word": re.compile(r"\b(premise|justification|dependenc(y|ies)|gold|withdraw|recompute|supersede[sd]?|node)\b", re.I),
}
# Only flagged in memories (beliefs / decisions): a memory should state a conclusion, not its reasons.
SOFT_MEMORY = {
    "explains_reason": re.compile(
        r"\b(because|since|therefore|thus|hence|as a result|given that|based on|according to|due to|"
        r"which means|supported by|confirmed by|so that)\b", re.I),
    "mentions_sources": re.compile(
        r"\b(both|either|two|three|several|multiple|independent(ly)?)\s+(sources?|reports?|records?|documents?)\b|"
        r"\b(sources?|reports?|evidence|records? show)\b", re.I),
}
SOFT_UPDATE = {
    "update_mentions_implication": re.compile(r"\b(therefore|which means|so (we|you) should|as a result|no longer recommend)\b", re.I),
}

STOP = set("""a an the of to in on at for from by with and or but not no is are was were be been being has have had
do does did this that these those it its as into than then there their they them he she his her we our you your
i me my will would can could should may might must about over under after before during per via each any all
some more most less least very also only just new now""".split())


def tokens(text: str) -> set[str]:
    out = set()
    for w in re.findall(r"[a-z0-9]+", text.lower()):
        if w in STOP or len(w) < 2:
            continue
        out.add(w[:-1] if len(w) > 3 and w.endswith("s") else w)
    return out


def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a | b else 0.0


@dataclass
class Flag:
    scenario: str
    item: str
    kind: str
    match: str
    hard: bool


def text_flags(system: dict) -> list[Flag]:
    flags: list[Flag] = []
    sid = system["scenario"]
    extra = set(system) - SYSTEM_VIEW_KEYS
    if extra:
        flags.append(Flag(sid, "-", "unexpected_key", ",".join(sorted(extra)), True))
    items = [("evidence", e) for e in system["evidence"]] + [("memory", m) for m in system["memories"]] + \
            [("update", u) for u in system["updates"]]
    for kind, item in items:
        fields = [item["text"]] + ([item["source"]] if "source" in item else [])
        for text in fields:
            for name, pat in HARD.items():
                if m := pat.search(text):
                    flags.append(Flag(sid, item["id"], name, m.group(0), True))
            soft = SOFT_MEMORY if kind == "memory" else SOFT_UPDATE if kind == "update" else {}
            for name, pat in soft.items():
                if m := pat.search(text):
                    flags.append(Flag(sid, item["id"], name, m.group(0), False))
    return flags


def lexical_justifications(system: dict, abs_threshold: float = 0.15, rel_threshold: float = 0.6) -> dict:
    """Bag-of-words structure guess: for each memory, the candidates (all evidence and
    other memories) whose token overlap is >= rel_threshold * best and >= abs_threshold,
    as one AND-set. A deliberately simple floor that any real extractor must beat."""
    texts = {e["id"]: tokens(e["text"]) for e in system["evidence"]} | \
            {m["id"]: tokens(m["text"]) for m in system["memories"]}
    pred = {}
    for m in system["memories"]:
        scores = {c: jaccard(texts[m["id"]], t) for c, t in texts.items() if c != m["id"]}
        best = max(scores.values(), default=0.0)
        chosen = sorted(c for c, v in scores.items() if v >= abs_threshold and v >= rel_threshold * best)
        pred[m["id"]] = [chosen] if chosen else []
    return pred


def premise_overlap_auc(system: dict, evaluation: dict) -> float | None:
    """P(a true premise has higher overlap with its conclusion than a non-premise), over
    all memories. 0.5 = no lexical signal; 1.0 = wording fully separates premises.
    Shared entity names legitimately push this above 0.5, so it is only a review flag."""
    texts = {e["id"]: tokens(e["text"]) for e in system["evidence"]} | \
            {m["id"]: tokens(m["text"]) for m in system["memories"]}
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
            words = [w for w in re.findall(r"[a-z]+", m["text"].lower())]
            grams = {tuple(words[i : i + 3]) for i in range(len(words) - 2)}
            for g in grams:
                if all(w in STOP for w in g):
                    continue
                gram_count[g] += 1
                gram_scen.setdefault(g, set()).add(sv["scenario"])
    return sorted(
        ((" ".join(g), c / n_mem) for g, c in gram_count.items()
         if n_mem and c / n_mem > max_share and len(gram_scen[g]) >= min_scenarios),
        key=lambda x: -x[1],
    )


@dataclass
class LeakReport:
    flags: list[Flag] = field(default_factory=list)
    lexical: ExtractionScore = field(default_factory=ExtractionScore)
    aucs: dict[str, float | None] = field(default_factory=dict)
    templates: list[tuple[str, float]] = field(default_factory=list)

    @property
    def hard_flags(self) -> list[Flag]:
        return [f for f in self.flags if f.hard]

    def summary(self) -> dict:
        aucs = [a for a in self.aucs.values() if a is not None]
        return {
            "scenarios": len(self.aucs),
            "hard_flags": len(self.hard_flags),
            "soft_flags": len(self.flags) - len(self.hard_flags),
            "lexical_heuristic": self.lexical.summary(),
            "premise_overlap_auc_mean": sum(aucs) / len(aucs) if aucs else None,
            "template_trigrams": self.templates,
        }


def check(pairs: list[tuple[dict, dict]]) -> LeakReport:
    """Run every check over (system_view, eval_view) pairs."""
    rep = LeakReport()
    for system, evaluation in pairs:
        rep.flags += text_flags(system)
        rep.lexical.add(evaluation["justifications"], lexical_justifications(system))
        rep.aucs[system["scenario"]] = premise_overlap_auc(system, evaluation)
    rep.templates = template_flags([s for s, _ in pairs])
    return rep
