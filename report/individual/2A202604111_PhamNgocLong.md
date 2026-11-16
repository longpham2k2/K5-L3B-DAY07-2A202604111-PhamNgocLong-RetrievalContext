# Báo cáo Day 7

## Dữ liệu và benchmark

- Nguồn, quyền sử dụng, số trang và số chunk: Chương 1 "What Are Data and Data Science?" của giáo trình "Principles of Data Science", gồm 5 mục 1.1–1.5. Nguồn: https://openstax.org/details/books/principles-data-science. Giấy phép CC BY-NC-SA 4.0 (trang 4 PDF), cho phép dùng phi thương mại có ghi nguồn. Sử dụng 45 trang nội dung từ 19-63 (trang in 9-53), bỏ qua 1-18 (bìa, bản quyền, mục lục, lời nói đầu) và 64-66 (câu hỏi ôn tập không có đáp án và tài liệu tham khảo). Đơn vị đếm là số trang do trình xem PDF hiển thị, số in trên sách = trang PDF − 10 và được lưu riêng ở trường `printed_page`. Tái sử dụng day 6, đã chọn strategy C nên có số chunk = 135.
- Vector store, embedding model, phiên bản và số chiều: Vector được lưu trên PostgreSQL 17.11 có extension pgvector 0.8.7. Sử dụng model MiniLM-L6-v2 do sách viết bằng tiếng Anh, chạy local, lưu 384 chiều, sử dụng sentence-transformers 6.3.0. 
- Agent model, cách chạy và phân chia dev/test:
    - Agent model: gemini-3.5-flash-lite gọi qua endpoint tương thích của Google, với providers.py port từ lab trước (DAY04). Đặt temperature = 0 để kết quả lặp lại được. Đã kiểm tra model hỗ trợ tool-calling với câu "What is the Iris dataset?", model gọi search với {"query": "Iris dataset"}, khoảng 0,6 s/lượt. Mỗi lượt gọi ghi lại input_tokens/output_tokens và latency_ms để tính thời gian và chi phí theo bảng giá Gemini ở ngày chạy. Lỗi HTTP 429/5xx được thử lại với backoff (5–40 s); nếu vẫn lỗi, câu đó ghi status: "error" và báo riêng, không thay bằng kết quả giả. Embedding cho truy vấn vẫn sử dụng all-MiniLM-L6-v2 từ Day 6.
    - Cách chạy: Python 3.15.2, python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt. Chép .env.example thành .env, điền DATABASE_URL của PostgreSQL/pgvector Day 6 và GEMINI_API_KEY. Sau đó:
        - python -m src.day6_adapter --day6-dir <repo Day 6>: xuất chunk và câu hỏi ra data/day6/.
        - python -m src.verify_evidence --pdf <PDF>: kiểm tra 20/20 evidence truy được về đúng một chunk và có trong trang PDF gốc.
        - python -m unittest discover -s tests -v: test offline.
        - python -m src.run --config configs/<name>.json --split dev
        - python -m src.run --config configs/<cấu hình đã chọn>.json --split test --final: chỉ chạy sau khi chốt cấu hình trên dev.
    - Phân chia dev/test: 24 câu. Dev 17 câu = 15 có đáp án (d01–d15) + 2 thiếu evidence (dn01, dn02). Test 7 câu = 5 có đáp án (t01–t05) + 2 thiếu evidence (tn01, tn02). 20 câu có đáp án giữ nguyên split của Day 6, cố định trước lần truy xuất đầu tiên. Gold page của test (26, 34, 40, 43, 54) không trùng trang nào của dev. 4 câu thiếu evidence viết mới cho Day 7. Agent chỉ đọc data/day6/cases.json (id, câu hỏi, filter section có sẵn ở 4 câu d13–d15, t05), không có gold hay đáp án. Mọi lựa chọn phương pháp và cấu hình chỉ dựa trên dev theo tiêu chí công bố trước; test chạy một lần cho baseline và cấu hình đã chốt. Day 6 đã chạy test dense (C) cùng lúc với dev, nhưng việc chọn C dựa trên dev; điều này được ghi rõ như một giới hạn.
