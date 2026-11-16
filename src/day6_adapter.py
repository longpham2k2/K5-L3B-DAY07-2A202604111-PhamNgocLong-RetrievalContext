"""Export Day 6 chunks (from pgvector) and benchmark questions into the Day 7 JSON format.

Run from the repo root:
    python -m src.day6_adapter --day6-dir ../K5-L3B-DAY06-PhamNgocLong-2A202604111-DataIngestion

Writes data/day6/chunks.json, data/day6/questions.json and data/day6/export_manifest.json.
Chunks come from the database (not chunks_B.jsonl) so IDs, text and metadata are exactly
what dense search returns. Gold fields are only copied into questions.json for evaluation;
they never go to the agent or the retrievers.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHUNK_COLUMNS = ("chunk_id", "document_id", "source", "page", "printed_page", "section",
                 "chunk_index", "char_start", "char_end", "text", "model")


def chunk_from_row(row: dict[str, Any], strategy: str) -> dict[str, Any]:
    """Map one row of the Day 6 `chunks` table to the Day 7 chunk contract."""
    return {
        "id": row["chunk_id"],
        "text": row["text"],
        "source_id": row["document_id"],
        "source": row["source"],
        "page": row["page"],
        "metadata": {
            "printed_page": row["printed_page"],
            "section": row["section"],
            "chunk_index": row["chunk_index"],
            "char_start": row["char_start"],
            "char_end": row["char_end"],
            "day6_strategy": strategy,
            "embedding_model": row["model"],
        },
    }


def question_from_day6(q: dict[str, Any]) -> dict[str, Any]:
    """Map one Day 6 benchmark question to the Day 7 answerable-question contract."""
    out = {
        "id": q["id"],
        "split": q["split"],
        "question": q["question"],
        "answerable": True,
        "expected_behavior": "search_and_answer",
        "expected_answer": q["expected_answer"],
        "gold": [{"source_id": q["gold_source_id"], "page": q["gold_page"],
                  "evidence": q["evidence_quote"]}],
        "type": q.get("type"),
    }
    if q.get("filter"):
        out["filter"] = q["filter"]
    return out


def load_day6_questions(path: Path) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    items = raw["questions"] if isinstance(raw, dict) else raw
    if not isinstance(items, list) or not items:
        raise ValueError(f"{path}: expected a non-empty question list")
    return [question_from_day6(q) for q in items]


MIN_COUNTS = {("dev", True): 15, ("dev", False): 2, ("test", True): 5, ("test", False): 2}
NO_EVIDENCE_FIELDS = ("id", "split", "question", "answerable", "expected_behavior", "absence_reason")


def load_no_evidence(path: Path) -> list[dict[str, Any]]:
    items = json.loads(path.read_text(encoding="utf-8"))
    for q in items:
        missing = [k for k in NO_EVIDENCE_FIELDS if not q.get(k) and q.get(k) is not False]
        if missing or q["answerable"] is not False or q["expected_behavior"] != "search_and_abstain":
            raise ValueError(f"{path}: {q.get('id')} invalid (missing {missing})")
    return items


def build_cases(answerable: list[dict[str, Any]], no_evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """All benchmark questions without gold: what the agent runner and agent_metrics.py read."""
    cases = []
    for q in [*answerable, *no_evidence]:
        case = {k: q[k] for k in ("id", "split", "question", "answerable", "expected_behavior")}
        if q.get("filter"):
            case["filter"] = q["filter"]
        cases.append(case)
    ids = [c["id"] for c in cases]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate question IDs across answerable and no-evidence sets")
    return cases


def count_cases(cases: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    return {s: {"answerable": sum(c["split"] == s and c["answerable"] for c in cases),
                "no_evidence": sum(c["split"] == s and not c["answerable"] for c in cases)}
            for s in ("dev", "test")}


def _squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def check_gold(questions: list[dict[str, Any]], chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """For each gold evidence, report whether it sits inside one chunk of the right source/page.

    `exact` matches the starter's hit() definition (verbatim substring); `whitespace` means it
    only matches after collapsing whitespace, so the scorer needs normalization or an edit.
    """
    report = []
    for q in questions:
        for g in q.get("gold", []):
            same_page = [c for c in chunks if c["source_id"] == g["source_id"] and c["page"] == g["page"]]
            exact = [c["id"] for c in same_page if g["evidence"] in c["text"]]
            loose = [c["id"] for c in same_page if _squash(g["evidence"]) in _squash(c["text"])]
            status = "exact" if exact else "whitespace" if loose else "missing"
            report.append({"question_id": q["id"], "page": g["page"], "status": status,
                           "chunk_ids": exact or loose})
    return report


def align_gold(questions: list[dict[str, Any]], chunks: list[dict[str, Any]]) -> int:
    """Replace whitespace-only mismatches with the verbatim span from the chunk, in place.

    Day 6 quotes were checked against whitespace-normalized page text, while chunk text keeps
    PDF line breaks. The words are unchanged; only spacing is copied from the chunk so the
    starter's verbatim hit() works. The Day 6 wording is kept in `evidence_day6`.
    """
    changed = 0
    for q in questions:
        for g in q.get("gold", []):
            pattern = re.compile(r"\s+".join(map(re.escape, g["evidence"].split())))
            for c in chunks:
                if c["source_id"] != g["source_id"] or c["page"] != g["page"] or g["evidence"] in c["text"]:
                    continue
                m = pattern.search(c["text"])
                if m:
                    g["evidence_day6"], g["evidence"] = g["evidence"], m.group(0)
                    changed += 1
                    break
    return changed


def fetch_chunks(database_url: str, strategy: str) -> list[dict[str, Any]]:
    import psycopg

    sql = (f"SELECT {', '.join(CHUNK_COLUMNS)} FROM chunks WHERE strategy = %s "
           "ORDER BY page, chunk_index, chunk_id")
    with psycopg.connect(database_url, connect_timeout=5) as conn, \
            conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
        cur.execute(sql, (strategy,))
        rows = cur.fetchall()
    if not rows:
        raise RuntimeError(f"no chunks for strategy {strategy!r}; did the Day 6 ingestion run?")
    return [chunk_from_row(r, strategy) for r in rows]


def main() -> None:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--day6-dir", type=Path, required=True, help="path to the Day 6 repo")
    p.add_argument("--strategy", default="B", help="Day 6 index to export (default B, used by chosen config C)")
    p.add_argument("--no-evidence", type=Path, default=ROOT / "data" / "no_evidence_questions.json")
    p.add_argument("--output", type=Path, default=ROOT / "data" / "day6")
    args = p.parse_args()

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is not set; copy .env.example to .env")

    chunks = fetch_chunks(database_url, args.strategy)
    questions = load_day6_questions(args.day6_dir / "benchmark" / "questions.json")
    aligned = align_gold(questions, chunks)
    gold_report = check_gold(questions, chunks)
    models = sorted({c["metadata"]["embedding_model"] for c in chunks})
    no_evidence = load_no_evidence(args.no_evidence)
    cases = build_cases(questions, no_evidence)
    counts = count_cases(cases)
    short = [f"{s} {'answerable' if a else 'no_evidence'} {counts[s]['answerable' if a else 'no_evidence']}<{n}"
             for (s, a), n in MIN_COUNTS.items()
             if counts[s]["answerable" if a else "no_evidence"] < n]
    if short:
        raise SystemExit(f"benchmark below Day 7 minimum: {short}")
    day6_run = json.loads((args.day6_dir / "starter" / "results" / "run_config.json").read_text(encoding="utf-8"))

    args.output.mkdir(parents=True, exist_ok=True)
    manifest = {
        "exported_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "day6_repo": args.day6_dir.resolve().name,
        "day6_strategy": args.strategy,
        "day6_strategy_config": day6_run["strategies"][args.strategy],
        "embedding": day6_run["embedding"],
        "vector_store": day6_run["vector_store"],
        "day6_python": day6_run["python"],
        "embedding_models_in_index": models,
        "chunks": len(chunks),
        "benchmark": counts,
        "gold_whitespace_aligned": aligned,
        "gold_check": {s: sum(r["status"] == s for r in gold_report) for s in ("exact", "whitespace", "missing")},
        "gold_problems": [r for r in gold_report if r["status"] != "exact"],
        "license": "Chunk text: OpenStax Principles of Data Science, CC BY-NC-SA 4.0, openstax.org",
    }
    outputs = (("chunks.json", chunks), ("questions.json", questions), ("no_evidence.json", no_evidence),
               ("cases.json", cases), ("export_manifest.json", manifest))
    for name, data in outputs:
        (args.output / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"{len(chunks)} chunks (strategy {args.strategy}, model {', '.join(models)}) -> {args.output}")
    print(f"benchmark {len(cases)} cases: {counts}")
    print(f"gold check: {manifest['gold_check']} ({aligned} whitespace-aligned to chunk text)")
    for r in manifest["gold_problems"]:
        print(f"  {r['question_id']} page {r['page']}: {r['status']} {r['chunk_ids']}")


if __name__ == "__main__":
    main()
