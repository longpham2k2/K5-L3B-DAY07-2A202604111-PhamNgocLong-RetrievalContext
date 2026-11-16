"""Offline checks for the Day 6 adapter mappings; no database or model needed."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.day6_adapter import (align_gold, build_cases, check_gold, chunk_from_row, count_cases,
                              question_from_day6)

ROW = {"chunk_id": "doc:B:p021:c02", "document_id": "doc", "source": "book.pdf", "page": 21,
       "printed_page": 11, "section": "1.1", "chunk_index": 2, "char_start": 10, "char_end": 90,
       "text": "data scientists spend about half\nof the entire process", "model": "m"}
Q = {"id": "d01", "split": "dev", "type": "direct", "question": "How much?",
     "expected_answer": "About half.", "gold_source_id": "doc", "gold_page": 21,
     "evidence_quote": "spend about half of the entire", "filter": None}


class AdapterTests(unittest.TestCase):
    def test_chunk_mapping_keeps_source_page_and_metadata(self):
        c = chunk_from_row(ROW, "B")
        self.assertEqual((c["id"], c["source_id"], c["page"]), ("doc:B:p021:c02", "doc", 21))
        self.assertEqual(c["metadata"]["section"], "1.1")
        self.assertEqual(c["metadata"]["day6_strategy"], "B")

    def test_question_mapping_builds_gold_and_keeps_filter_only_when_set(self):
        q = question_from_day6(Q)
        self.assertEqual(q["gold"], [{"source_id": "doc", "page": 21, "evidence": "spend about half of the entire"}])
        self.assertTrue(q["answerable"])
        self.assertNotIn("filter", q)
        self.assertEqual(question_from_day6({**Q, "filter": {"section": "1.3"}})["filter"], {"section": "1.3"})

    def test_gold_check_distinguishes_exact_whitespace_and_missing(self):
        chunks = [chunk_from_row(ROW, "B")]
        status = lambda ev, page=21: check_gold([question_from_day6({**Q, "evidence_quote": ev, "gold_page": page})], chunks)[0]["status"]
        self.assertEqual(status("spend about half"), "exact")
        self.assertEqual(status("spend about half of the entire"), "whitespace")
        self.assertEqual(status("spend about half", page=22), "missing")

    def test_align_gold_copies_chunk_whitespace_and_keeps_original(self):
        chunks = [chunk_from_row(ROW, "B")]
        qs = [question_from_day6(Q)]
        self.assertEqual(align_gold(qs, chunks), 1)
        g = qs[0]["gold"][0]
        self.assertEqual(g["evidence"], "spend about half\nof the entire")
        self.assertEqual(g["evidence_day6"], "spend about half of the entire")
        self.assertEqual(check_gold(qs, chunks)[0]["status"], "exact")

    def test_cases_carry_no_gold_and_reject_duplicate_ids(self):
        ne = {"id": "dn01", "split": "dev", "question": "Salary?", "answerable": False,
              "expected_behavior": "search_and_abstain", "absence_reason": "not in corpus"}
        cases = build_cases([question_from_day6({**Q, "filter": {"section": "1.1"}})], [ne])
        self.assertEqual([c["id"] for c in cases], ["d01", "dn01"])
        self.assertEqual(cases[0]["filter"], {"section": "1.1"})
        for c in cases:
            self.assertFalse({"gold", "expected_answer", "absence_reason"} & set(c))
        self.assertEqual(count_cases(cases)["dev"], {"answerable": 1, "no_evidence": 1})
        with self.assertRaises(ValueError):
            build_cases([question_from_day6(Q)], [{**ne, "id": "d01"}])


if __name__ == "__main__":
    unittest.main()
