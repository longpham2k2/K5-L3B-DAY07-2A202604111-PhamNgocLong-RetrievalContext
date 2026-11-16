"""Store and search vectors in PostgreSQL + pgvector (exact cosine search)."""
from __future__ import annotations

import hashlib
import json
from typing import Any

import psycopg

from .models import Chunk

TABLE = "chunks"
# Only these metadata columns may be used as filters; values are always bound parameters.
FILTERABLE = {"section", "page", "document_id"}


def _vec(v: list[float]) -> str:
    return "[" + ",".join(f"{x:.7f}" for x in v) + "]"


class PgVectorStore:
    def __init__(self, database_url: str, dimensions: int) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be positive")
        self.database_url = database_url
        self.dimensions = dimensions

    def _connect(self) -> psycopg.Connection:
        return psycopg.connect(self.database_url, connect_timeout=5)

    def create_schema(self) -> None:
        with self._connect() as conn:
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLE} (
                    chunk_id      text PRIMARY KEY,
                    strategy      text NOT NULL,
                    document_id   text NOT NULL,
                    source        text NOT NULL,
                    page          integer NOT NULL,
                    printed_page  integer,
                    section       text NOT NULL,
                    chunk_index   integer NOT NULL,
                    char_start    integer NOT NULL,
                    char_end      integer NOT NULL,
                    text          text NOT NULL,
                    content_hash  text NOT NULL,
                    model         text NOT NULL,
                    embedding     vector({self.dimensions}) NOT NULL
                )""")
            row = conn.execute(
                "SELECT format_type(atttypid, atttypmod) FROM pg_attribute "
                "WHERE attrelid = %s::regclass AND attname = 'embedding'", (TABLE,)).fetchone()
            if row[0] != f"vector({self.dimensions})":
                raise RuntimeError(f"existing table has {row[0]}, model needs vector({self.dimensions}); "
                                   f"drop table {TABLE} to switch models")
            # No B-tree index on (strategy, section): at a few hundred rows a sequential scan is
            # just as fast, and such an index would stop the planner from using HNSW in the
            # side experiment. Indexes never change exact-search results.
            conn.execute(f"DROP INDEX IF EXISTS {TABLE}_strategy_section")

    def count(self, strategy: str | None = None) -> int:
        with self._connect() as conn:
            if strategy:
                return conn.execute(f"SELECT count(*) FROM {TABLE} WHERE strategy = %s", (strategy,)).fetchone()[0]
            return conn.execute(f"SELECT count(*) FROM {TABLE}").fetchone()[0]

    def upsert(self, strategy: str, chunks: list[Chunk], vectors: list[list[float]],
               model: str) -> dict[str, int]:
        """Insert/update by stable chunk_id; delete this strategy's chunks that no longer exist.

        Rows whose text hash and model are unchanged are left untouched, so re-ingesting
        the same version is a no-op (inserted = updated = deleted = 0).
        """
        if len(chunks) != len(vectors):
            raise ValueError(f"{len(chunks)} chunks but {len(vectors)} vectors")
        if any(len(v) != self.dimensions for v in vectors):
            raise ValueError(f"vector size must be {self.dimensions}")
        ids = [c.chunk_id for c in chunks]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate chunk_id in batch")
        stats = {"inserted": 0, "updated": 0, "unchanged": 0, "deleted": 0}
        with self._connect() as conn, conn.transaction():
            existing = dict(conn.execute(
                f"SELECT chunk_id, content_hash || '|' || model FROM {TABLE} WHERE strategy = %s",
                (strategy,)).fetchall())
            for c, v in zip(chunks, vectors):
                h = hashlib.sha256(c.text.encode("utf-8")).hexdigest()
                if existing.get(c.chunk_id) == f"{h}|{model}":
                    stats["unchanged"] += 1
                    continue
                stats["updated" if c.chunk_id in existing else "inserted"] += 1
                m = c.metadata
                conn.execute(f"""
                    INSERT INTO {TABLE} (chunk_id, strategy, document_id, source, page, printed_page,
                        section, chunk_index, char_start, char_end, text, content_hash, model, embedding)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::vector)
                    ON CONFLICT (chunk_id) DO UPDATE SET
                        strategy=EXCLUDED.strategy, document_id=EXCLUDED.document_id, source=EXCLUDED.source,
                        page=EXCLUDED.page, printed_page=EXCLUDED.printed_page, section=EXCLUDED.section,
                        chunk_index=EXCLUDED.chunk_index, char_start=EXCLUDED.char_start,
                        char_end=EXCLUDED.char_end, text=EXCLUDED.text, content_hash=EXCLUDED.content_hash,
                        model=EXCLUDED.model, embedding=EXCLUDED.embedding""",
                    (c.chunk_id, strategy, c.document_id, c.source, c.page, m.get("printed_page"),
                     m["section"], m["chunk_index"], m["char_start"], m["char_end"], c.text, h, model, _vec(v)))
            obsolete = [cid for cid in existing if cid not in set(ids)]
            if obsolete:
                conn.execute(f"DELETE FROM {TABLE} WHERE strategy = %s AND chunk_id = ANY(%s)",
                             (strategy, obsolete))
            stats["deleted"] = len(obsolete)
        return stats

    def create_ann_index(self, strategy: str, m: int = 16, ef_construction: int = 64) -> str:
        """Partial HNSW index (cosine) over one strategy's rows. Side experiment only."""
        if not strategy.isalnum():
            raise ValueError("strategy name must be alphanumeric")
        name = f"{TABLE}_hnsw_{strategy.lower()}"
        with self._connect() as conn:
            conn.execute(f"CREATE INDEX IF NOT EXISTS {name} ON {TABLE} USING hnsw "
                         f"(embedding vector_cosine_ops) WITH (m = {int(m)}, ef_construction = {int(ef_construction)}) "
                         f"WHERE strategy = '{strategy}'")
        return name

    def search(self, strategy: str, query_vector: list[float], top_k: int = 3,
               filters: dict[str, Any] | None = None,
               ann: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Cosine search within one strategy, optional metadata filter.

        ann=None  -> exact search (all matching rows ranked; the official A/B/C setting).
        ann={...} -> force the HNSW index (approximate) with the given ef_search and
                     iterative_scan; EXPLAIN verifies the index is really used.
        """
        if len(query_vector) != self.dimensions:
            raise ValueError(f"query vector size must be {self.dimensions}")
        where, params = ["strategy = %s"], [strategy]
        for key, value in (filters or {}).items():
            if key not in FILTERABLE:
                raise ValueError(f"filter on {key!r} is not allowed")
            where.append(f"{key} = %s")
            params.append(value)
        qv = _vec(query_vector)
        # An HNSW index can only serve ORDER BY <distance> LIMIT k, so no tie-breaker in ANN mode.
        order = "embedding <=> %s::vector" + ("" if ann else ", chunk_id")
        sql = (f"SELECT chunk_id, document_id, source, page, printed_page, section, chunk_index, "
               f"char_start, char_end, text, 1 - (embedding <=> %s::vector) AS score "
               f"FROM {TABLE} WHERE {' AND '.join(where)} ORDER BY {order} LIMIT %s")
        args = [qv, *params, qv, top_k]
        with self._connect() as conn, conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            if ann:
                if ann.get("iterative_scan", "off") not in ("off", "strict_order", "relaxed_order"):
                    raise ValueError("bad iterative_scan")
                cur.execute("SET LOCAL enable_seqscan = off")
                cur.execute("SET LOCAL enable_bitmapscan = off")
                cur.execute(f"SET LOCAL hnsw.ef_search = {int(ann.get('ef_search', 40))}")
                cur.execute(f"SET LOCAL hnsw.iterative_scan = {ann.get('iterative_scan', 'off')}")
                cur.execute("EXPLAIN (FORMAT JSON) " + sql, args)
                plan = json.dumps(cur.fetchone()["QUERY PLAN"])
                index = f"{TABLE}_hnsw_{strategy.lower()}"
                if index not in plan:
                    raise RuntimeError(f"HNSW index {index} not used by the planner; ANN result would be invalid")
            cur.execute(sql, args)
            rows = cur.fetchall()
        for r in rows:
            r["score"] = round(float(r["score"]), 4)
        return rows
