"""Offline checks for the agent loop, BM25/hybrid retrievers and gold-side metrics.

The provider and retriever here are scripted fakes: they test control flow, not model quality.
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.agent import run_agent
from src.evaluate import context_evidence, hit, retrieval_metrics, review_template
from src.lexical import BM25Retriever, HybridRetriever

CHUNKS = [
    {"id": "doc:B:p021:c00", "source_id": "doc", "source": "book.pdf", "page": 21,
     "text": "Data scientists spend about half of the process on data collection and cleaning.",
     "metadata": {"section": "1.1"}},
    {"id": "doc:B:p037:c01", "source_id": "doc", "source": "book.pdf", "page": 37,
     "text": "The Iris dataset has 150 flowers with sepal and petal measurements.",
     "metadata": {"section": "1.3"}},
    {"id": "doc:B:p040:c00", "source_id": "doc", "source": "book.pdf", "page": 40,
     "text": "Tableau and PowerBI are tools for data visualization dashboards.",
     "metadata": {"section": "1.4"}},
]
CFG = {"name": "t", "top_k": 2, "max_searches": 2, "budget_chars": 1000, "use_filter": True}


class FakeProvider:
    def __init__(self, turns, fail_at=None):
        self.turns, self.fail_at, self.seen = list(turns), fail_at, []

    def info(self):
        return {"provider": "fake", "model": "scripted", "temperature": 0}

    def complete(self, messages, schemas):
        self.seen.append([dict(m) for m in messages])
        if self.fail_at is not None and len(self.seen) == self.fail_at:
            raise RuntimeError("provider returned HTTP 503")
        calls = self.turns.pop(0)
        msg = {"role": "assistant", "content": None if calls else "plain text",
               "tool_calls": [{"id": f"c{i}", "type": "function",
                               "function": {"name": n, "arguments": json.dumps(a)}} for i, (n, a) in enumerate(calls)]}
        return {"message": msg, "calls": [{"id": f"c{i}", "name": n, "arguments": json.dumps(a)}
                                          for i, (n, a) in enumerate(calls)],
                "finish": "tool_calls" if calls else "stop", "usage": {"input_tokens": 10, "output_tokens": 2},
                "latency_ms": 1.0}


def case(qid="d01", question="How long is cleaning?", **kw):
    return {"id": qid, "split": "dev", "question": question, **kw}


class AgentLoopTests(unittest.TestCase):
    def setUp(self):
        self.bm25 = BM25Retriever(CHUNKS)

    def test_search_then_cited_answer_records_trace(self):
        p = FakeProvider([[("search_chapter", {"query": "data collection cleaning"})],
                          [("final_answer", {"answer": "About half [doc:B:p021:c00].", "citations": ["doc:B:p021:c00"]})]])
        t = run_agent(case(), p, self.bm25, CFG)
        self.assertEqual((t["status"], t["citations"], t["stop"]), ("answered", ["doc:B:p021:c00"], "final_answer"))
        self.assertEqual(t["n_searches"], 1)
        self.assertEqual(t["n_model_calls"], 2)
        self.assertIn("doc:B:p021:c00", t["context_ids"])
        self.assertEqual(t["usage"], {"input_tokens": 20, "output_tokens": 4})
        search = next(e for e in t["events"] if e["event"] == "search")
        self.assertEqual(search["results"][0]["rank"], 1)
        # the tool result passed back to the model carries passage ids and text
        tool_msg = next(m for m in p.seen[1] if m["role"] == "tool")
        self.assertIn("doc:B:p021:c00", tool_msg["content"])

    def test_citation_not_in_context_is_rejected(self):
        p = FakeProvider([[("search_chapter", {"query": "iris"})],
                          [("final_answer", {"answer": "x [doc:B:p040:c00]", "citations": ["doc:B:p040:c00"]})]])
        t = run_agent(case(), p, self.bm25, {**CFG, "top_k": 1})
        self.assertEqual((t["status"], t["stop"], t["citations"]), ("abstain", "invalid_citations", []))
        self.assertEqual(t["rejected_answer"], "x [doc:B:p040:c00]")

    def test_inline_citations_used_when_list_missing(self):
        p = FakeProvider([[("search_chapter", {"query": "iris dataset"})],
                          [("final_answer", {"answer": "150 flowers [doc:B:p037:c01].", "citations": []})]])
        t = run_agent(case(), p, self.bm25, CFG)
        self.assertEqual((t["status"], t["citations"]), ("answered", ["doc:B:p037:c01"]))

    def test_abstain_and_search_limit(self):
        p = FakeProvider([[("search_chapter", {"query": "salary"})], [("search_chapter", {"query": "wage"})],
                          [("search_chapter", {"query": "pay"})], [("abstain", {"reason": "not in chapter"})]])
        t = run_agent(case(), p, self.bm25, CFG)
        self.assertEqual((t["status"], t["abstain_reason"]), ("abstain", "not in chapter"))
        self.assertEqual(t["n_searches"], 2)
        self.assertTrue(any(e["event"] == "search_limit" for e in t["events"]))

    def test_provider_error_is_reported_not_hidden(self):
        p = FakeProvider([[("search_chapter", {"query": "iris"})]], fail_at=2)
        t = run_agent(case(), p, self.bm25, CFG)
        self.assertEqual(t["status"], "error")
        self.assertIn("503", t["error"])
        self.assertEqual(t["n_searches"], 1)

    def test_no_tool_call_nudges_once_then_abstains(self):
        t = run_agent(case(), FakeProvider([[], []]), self.bm25, CFG)
        self.assertEqual((t["status"], t["stop"]), ("abstain", "no_final_tool"))

    def test_budget_drops_passages_and_filter_is_applied(self):
        p = FakeProvider([[("search_chapter", {"query": "data flowers"})], [("abstain", {"reason": "-"})]])
        t = run_agent(case(filter={"section": "1.3"}), p, self.bm25, {**CFG, "budget_chars": 1000})
        search = next(e for e in t["events"] if e["event"] == "search")
        self.assertEqual({r["section"] for r in search["results"]}, {"1.3"})
        self.assertEqual(search["filter"], {"section": "1.3"})
        p = FakeProvider([[("search_chapter", {"query": "data"})], [("abstain", {"reason": "-"})]])
        t = run_agent(case(), p, self.bm25, {**CFG, "budget_chars": 90})
        search = next(e for e in t["events"] if e["event"] == "search")
        self.assertEqual(len(search["added_to_context"]), 1)
        self.assertEqual(len(search["dropped_for_budget"]), 1)
        self.assertLessEqual(t["context_chars"], 90)

    def test_first_search_original_runs_before_model_and_counts_toward_limit(self):
        cfg = {**CFG, "first_search": "original", "max_searches": 2}
        p = FakeProvider([[("search_chapter", {"query": "data"})], [("search_chapter", {"query": "more"})],
                          [("final_answer", {"answer": "About half [doc:B:p021:c00].", "citations": ["doc:B:p021:c00"]})]])
        t = run_agent(case(question="How long is data collection and cleaning?"), p, self.bm25, cfg)
        searches = [e for e in t["events"] if e["event"] == "search"]
        self.assertEqual([(e["by"], e["query"]) for e in searches],
                         [("system", "How long is data collection and cleaning?"), ("model", "data")])
        self.assertEqual((t["n_searches"], t["n_model_searches"]), (2, 1))
        self.assertTrue(any(e["event"] == "search_limit" for e in t["events"]))  # 3rd search refused
        first_user = p.seen[0][1]["content"]
        self.assertIn("doc:B:p021:c00", first_user)             # initial passages shown up front
        self.assertIn("1 more time", first_user)
        self.assertEqual(t["status"], "answered")

    def test_agent_never_receives_gold_fields(self):
        p = FakeProvider([[("abstain", {"reason": "-"})]])
        run_agent(case(), p, self.bm25, CFG)
        sent = json.dumps(p.seen)
        for word in ("gold", "expected_answer", "evidence"):
            self.assertNotIn(word, sent)


class RetrieverAndMetricTests(unittest.TestCase):
    def test_bm25_ranks_lexical_match_first_and_filters(self):
        r = BM25Retriever(CHUNKS)
        self.assertEqual(r.search("iris sepal", top_k=3)[0]["id"], "doc:B:p037:c01")
        self.assertEqual([c["id"] for c in r.search("data", filters={"section": "1.4"})], ["doc:B:p040:c00"])
        with self.assertRaises(ValueError):
            r.search("data", filters={"year": 2020})

    def test_hybrid_rrf_rewards_agreement(self):
        class Fixed:
            def __init__(self, order): self.order = order
            def info(self): return {}
            def search(self, q, *, filters=None, top_k=3):
                by = {c["id"]: c for c in CHUNKS}
                return [{**by[i], "rank": n, "score": 1.0} for n, i in enumerate(self.order[:top_k], 1)]
        a, b, c = (x["id"] for x in CHUNKS)
        res = HybridRetriever(Fixed([a, b, c]), Fixed([b, c, a]), k=60).search("q", top_k=3)
        self.assertEqual(res[0]["id"], b)  # ranks 2 + 1 beat 1 + 3
        self.assertEqual(res[0]["metadata"]["component_ranks"], {"dense": 2, "bm25": 1})

    def test_metrics_use_verbatim_evidence_on_gold_page(self):
        gold = [{"source_id": "doc", "page": 37, "evidence": "150 flowers"}]
        self.assertTrue(hit(CHUNKS[1], gold))
        self.assertFalse(hit({**CHUNKS[1], "page": 38}, gold))
        qs = [{"id": "d01", "question": "iris sepal", "gold": gold}]
        m = retrieval_metrics(BM25Retriever(CHUNKS), qs, use_filter=False)
        self.assertEqual((m["hit1"], m["hit3"], m["N"]), (1, 1, 1))
        ctx = context_evidence([{"query_id": "d01", "context_ids": ["doc:B:p037:c01"]}], qs,
                               {c["id"]: c for c in CHUNKS})
        self.assertEqual((ctx["n"], ctx["N"]), (1, 1))

    def test_review_template_matches_agent_metrics_shape(self):
        traces = [{"query_id": "d01", "status": "answered", "citations": ["x", "y"]},
                  {"query_id": "dn01", "status": "abstain", "citations": []},
                  {"query_id": "d02", "status": "error", "citations": []}]
        cases = {"d01": {"answerable": True}, "dn01": {"answerable": False}, "d02": {"answerable": True}}
        rows = review_template(traces, cases)
        self.assertEqual([r["query_id"] for r in rows], ["d01", "dn01"])
        self.assertEqual(rows[0]["citation_support"], [None, None])
        self.assertIn("answer_grade", rows[0])
        self.assertIn("abstention_correct", rows[1])


if __name__ == "__main__":
    unittest.main()
