"""Run one agent configuration on one split and write traces, metrics and a review sheet.

    python -m src.run --config configs/dense.json --split dev
    python -m src.run --config configs/dense.json --split test --final   # only after choosing on dev

Output (results/<split>/<config name>/): traces.json, retrieval.json, summary.json,
reviews_template.json, review.md, config.json. The agent reads data/day6/cases.json only;
gold (questions.json) is loaded after all agent runs, for scoring.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from .agent import SYSTEM_PROMPT, run_agent
from .evaluate import context_evidence, retrieval_metrics, review_markdown, review_template, run_summary
from .lexical import BM25Retriever, HybridRetriever

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "day6"
REQUIRED = ("name", "retriever", "top_k", "max_searches", "budget_chars")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_retriever(cfg: dict[str, Any], chunks: list[dict[str, Any]]) -> Any:
    kind = cfg["retriever"]
    if kind == "bm25":
        return BM25Retriever(chunks, **cfg.get("bm25", {}))
    from .dense import DenseRetriever  # loads the embedding model and checks the pgvector index

    dense = DenseRetriever(strategy=cfg.get("day6_strategy", "B"))
    if kind == "dense":
        return dense
    if kind == "hybrid":
        return HybridRetriever(dense, BM25Retriever(chunks, **cfg.get("bm25", {})), **cfg.get("rrf", {}))
    raise ValueError(f"unknown retriever {kind!r}")


def prices_from_env() -> dict[str, float] | None:
    i, o = os.getenv("PRICE_INPUT_PER_MTOK"), os.getenv("PRICE_OUTPUT_PER_MTOK")
    return {"input": float(i), "output": float(o)} if i and o else None


def main() -> None:
    load_dotenv(ROOT / ".env")
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--split", choices=("dev", "test"), required=True)
    p.add_argument("--final", action="store_true", help="required for test: config was chosen on dev")
    p.add_argument("--ids", nargs="*", help="run only these case ids (debugging; not for reported results)")
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    if args.split == "test" and not args.final:
        raise SystemExit("test is held out: choose the config on dev first, then rerun with --final")

    cfg = load_json(args.config)
    missing = [k for k in REQUIRED if k not in cfg]
    if missing:
        raise SystemExit(f"config missing {missing}")
    out = args.output or ROOT / "results" / args.split / cfg["name"]
    out.mkdir(parents=True, exist_ok=True)

    from .providers import Provider

    chunk_list = load_json(DATA / "chunks.json")
    cases = [c for c in load_json(DATA / "cases.json") if c["split"] == args.split]
    if args.ids:
        cases = [c for c in cases if c["id"] in set(args.ids)]
    provider = Provider.from_env()
    retriever = build_retriever(cfg, chunk_list)

    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    traces = []
    for i, case in enumerate(cases, 1):
        agent_case = {k: case[k] for k in ("id", "split", "question") if k in case}
        if "filter" in case:
            agent_case["filter"] = case["filter"]
        t = run_agent(agent_case, provider, retriever, cfg)
        traces.append(t)
        print(f"[{i}/{len(cases)}] {t['query_id']}: {t['status']:8} searches={t['n_searches']} "
              f"calls={t['n_model_calls']} {t['latency_ms'] / 1000:.1f}s {t.get('error') or ''}")
    write_json(out / "traces.json", traces)

    # ---- gold-side scoring: only after every agent run is finished ----
    chunks = {c["id"]: c for c in chunk_list}
    ids = {c["id"] for c in cases}
    gold_qs = [q for q in load_json(DATA / "questions.json") if q["id"] in ids]
    absent = {q["id"]: q for q in load_json(DATA / "no_evidence.json") if q["id"] in ids}
    case_by_id = {c["id"]: c for c in cases}
    t0 = time.perf_counter()
    retrieval = retrieval_metrics(retriever, gold_qs, use_filter=cfg.get("use_filter", True), k=3)
    retrieval["latency_ms_total"] = round((time.perf_counter() - t0) * 1000, 1)
    ctx = context_evidence(traces, gold_qs, chunks)
    summary = {"config": cfg, "split": args.split, "started_utc": started, "model": provider.info(),
               "retriever": retriever.info(), "subset_ids": args.ids or None,
               "retrieval_original_query": {k: v for k, v in retrieval.items() if k != "per_query"},
               "context_evidence": {"n": ctx["n"], "N": ctx["N"]}, **run_summary(traces, prices_from_env())}
    write_json(out / "retrieval.json", retrieval)
    write_json(out / "summary.json", summary)
    write_json(out / "config.json", {**cfg, "system_prompt": SYSTEM_PROMPT})
    write_json(out / "reviews_template.json", review_template(traces, case_by_id))
    (out / "review.md").write_text(review_markdown(traces, case_by_id, {q["id"]: q for q in gold_qs}, absent,
                                                   chunks, ctx), encoding="utf-8")
    r = summary["retrieval_original_query"]
    print(f"\n{cfg['name']} / {args.split}: Hit@1 {r['hit1']}/{r['N']}  Hit@3 {r['hit3']}/{r['N']}  "
          f"Context evidence {ctx['n']}/{ctx['N']}  status {summary['status']}  "
          f"tokens {summary['tokens']}  median {summary['latency_ms']['median']} ms -> {out}")


if __name__ == "__main__":
    main()
