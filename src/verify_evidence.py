"""Trace every gold evidence to source -> PDF page -> exactly one chunk, and check it in the PDF.

    python -m src.verify_evidence --pdf ../K5-L3B-DAY06-PhamNgocLong-2A202604111-DataIngestion/data/raw/Principles-of-Data-Science-WEB.pdf

Writes data/day6/evidence_map.json. Exits non-zero if any evidence is not traceable.
This reads gold, so it is an evaluation tool only; never import it from the agent.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "day6"


def squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def trace(questions: list[dict], chunks: list[dict], page_text: dict[int, str]) -> list[dict]:
    rows = []
    for q in questions:
        for g in q["gold"]:
            ids = [c["id"] for c in chunks if c["source_id"] == g["source_id"]
                   and c["page"] == g["page"] and g["evidence"] in c["text"]]
            meta = next(c["metadata"] for c in chunks if c["id"] == ids[0]) if ids else {}
            pdf = squash(page_text.get(g["page"], ""))
            ev = squash(g["evidence"])
            rows.append({"question_id": q["id"], "split": q["split"], "source_id": g["source_id"],
                         "pdf_page": g["page"], "printed_page": meta.get("printed_page"),
                         "section": meta.get("section"), "chunk_ids": ids,
                         # Line-end hyphens: "data- driven" may be "data-driven" or "datadriven".
                         "evidence_in_pdf_page": any(ev in v for v in (pdf, pdf.replace("- ", "-"),
                                                                       pdf.replace("- ", "")))})
    return rows


def main() -> None:
    from pypdf import PdfReader

    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--pdf", type=Path, required=True)
    args = p.parse_args()
    chunks = json.loads((DATA / "chunks.json").read_text(encoding="utf-8"))
    questions = json.loads((DATA / "questions.json").read_text(encoding="utf-8"))
    reader = PdfReader(args.pdf)
    pages = {g["page"] for q in questions for g in q["gold"]}
    rows = trace(questions, chunks, {n: reader.pages[n - 1].extract_text() for n in pages})
    (DATA / "evidence_map.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for r in rows:
        print(f"{r['question_id']:4} {r['split']:4} PDF p{r['pdf_page']} (printed {r['printed_page']}) "
              f"sec {r['section']:5} {','.join(r['chunk_ids']) or '-'}  in_pdf={r['evidence_in_pdf_page']}")
    ok = all(len(r["chunk_ids"]) == 1 and r["evidence_in_pdf_page"] for r in rows)
    print(f"{sum(len(r['chunk_ids']) == 1 for r in rows)}/{len(rows)} map to exactly one chunk; "
          f"{sum(r['evidence_in_pdf_page'] for r in rows)}/{len(rows)} found in the original PDF page")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
