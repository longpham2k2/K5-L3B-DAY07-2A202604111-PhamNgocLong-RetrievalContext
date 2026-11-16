# Code

## Reusing Day 6

| File | Purpose |
|---|---|
| `day6/` | `store.py`, `embeddings.py`, `models.py` copied unchanged from the Day 6 repo (commit `4c17382`), so query embeddings and search match the Day 6 index |
| `day6_adapter.py` | Exports Day 6 chunks (from pgvector) and benchmark questions to the Day 7 JSON format in `data/day6/` |
| `dense.py` | `DenseRetriever`: the starter `Retriever` protocol over the Day 6 pgvector index |

**Index reused:** Day 6 strategy **B** (paragraph chunks, max 900 characters, 135 chunks). It was chosen in Day 6 as config C = B + `section` filter. Embedding model: `sentence-transformers/all-MiniLM-L6-v2`, 384 dimensions, normalized, no query prefix. Search: PostgreSQL + pgvector, exact cosine. `DenseRetriever` refuses to start if the stored vectors were made by a different model.

### Setup

```bash
pip install -r requirements.txt
cp .env.example .env          # set DATABASE_URL to the Day 6 database
python -m src.day6_adapter --day6-dir ../K5-L3B-DAY06-PhamNgocLong-2A202604111-DataIngestion
```

The Day 6 database must already be populated. To rebuild it, run the Day 6 ingestion with the same PDF and check its sha256 against the Day 6 `data/manifest.json`.

Output in `data/day6/`:
- `chunks.json`: the 135 chunks with `id`, `text`, `source_id`, `source`, `page` and `metadata` (`section`, `printed_page`, offsets)
- `questions.json`: 15 dev + 5 test answerable questions, with `gold` and an optional `filter`. This is the input for retrieval metrics (`baseline.py`).
- `no_evidence.json`: copy of [data/no_evidence_questions.json](../data/no_evidence_questions.json)
- `cases.json`: all 24 questions with **no gold**: `id`, `split`, `question`, `answerable`, `expected_behavior` and an optional `filter`. This is the input for the agent runner and `agent_metrics.py --cases`.
- `export_manifest.json`: embedding model, versions and dimensions, the vector store, the Day 6 chunking config, benchmark counts and the gold check

The adapter stops if the benchmark is below the Day 7 minimum (dev 15+2, test 5+2).

### Benchmark

| Split | Answerable (Day 6) | No evidence (Day 7) | Total |
|---|---:|---:|---:|
| dev | 15 (d01–d15) | 2 (dn01, dn02) | 17 |
| test | 5 (t01–t05) | 2 (tn01, tn02) | 7 |

The answerable questions come unchanged from Day 6. That test set was evaluated only after the Day 6 configuration was locked, so it was not used for tuning.

The no-evidence questions are hand-written and sit close to real content: the Anaconda survey (p21), the BLS source (p32), Tableau/PowerBI (p40) and the movie-gross scatterplot (p58). Each records `absence_reason` and `verification`, the search run over the text of every corpus page (PDF 19–63). Absence was checked on the full text, not on top-k results.

### Gold evidence alignment

Day 6 evidence quotes were checked against whitespace-normalized page text, but chunk text keeps the PDF line breaks. For 15 of the 20 questions, the adapter replaces the quote with the verbatim span from the gold chunk. Only whitespace changes; the original is kept in `gold[].evidence_day6`. This lets the starter's exact-substring `hit()` work. All 20 gold quotes then match a chunk on the gold page.

### Filters

`DenseRetriever.search(query, filters=..., top_k=...)` accepts `section`, `page` and `source_id`. Only pass the `filter` set in a question beforehand (the reader's section, as in Day 6); never derive it from the gold answer.
