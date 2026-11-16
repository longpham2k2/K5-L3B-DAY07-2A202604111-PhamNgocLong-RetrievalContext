"""Gold-side evaluation: retrieval and context metrics, plus the manual review sheet.

Runs only after the agent has finished; nothing here is passed to the agent or the retrievers.
Hit definition (same as starter/baseline.py): a chunk hits when its source_id and page match a
gold entry and the gold evidence is a verbatim substring of the chunk text.
"""
from __future__ import annotations

import statistics
from collections import Counter
from typing import Any


def hit(chunk: dict[str, Any], gold: list[dict[str, Any]]) -> bool:
    return any(chunk["source_id"] == g["source_id"] and chunk["page"] == g["page"] and g["evidence"] in chunk["text"]
               for g in gold)


def retrieval_metrics(retriever: Any, questions: list[dict[str, Any]], *, use_filter: bool, k: int = 3) -> dict[str, Any]:
    """Rank the ORIGINAL question once (no agent, no rewrite) and report Hit@1, Evidence Hit@k, MRR@k."""
    rows = []
    for q in questions:
        results = retriever.search(q["question"], filters=q.get("filter") if use_filter else None, top_k=k)
        ranks = [r["rank"] for r in results if hit(r, q["gold"])]
        first = min(ranks) if ranks else None
        rows.append({"query_id": q["id"], "first_gold_rank": first,
                     "results": [{"id": r["id"], "rank": r["rank"], "score": r["score"], "page": r["page"],
                                  "hit": hit(r, q["gold"])} for r in results]})
    n = len(rows)
    return {"N": n, "k": k, "query": "original question",
            "hit1": sum(r["first_gold_rank"] == 1 for r in rows),
            f"hit{k}": sum(r["first_gold_rank"] is not None for r in rows),
            f"mrr{k}": round(sum(1 / r["first_gold_rank"] for r in rows if r["first_gold_rank"]) / n, 4) if n else None,
            "per_query": rows}


def context_evidence(traces: list[dict[str, Any]], questions: list[dict[str, Any]],
                     chunks: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Share of answerable questions whose FINAL context (all passages shown to the model) holds gold evidence."""
    by_id = {t["query_id"]: t for t in traces}
    per = {}
    for q in questions:
        t = by_id.get(q["id"])
        ids = t.get("context_ids", []) if t else []
        per[q["id"]] = [i for i in ids if hit(chunks[i], q["gold"])]
    return {"n": sum(bool(v) for v in per.values()), "N": len(questions), "gold_chunks_in_context": per}


def run_summary(traces: list[dict[str, Any]], prices: dict[str, float] | None) -> dict[str, Any]:
    ok = [t for t in traces if t["status"] != "error"]
    tokens_in = sum(t["usage"]["input_tokens"] for t in traces)
    tokens_out = sum(t["usage"]["output_tokens"] for t in traces)
    cost = (round(tokens_in / 1e6 * prices["input"] + tokens_out / 1e6 * prices["output"], 6)
            if prices else None)
    lat = [t["latency_ms"] for t in ok]
    return {
        "cases": len(traces),
        "status": dict(Counter(t["status"] for t in traces)),
        "stop_reasons": dict(Counter(t.get("stop") for t in traces)),
        "errors": [{"query_id": t["query_id"], "error": t.get("error")} for t in traces if t["status"] == "error"],
        "tool_use": {"n": sum(t["n_searches"] > 0 for t in ok), "N": len(ok)},
        "searches_per_case": dict(sorted(Counter(t["n_searches"] for t in traces).items())),
        "model_calls_per_case": dict(sorted(Counter(t["n_model_calls"] for t in traces).items())),
        "avg_context_chars": round(statistics.mean(t["context_chars"] for t in traces), 1) if traces else None,
        "latency_ms": {"median": statistics.median(lat) if lat else None, "total": round(sum(lat), 1)},
        "tokens": {"input": tokens_in, "output": tokens_out},
        "provider_retries": dict(Counter(r["status"] for t in traces for ev in t["events"]
                                         if ev["event"] == "model" for r in ev.get("retries", []))),
        "cost_usd": cost,
        "cost_note": "from PRICE_INPUT_PER_MTOK / PRICE_OUTPUT_PER_MTOK" if prices else
                     "prices not set: cost = tokens x price on the run date",
    }


def review_template(traces: list[dict[str, Any]], cases: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """One blank label per non-error run, in the shape starter/agent_metrics.py expects."""
    out = []
    for t in traces:
        if t["status"] == "error":
            continue
        row: dict[str, Any] = {"query_id": t["query_id"], "status": t["status"],
                               "citation_support": [None] * len(t["citations"]), "reason": ""}
        if cases[t["query_id"]]["answerable"]:
            row["answer_grade"] = None
            row["context_grade"] = None
        else:
            row["abstention_correct"] = None
        out.append(row)
    return out


def review_markdown(traces: list[dict[str, Any]], cases: dict[str, dict[str, Any]],
                    gold: dict[str, dict[str, Any]], absent: dict[str, dict[str, Any]],
                    chunks: dict[str, dict[str, Any]], ctx: dict[str, Any]) -> str:
    """Human-readable sheet: question, agent answer, cited passages and gold side by side."""
    lines = ["# Review sheet", "",
             "Fill the labels in `reviews.json` (copy of `reviews_template.json`). Read each cited passage: "
             "a valid id is not proof of support.", "",
             "- `answer_grade`: 0 wrong/unsupported, 1 partly correct, 2 correct and complete (abstain = 0)",
             "- `citation_support`: one true/false per citation, in order",
             "- `context_grade`: 0 no evidence in context, 1 evidence but missing condition/source, 2 complete",
             "- `abstention_correct`: true only if it abstained and added no unsupported claims", ""]
    for t in traces:
        qid, case = t["query_id"], cases[t["query_id"]]
        lines += [f"## {qid} ({'answerable' if case['answerable'] else 'no evidence'}) — {t['status']}", "",
                  f"**Question:** {t['question']}", ""]
        if t.get("filter"):
            lines += [f"**Filter:** `{t['filter']}`", ""]
        searches = [e for e in t["events"] if e["event"] == "search"]
        for e in searches:
            lines.append(f"- search `{e['query']}` → " + ", ".join(
                f"{r['id'].split(':', 2)[-1]} ({r['score']})" for r in e["results"]))
        lines += ["", f"**Answer:** {t.get('answer')}"]
        if t.get("rejected_answer"):
            lines.append(f"**Rejected answer (invalid citations):** {t['rejected_answer']}")
        if t.get("abstain_reason"):
            lines.append(f"**Abstain reason:** {t['abstain_reason']}")
        if t.get("error"):
            lines.append(f"**Error:** {t['error']}")
        for cid in t["citations"]:
            lines += ["", f"> **[{cid}]** p{chunks[cid]['page']}: {chunks[cid]['text']}"]
        if qid in gold:
            g = gold[qid]
            lines += ["", f"**Expected:** {g['expected_answer']}",
                      f"**Gold evidence (p{g['gold'][0]['page']}):** {g['gold'][0]['evidence']}",
                      f"**Gold in final context:** {ctx['gold_chunks_in_context'].get(qid) or 'no'}"]
        elif qid in absent:
            lines += ["", f"**Absence reason:** {absent[qid]['absence_reason']}"]
        lines += ["", "---", ""]
    return "\n".join(lines)
