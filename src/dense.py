"""Dense retrieval over the Day 6 pgvector index; implements the starter Retriever protocol."""
from __future__ import annotations

import os
from typing import Any

import psycopg

from .day6.embeddings import MyEmbedder
from .day6.store import PgVectorStore

# Day 7 chunk fields -> Day 6 table columns allowed as filters.
FILTER_KEYS = {"section": "section", "page": "page", "source_id": "document_id"}


def to_day7_chunk(row: dict[str, Any], rank: int, strategy: str) -> dict[str, Any]:
    """Map a PgVectorStore.search row to the Day 7 chunk format, with score and rank."""
    return {
        "id": row["chunk_id"],
        "text": row["text"],
        "source_id": row["document_id"],
        "source": row["source"],
        "page": row["page"],
        "score": row["score"],
        "rank": rank,
        "retriever": "dense",
        "metadata": {
            "printed_page": row["printed_page"],
            "section": row["section"],
            "chunk_index": row["chunk_index"],
            "char_start": row["char_start"],
            "char_end": row["char_end"],
            "day6_strategy": strategy,
        },
    }


def map_filters(filters: dict[str, Any] | None) -> dict[str, Any] | None:
    if not filters:
        return None
    unknown = set(filters) - set(FILTER_KEYS)
    if unknown:
        raise ValueError(f"unsupported filter keys: {sorted(unknown)}; allowed: {sorted(FILTER_KEYS)}")
    return {FILTER_KEYS[k]: v for k, v in filters.items()}


class DenseRetriever:
    """Embed the query with the Day 6 model and run exact cosine search in pgvector.

    On init it checks that the stored vectors were made by the same model, so query and
    document embeddings are always compatible. Errors propagate; there is no fallback.
    """

    def __init__(self, database_url: str | None = None, model_name: str | None = None,
                 strategy: str = "B", embedder: Any = None) -> None:
        self.database_url = database_url or os.environ["DATABASE_URL"]
        self.strategy = strategy
        self.embedder = embedder or MyEmbedder(model_name or os.environ["EMBEDDING_MODEL"])
        self.store = PgVectorStore(self.database_url, self.embedder.dimensions)
        self._check_index()

    def _check_index(self) -> None:
        with psycopg.connect(self.database_url, connect_timeout=5) as conn:
            models = [r[0] for r in conn.execute(
                "SELECT DISTINCT model FROM chunks WHERE strategy = %s", (self.strategy,)).fetchall()]
        if not models:
            raise RuntimeError(f"no chunks for strategy {self.strategy!r} in the Day 6 index")
        if models != [self.embedder.model_name]:
            raise RuntimeError(f"index built with {models}, query model is {self.embedder.model_name!r}")

    def info(self) -> dict[str, Any]:
        return {"retriever": "dense", "backend": "pgvector exact cosine", "strategy": self.strategy,
                "model": self.embedder.model_name, "dimensions": self.embedder.dimensions}

    def search(self, query: str, *, filters: dict[str, Any] | None = None,
               top_k: int = 3) -> list[dict[str, Any]]:
        if not query.strip() or top_k < 1:
            raise ValueError("query must be non-empty and top_k >= 1")
        rows = self.store.search(self.strategy, self.embedder.embed_query(query),
                                 top_k=top_k, filters=map_filters(filters))
        return [to_day7_chunk(r, i, self.strategy) for i, r in enumerate(rows, 1)]