- Cách xác định câu có/thiếu evidence và tiêu chí chấm:
    - 20 câu có đáp án lấy từ Day 6 (15 dev d01–d15, 5 test t01–t05). Split cố định từ Day 6; test không dùng để chỉnh (xem giới hạn ở dưới).
    - Evidence nằm nguyên văn trong một chunk đúng trang. 15 câu chỉ được căn lại khoảng trắng theo chunk; bản gốc giữ ở evidence_day6.
    - 4 câu thiếu evidence (dn01, dn02, tn01, tn02) gần chủ đề của p21/p32/p40/p58. Đã kiểm tra bằng tìm kiếm trên toàn văn 45 trang, không chỉ top-k.
    - Chấm theo BENCHMARK.md: answer 0/1/2, citation phải có trong context và hỗ trợ câu trả lời, câu thiếu evidence đạt khi từ chối và không đưa ra con số.
    - Test (t01–t05) giữ nguyên từ Day 6, cố định trước lần truy xuất đầu tiên. Day 6 đã chạy test cùng lúc với dev và báo kết quả dense (C) trên test, nhưng việc chọn C dựa trên dev theo tiêu chí công bố trước. Ở Day 7 mọi lựa chọn phương pháp/cấu hình chỉ dựa trên dev; test chạy một lần sau khi chốt. 4 câu thiếu evidence (dn01, dn02, tn01, tn02) mới viết cho Day 7.
- Cách kết nối: Kết nối trực tiếp vào bảng chunks (strategy B, do C tái sử dụng của B) trong PostgreSQL của Day 6 qua DATABASE_URL trong .env. src/day6/ chép nguyên store.py/embeddings.py từ Day 6 để query embedding giống hệt lúc index; DenseRetriever kiểm tra model trong bảng trùng với model truy vấn, sai thì dừng. python -m src.day6_adapter xuất chunk và câu hỏi sang data/day6/, ghi phiên bản vào export_manifest.json.
- Tiêu chí chọn cấu hình (trước khi chạy dev):
    - Loại cấu hình khẳng định thông tin ở câu thiếu evidence của dev (dn01, dn02) hoặc còn lỗi hệ thống.
    - Xếp theo grounded answer trung bình /2 trên 15 câu dev có đáp án.
    - Nếu bằng, xét lần lượt Context Evidence Rate → Evidence Hit@3 → tỷ lệ citation hợp lệ → số câu có đáp án bị từ chối nhầm.
    - Cuối cùng là thời gian trung vị/câu và chi phí token.
    - Chênh lệch ≤ 1 câu (≤ 6,7%) coi là bằng nhau và chọn cấu hình đơn giản/rẻ hơn, vì dev chỉ có 15 câu. Test chỉ chạy một lần cho baseline và cấu hình đã chọn, sau khi chốt.

## Retrieval và thử nghiệm

| Cấu hình | Phương pháp, top-k, filter, rerank, context budget | Giả thuyết / thay đổi | Split | Hit@1 | Evidence Hit@3 | Context Evidence Rate | Thời gian / chi phí |
|---|---|---|---|---|---|---|---|
| Baseline: Dense | Dense: all-MiniLM-L6-v2 (384 chiều) + pgvector cosine exact, index B Day 6 (135 chunk); top-k 3; filter `section` (chỉ 4 câu có sẵn); không rerank; budget 4.000 ký tự, tối đa 3 lượt search | Baseline = cấu hình C đã chọn ở Day 6; agent Gemini tự viết query | dev | 14/15 (93%) | 15/15 (100%) | 13/15 (87%) | median 8.6 s/câu; 43.9k in + 2.5k out token/17 câu; 2 lần 429 |
| Phương pháp 2: BM25 | Sparse/lexical: Okapi BM25 (k1=1.5, b=0.75, tách từ `\w+`), cùng 135 chunk; top-k 3; filter `section`; không rerank; budget 4.000 ký tự | Query agent viết lại thường là từ khóa (vd "Anaconda 2020 survey") nên khớp từ chính xác có thể tốt hơn dense | dev | 13/15 (87%) | 14/15 (93%) | 15/15 (100%) | median 6.6 s/câu; 43.1k in + 2.5k out; 1 lần 429 |
| Phương pháp 3: Hybrid RRF | Dense + BM25 hợp nhất bằng Reciprocal Rank Fusion (k=60, 20 candidate mỗi bên); top-k 3; filter `section`; budget 4.000 ký tự | Kết hợp ngữ nghĩa và từ khóa để bù lỗi cho nhau; RRF dùng rank nên không cần chuẩn hóa score giữa cosine và BM25 | dev | 13/15 (87%) | 14/15 (93%) | 15/15 (100%) | median 9.4 s/câu; 46.8k in + 2.8k out; 3 lần 429 |
| Cải thiện 1: Dense + search câu gốc trước | Như Baseline Dense + `first_search=original`: hệ thống tìm bằng câu hỏi gốc trước, tính vào giới hạn 3 search | Lỗi d01, d11: câu gốc có gold hạng 1/3 nhưng agent chỉ tìm bằng query tự viết nên mất evidence → tìm câu gốc trước sẽ đưa evidence vào context | dev | 14/15 (93%) | 15/15 (100%) | 15/15 (100%) | median 2.1 s/câu; 28.5k in + 1.7k out (−35%); 1.41 lượt gọi model/câu; 3 lần 429 |
| Cải thiện 2: BM25 + search câu gốc trước | Như BM25 + `first_search=original` | BM25 đã 15/15; đưa sẵn kết quả của câu gốc giúp model trả lời ít lượt gọi hơn, giảm token/thời gian mà giữ chất lượng | dev | 13/15 (87%) | 14/15 (93%) | 15/15 (100%) | median 1.6 s/câu; 27.1k in + 1.8k out (−37%); 1.35 lượt gọi/câu; 3 lần 429 |
| Cấu hình đã chọn | | | test | | | | |
| Baseline | | | test | | | | |

