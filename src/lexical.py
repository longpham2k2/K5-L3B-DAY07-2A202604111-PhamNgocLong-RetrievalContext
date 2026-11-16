"""Lexical (BM25) and hybrid (dense + BM25, Reciprocal Rank Fusion) retrievers.

Both search the same chunks as the Day 6 dense index (data/day6/chunks.json, strategy B),
apply the same metadata filters and return the same Day 7 chunk format with score and rank.
"""
from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from typing import Any, Protocol

FILTER_KEYS = ("section", "page", "source_id")


def tokenize(text: str) -> list[str]:
    """Unicode word tokens, case-folded. The corpus is English, so no Vietnamese segmentation."""
    return re.findall(r"\w+", unicodedata.normalize("NFC", text).casefold())


def matches(chunk: dict[str, Any], filters: dict[str, Any] | None) -> bool:
    if not filters:
        return True
    unknown = set(filters) - set(FILTER_KEYS)
    if unknown:
        raise ValueError(f"unsupported filter keys: {sorted(unknown)}; allowed: {list(FILTER_KEYS)}")
    for key, value in filters.items():
        actual = chunk["source_id"] if key == "source_id" else chunk["page"] if key == "page" else chunk["metadata"].get(key)
        if actual != value:
            return False
    return True


class Retriever(Protocol):
    def search(self, query: str, *, filters: dict[str, Any] | None = None, top_k: int = 3) -> list[dict[str, Any]]: ...
    def info(self) -> dict[str, Any]: ...


class BM25Retriever:
    """Okapi BM25 over chunk text (k1=1.5, b=0.75 by default). In-memory, standard library only."""

    def __init__(self, chunks: list[dict[str, Any]], k1: float = 1.5, b: float = 0.75) -> None:
        if not chunks:
            raise ValueError("BM25 needs at least one chunk")
        self.chunks, self.k1, self.b = chunks, k1, b
        self.tf = [Counter(tokenize(c["text"])) for c in chunks]
        self.len = [sum(t.values()) for t in self.tf]
        self.avg_len = sum(self.len) / len(self.len)
        df = Counter(term for t in self.tf for term in t)
        n = len(chunks)
        self.idf = {term: math.log(1 + (n - d + 0.5) / (d + 0.5)) for term, d in df.items()}

    def info(self) -> dict[str, Any]:
        return {"retriever": "bm25", "k1": self.k1, "b": self.b, "chunks": len(self.chunks),
                "tokenizer": "unicode \\w+ casefold"}

    def search(self, query: str, *, filters: dict[str, Any] | None = None, top_k: int = 3) -> list[dict[str, Any]]:
        if not query.strip() or top_k < 1:
            raise ValueError("query must be non-empty and top_k >= 1")
        terms = set(tokenize(query))
        scored = []
        for chunk, tf, length in zip(self.chunks, self.tf, self.len):
            if not matches(chunk, filters):
                continue
            score = 0.0
            for term in terms:
                f = tf.get(term, 0)
                if f:
                    score += self.idf[term] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * length / self.avg_len))
            if score > 0:
                scored.append((score, chunk))
        scored.sort(key=lambda x: (-x[0], x[1]["id"]))
        return [{**c, "score": round(s, 4), "rank": i, "retriever": "bm25"}
                for i, (s, c) in enumerate(scored[:top_k], 1)]


class HybridRetriever:
    """Reciprocal Rank Fusion of dense and BM25: score = sum over retrievers of 1 / (k + rank).

    RRF uses ranks only, so cosine and BM25 scores never need to be put on one scale. Each
    retriever contributes its top `candidates`; component ranks are kept in metadata.
    """

    def __init__(self, dense: Retriever, lexical: Retriever, k: int = 60, candidates: int = 20) -> None:
        self.dense, self.lexical, self.k, self.candidates = dense, lexical, k, candidates

    def info(self) -> dict[str, Any]:
        return {"retriever": "hybrid_rrf", "rrf_k": self.k, "candidates_per_retriever": self.candidates,
                "components": [self.dense.info(), self.lexical.info()]}

    def search(self, query: str, *, filters: dict[str, Any] | None = None, top_k: int = 3) -> list[dict[str, Any]]:
        if not query.strip() or top_k < 1:
            raise ValueError("query must be non-empty and top_k >= 1")
        fused: dict[str, dict[str, Any]] = {}
        for name, retriever in (("dense", self.dense), ("bm25", self.lexical)):
            for r in retriever.search(query, filters=filters, top_k=self.candidates):
                entry = fused.setdefault(r["id"], {"chunk": r, "score": 0.0, "ranks": {}})
                entry["score"] += 1 / (self.k + r["rank"])
                entry["ranks"][name] = r["rank"]
        ordered = sorted(fused.values(), key=lambda e: (-e["score"], e["chunk"]["id"]))[:top_k]
        out = []
        for i, e in enumerate(ordered, 1):
            c = e["chunk"]
            out.append({**c, "score": round(e["score"], 6), "rank": i, "retriever": "hybrid_rrf",
                        "metadata": {**c["metadata"], "component_ranks": e["ranks"]}})
        return out
