"""Candidate retrieval for large stores (v0.2): a small model builds a memory's graph from
the few items most related to it, not from the whole store. TF-IDF cosine over word
tokens; no model calls, no external dependencies."""

from __future__ import annotations

import math
import re
from collections import Counter

_STOP = set("""a an the of to in on at for from by with and or but not no is are was were be been has have had
it its as this that these those than then any all each every per its into over under after before about""".split())


def _tokens(text: str) -> list[str]:
    out = []
    for w in re.findall(r"[a-z0-9]+", text.lower()):
        if w in _STOP or len(w) < 2:
            continue
        out.append(w[:-1] if len(w) > 3 and w.endswith("s") else w)
    return out


class Index:
    """TF-IDF index over (id, text) items."""

    def __init__(self, items: list[tuple[str, str]]):
        self.ids = [i for i, _ in items]
        docs = [Counter(_tokens(t)) for _, t in items]
        df = Counter(w for d in docs for w in d)
        n = len(docs)
        self.idf = {w: math.log((1 + n) / (1 + c)) + 1 for w, c in df.items()}
        self.vecs = [self._vec(d) for d in docs]

    def _vec(self, counts: Counter) -> dict[str, float]:
        v = {w: c * self.idf.get(w, 0.0) for w, c in counts.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {w: x / norm for w, x in v.items()}

    def top(self, text: str, k: int, exclude: set[str] = frozenset()) -> list[str]:
        q = self._vec(Counter(_tokens(text)))
        scored = sorted(((sum(q.get(w, 0.0) * x for w, x in v.items()), i)
                         for i, v in zip(self.ids, self.vecs) if i not in exclude), reverse=True)
        return [i for s, i in scored[:k] if s > 0]


def neighbourhood(view: dict, memory_ids: list[str], k_items: int = 12, k_policies: int = 4) -> dict:
    """A reduced snapshot for building ``memory_ids``: those memories, their ``k_items``
    nearest facts and memories, and their ``k_policies`` nearest policies, by TF-IDF.
    Memories reached are expanded once more (so a chain's upstream conclusion and its own
    facts come along)."""
    facts = {e["id"]: e for e in view["evidence"]}
    mems = {m["id"]: m for m in view["memories"]}
    items = Index([(i, x["text"]) for i, x in {**facts, **mems}.items()])
    pols = Index([(p["id"], p["text"]) for p in view.get("policies", [])])
    keep_items, keep_pols = set(memory_ids), set()
    frontier = list(memory_ids)
    for depth in range(2):
        nxt = []
        for mid in frontier:
            near = items.top(mems[mid]["text"], k_items, exclude={mid})
            keep_items.update(near)
            keep_pols.update(pols.top(mems[mid]["text"], k_policies))
            nxt += [x for x in near if x in mems and x not in memory_ids]
        frontier = nxt if depth == 0 else []
    return dict(view,
                evidence=[e for e in view["evidence"] if e["id"] in keep_items],
                memories=[m for m in view["memories"] if m["id"] in keep_items],
                policies=[p for p in view.get("policies", []) if p["id"] in keep_pols])


def facts_near(view: dict, text: str, k: int = 10) -> dict:
    """A reduced snapshot for reading one update: the ``k`` facts nearest to its text."""
    idx = Index([(e["id"], e["text"]) for e in view["evidence"]])
    near = set(idx.top(text, k))
    return dict(view, evidence=[e for e in view["evidence"] if e["id"] in near])


class DenseIndex:
    """Embedding retrieval (paraphrase-robust; policies name outcomes in other words than the
    memories that come from them). Uses fastembed (ONNX, CPU) when installed; falls back to
    TF-IDF otherwise. Vectors are normalised, so a dot product is a cosine."""

    MODEL = "nomic-ai/nomic-embed-text-v1.5"
    _models: dict = {}

    def __init__(self, items: list[tuple[str, str]], model: str | None = None):
        self.ids = [i for i, _ in items]
        self.model_name = model or self.MODEL
        try:
            import os

            if os.environ.get("BELIEFGRAPH_RETRIEVAL") == "tfidf":
                raise ImportError("TF-IDF forced")
            import numpy as np
            from fastembed import TextEmbedding
        except ImportError:
            self.np, self.tfidf = None, Index(items)
            return
        self.np = np
        if self.model_name not in self._models:
            self._models[self.model_name] = TextEmbedding(self.model_name)
        self.model = self._models[self.model_name]
        self.vecs = self._embed([t for _, t in items]) if items else np.zeros((0, 1))

    def _embed(self, texts: list[str]):
        np = self.np
        X = np.array(list(self.model.embed(texts)))
        return X / np.linalg.norm(X, axis=1, keepdims=True)

    def rank(self, text: str, exclude: set[str] = frozenset()) -> list[str]:
        if self.np is None:  # a full ranking, as the dense one: no-overlap items come last
            top = self.tfidf.top(text, len(self.tfidf.ids), exclude)
            return top + [i for i in self.ids if i not in exclude and i not in set(top)]
        order = self.np.argsort(-(self.vecs @ self._embed([text])[0]))
        return [self.ids[j] for j in order if self.ids[j] not in exclude]