Hit@1 và Evidence Hit@3 đo trên câu hỏi gốc, mỗi phương pháp xếp hạng một lần (không qua agent). Context Evidence Rate đo trên context cuối agent gửi cho model, gồm mọi lượt search với query do agent tự viết, nên có thể cao hơn Hit@3 (BM25: 14/15 → 15/15, agent tìm lại được d02 ở lượt 2) hoặc thấp hơn (Dense: 15/15 → 13/15, query viết lại làm mất evidence ở d01, d11). Thời gian là median mỗi câu trên 17 câu dev, chủ yếu là thời gian gọi Gemini; chênh lệch vài giây chịu ảnh hưởng của các lần HTTP 429.

Một cấu hình có thể đồng thời là phương pháp mới và cải thiện; giải thích rõ. Báo `n/N` và tỷ lệ, ghi đơn vị thời gian/chi phí, so sánh test sau khi chốt. Nêu hai lỗi dev, nguyên nhân, cách thử và lý do chọn cấu hình:
- Lỗi dev 1 – d01 (Dense): câu hỏi gốc xếp chunk gold p021:c00 ở hạng 1, nhưng agent tìm bằng query viết lại ("Anaconda 2020 survey data collection and cleaning", rồi "Anaconda 2020", "Anaconda"), dense không trả về chunk gold nên agent từ chối nhầm (answer 0).
- Lỗi dev 2 – d11 (Dense): cùng nguyên nhân; câu gốc có gold p045:c00 ở hạng 3, nhưng hai query viết lại không lấy được, agent trả lời một phần từ p043:c00 (thiếu "Run before", answer 1).
- Giả thuyết cải thiện: luôn dùng câu hỏi gốc cho lượt search đầu → Context Evidence của Dense lên 15/15.
- Sau cải thiện:
    - Dense + search gốc đã sửa được 2 lỗi dev trước đó. Trong đó d01 thay đổi từ từ chối sai (0) thành đúng (2), và d11 thay đổi từ đúng một phần (1) thành đúng (2). Các gold chunk cũng được trả về từ lượt search đầu tiên.
    - BM25 + search gốc giữ nguyên chất lượng 15/15 nhưng đã giảm được số lần gọi model xuống 1 nửa, input token xuống 37% và median thời gian giảm từ 6.6s còn 1.6s. Trong đó, 13/17 câu được trả lời ngay từ lượt search đầu.
- Áp dụng tiêu chí chọn cấu hình: 
    - Trả về abstention cho 2 câu thiếu evidence: cả 5 cấu hình đều đạt, 2/2 và 0 lỗi.
    - Xếp theo grounded answer /2 cho 15 câu dev có đáp án: dense được 1.80 (13 câu đạt 2) trong khi các cấu hình khác được 2.00 (15 câu); chênh 2 câu > ngưỡng 1 câu nên dense bị loại ở bước này.
    - Sắp xếp theo các chỉ số:
        - Context Evidence: Cả 4 đạt 15/15.
        - Hit@3: dense + search gốc đạt 15/15 trong khi các cấu hình còn lại (không tính dense do đã bị loại) đều đạt 14/15.
        - Tỷ lệ Citations: Cả 4 đạt 100%. 
        - Từ chối nhầm: Không cấu hình nào từ chối nhầm.
    - Thời gian/chi phí: BM25 + search gốc dùng ít token nhất (27.1k so với 28.5k) và có median thấp nhất (1.6 s so với 2.1 s), nhưng chênh lệch nhỏ và cả hai đều có 3 lần HTTP 429, nên gần như bằng nhau.
- Kết quả: chọn BM25 + search gốc. Dense + search gốc hơn 1 câu ở Hit@1/Hit@3 (d02), nhưng chênh ≤ 1 câu được coi là bằng nhau; khi bằng nhau, chọn cấu hình đơn giản hơn: BM25 không cần embedding model và vector store. Rủi ro: câu diễn đạt lại không trùng từ (như d02) cần thêm lượt search.

## Agent và đánh giá

- Tool, số lượt gọi, điều kiện dừng, cách chọn context và xử lý lỗi:
    - 3 tool: `search_chapter(query)` (retriever theo cấu hình, top-k 3, filter `section` do hệ thống áp từ câu hỏi, model không tự chọn), `final_answer(answer, citations)`, `abstain(reason)`.
    - Tối đa 3 lượt search/câu (với `first_search=original`, lượt search câu gốc do hệ thống chạy cũng tính vào 3) và tối đa 6 lượt gọi model. Dừng khi gọi `final_answer`/`abstain`, hết lượt search hoặc hết lượt gọi. Nếu model trả lời bằng text không gọi tool thì nhắc 1 lần, lần 2 tính là abstain.
    - Context: mỗi lượt search thêm đoạn mới vào context đến khi đủ 4.000 ký tự; đoạn đã có không lặp lại, đoạn bị bỏ do budget được ghi trong trace.
    - Citation: `final_answer` chỉ được chấp nhận nếu mọi citation là đoạn model đã thấy; nếu không, ghi `abstain`/`invalid_citations` và giữ câu trả lời bị loại trong trace (dev: 0 lần).
    - Lỗi: HTTP 429/5xx thử lại có backoff và ghi `retries`; lỗi còn lại ghi `status: "error"`, không thay bằng kết quả giả. Đã thử key sai, provider không kết nối được và Postgres không truy cập được. Dev: 0 lỗi trên 85 lượt chạy; 12 lần 429 được thử lại thành công.

| Cấu hình / split | Tool use | Số lượt gọi | Grounded answer 0/1/2 và trung bình | Citation hợp lệ | Câu có citation | Abstention đúng | Từ chối nhầm |
|---|---|---|---|---|---|---|---|
| Dense / dev | 17/17 | search 1/2/3 lượt: 12/2/3 câu; gọi model TB 2.82 (6 lần phải nhắc gọi tool) | 1/1/13 → 1.80 | 15/16 | 14/14 | 2/2 | 1/15 (d01) |
| BM25 / dev | 17/17 | search 14/1/2; gọi model TB 2.76 (8 lần nhắc) | 0/0/15 → 2.00 | 16/16 | 15/15 | 2/2 | 0/15 |
| Hybrid RRF / dev | 17/17 | search 14/1/2; gọi model TB 2.94 (11 lần nhắc) | 0/0/15 → 2.00 | 18/18 | 15/15 | 2/2 | 0/15 |
| Dense + câu gốc / dev | 17/17 | search 13/2/3 (gồm lượt hệ thống); gọi model TB 1.41; model tự search TB 0.35 (0 lần nhắc) | 0/0/15 → 2.00 | 16/16 | 15/15 | 2/2 | 0/15 |
| BM25 + câu gốc (đã chọn) / dev | 17/17 | search 13/2/2; gọi model TB 1.35; model tự search TB 0.35 (0 lần nhắc) | 0/0/15 → 2.00 | 17/17 | 15/15 | 2/2 | 0/15 |
| BM25 + câu gốc (đã chọn) / test | | | | | | | |
| Dense (baseline) / test | | | | | | | |

| Query ID | Loại câu | Tool call và kết quả | Câu trả lời và citation | Nhãn, lý do |
|---|---|---|---|---|
| d01 (Dense) | direct | 3 search viết lại ("Anaconda 2020 survey data collection and cleaning", "Anaconda 2020", "Anaconda"), không lấy được p021:c00 | Từ chối | 0 – từ chối nhầm; câu gốc có gold ở hạng 1 nhưng agent không tìm bằng câu gốc |
| d01 (Dense + câu gốc) | direct | Search câu gốc của hệ thống → p021:c00 hạng 1; model không search thêm | "about half of the entire process" [p021:c00] | 2 – đã sửa lỗi d01 |
| d11 (Dense) | condition | 2 search viết lại, không lấy được p045:c00 | "Run all" [p043:c00] | 1 – thiếu "Run before"; p043:c00 không nói phải dùng sau khi sửa cell |
| d02 (BM25 + câu gốc) | paraphrase | Câu gốc không lấy được gold (lệch từ); model search thêm 2 lượt, "data science cycle steps order" lấy được p020:c04 | 5 bước theo thứ tự [p020:c04] | 2 – đúng, nhưng cần thêm lượt search (rủi ro của BM25) |
| dn01 (BM25 + câu gốc) | thiếu evidence | Câu gốc + 1 lượt search, chỉ tìm thấy khảo sát Anaconda về thu thập/làm sạch dữ liệu | Từ chối | Đúng – không đưa ra tỷ lệ cho deployment |

- Đường dẫn trace, nhãn, lệnh chạy, thời gian và chi phí: `results/dev/<cấu hình>/` gồm `traces.json` (mọi lượt gọi model và search), `review.md` (bảng đọc), `reviews.json` (nhãn), `agent_metrics.json`, `summary.json`. Lệnh: `python -m src.run --config configs/<cấu hình>.json --split dev`, sau đó `python starter/agent_metrics.py --cases data/day6/cases.json --traces results/dev/<cấu hình>/traces.json --reviews results/dev/<cấu hình>/reviews.json --split dev --output results/dev/<cấu hình>/agent_metrics.json`. Thời gian và token xem bảng Retrieval; chi phí = token × giá Gemini ngày chạy.
- Nhãn: 85 nhãn dev do Claude soạn nháp kèm lý do trích đoạn nguồn; tôi đọc lại từng citation và xác nhận kết quả đánh nhãn.
- Kết quả trước/sau, ví dụ lỗi, đánh đổi và giới hạn:
    - Trước/sau: tìm bằng câu gốc trước sửa 2 lỗi của Dense (d01: 0 → 2, d11: 1 → 2) và giảm khoảng một nửa số lượt gọi model ở cả Dense và BM25 (2.8 → 1.4), input token giảm 35–37%, median 6.6–8.6 s → 1.6–2.1 s. Ở baseline, model nhiều lần trả lời bằng text không gọi tool (6–11 lần/17 câu) nên tốn thêm lượt gọi; khi đã có sẵn đoạn của câu gốc thì không còn trường hợp này.
    - Đánh đổi: BM25 + câu gốc rẻ và đơn giản nhất nhưng yếu với câu diễn đạt lại (d02 cần thêm 2 lượt); Dense + câu gốc xử lý ngay ở lượt đầu nhưng cần embedding model và Postgres.
    - Giới hạn: dev đã bão hòa (4 cấu hình đều 2.00) nên không phân biệt được chất lượng giữa các cấu hình tốt; dev chỉ có 15 câu có đáp án, chủ yếu tra cứu một đoạn; nhãn do một người chấm; độ trễ bị ảnh hưởng bởi HTTP 429.

## Thử thách nâng cao (nếu thực hiện)

- Tài liệu, nguồn, quyền sử dụng, số trang và phiên bản:
- Cách xử lý text, bảng, ảnh, biểu đồ; phạm vi index và phần chưa xử lý:
- Cách chia benchmark, schema evidence, model và cấu hình đã chốt trên dev:

| Nhóm test | Đạt / tổng | Tỷ lệ | Lỗi / nhận xét |
|---|---|---|---|
| Bảng | | | |
| Ảnh, sơ đồ | | | |
| Biểu đồ | | | |
| Multi-hop | | | |
| Text | | | |
| Thiếu bằng chứng | | | |
| **Toàn bộ** | | | |

- Trace, nhãn và evidence từng câu; thời gian, chi phí, lỗi hệ thống:
- Giới hạn, cách tái lập và đường dẫn benchmark:
