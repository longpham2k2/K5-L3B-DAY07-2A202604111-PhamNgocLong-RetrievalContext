# Báo cáo Day 7

## Dữ liệu và benchmark

- Nguồn, quyền sử dụng, số trang và số chunk: Chương 1 "What Are Data and Data Science?" của giáo trình "Principles of Data Science", gồm 5 mục 1.1–1.5. Nguồn: https://openstax.org/details/books/principles-data-science. Giấy phép CC BY-NC-SA 4.0 (trang 4 PDF), cho phép dùng phi thương mại có ghi nguồn. Sử dụng 45 trang nội dung từ 19-63 (trang in 9-53), bỏ qua 1-18 (bìa, bản quyền, mục lục, lời nói đầu) và 64-66 (câu hỏi ôn tập không có đáp án và tài liệu tham khảo). Đơn vị đếm là số trang do trình xem PDF hiển thị, số in trên sách = trang PDF − 10 và được lưu riêng ở trường `printed_page`. Tái sử dụng day 6, đã chọn strategy C nên có số chunk = 135.
- Vector store, embedding model, phiên bản và số chiều: Vector được lưu trên PostgreSQL 17.11 có extension pgvector 0.8.7. Sử dụng model MiniLM-L6-v2 do sách viết bằng tiếng Anh, chạy local, lưu 384 chiều, sử dụng sentence-transformers 6.3.0. 
- Agent model, cách chạy và phân chia dev/test:
    - Agent model: gemini-3.5-flash-lite gọi qua endpoint tương thích của Google, với providers.py port từ lab trước (DAY04). Vì mục đích là RAG nên set temperature = 0. Đã kiểm tra model hỗ trợ tool-calling với câu "What is the Iris dataset?", model gọi search với {"query": "Iris dataset"}, khoảng 0,6 s/lượt. Mỗi lượt gọi ghi lại input_tokens/output_tokens và latency_ms để tính thời gian và chi phí theo bảng giá Gemini ở ngày chạy. Lỗi HTTP 429/5xx được thử lại với backoff (5–40 s); nếu vẫn lỗi, câu đó ghi status: "error" và báo riêng, không thay bằng kết quả giả. . Embedding cho truy vấn vẫn sử dụng all-MiniLM-L6-v2 từ Day 6.
    - Cách chạy: Python 3.15.2, python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt. Chép .env.example thành .env, điền DATABASE_URL của PostgreSQL/pgvector Day 6 và GEMINI_API_KEY. Sau đó:
        - python -m src.day6_adapter --day6-dir <repo Day 6>: xuất chunk và câu hỏi ra data/day6/.
        - python -m src.verify_evidence --pdf <PDF>: kiểm tra 20/20 evidence truy được về đúng một chunk và có trong trang PDF gốc.
        - python -m unittest discover -s tests -v: test offline.
        - <lệnh chạy agent>
    - Phân chia dev/test: 24 câu. Dev 17 câu = 15 có đáp án (d01–d15) + 2 thiếu evidence (dn01, dn02). Test 7 câu = 5 có đáp án (t01–t05) + 2 thiếu evidence (tn01, tn02). 20 câu có đáp án giữ nguyên split của Day 6, cố định trước lần truy xuất đầu tiên. Gold page của test (26, 34, 40, 43, 54) không trùng trang nào của dev. 4 câu thiếu evidence viết mới cho Day 7. Agent chỉ đọc data/day6/cases.json (id, câu hỏi, filter section có sẵn ở 4 câu d13–d15, t05), không có gold hay đáp án. Mọi lựa chọn phương pháp và cấu hình chỉ dựa trên dev theo tiêu chí công bố trước; test chạy một lần cho baseline và cấu hình đã chốt. Day 6 đã chạy test dense (C) cùng lúc với dev, nhưng việc chọn C dựa trên dev; điều này được ghi rõ như một giới hạn.
- Cách xác định câu có/thiếu evidence và tiêu chí chấm:
    - 20 câu có đáp án lấy từ Day 6 (15 dev d01–d15, 5 test t01–t05). Split cố định từ Day 6; test Day 6 chỉ chạy sau khi chốt cấu hình nên không dùng để chỉnh.
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
| Baseline | | | dev | | | | |
| Phương pháp 2 | | | dev | | | | |
| Phương pháp 3 | | | dev | | | | |
| Cải thiện 1 | | | dev | | | | |
| Cải thiện 2 | | | dev | | | | |
| Cấu hình đã chọn | | | test | | | | |
| Baseline | | | test | | | | |

Một cấu hình có thể đồng thời là phương pháp mới và cải thiện; giải thích rõ. Báo `n/N` và tỷ lệ, ghi đơn vị thời gian/chi phí, so sánh test sau khi chốt. Nêu hai lỗi dev, nguyên nhân, cách thử và lý do chọn cấu hình:

## Agent và đánh giá

- Tool, số lượt gọi, điều kiện dừng, cách chọn context và xử lý lỗi:

| Cấu hình / split | Tool use | Số lượt gọi | Grounded answer 0/1/2 và trung bình | Citation hợp lệ | Câu có citation | Abstention đúng | Từ chối nhầm |
|---|---|---|---|---|---|---|---|

| Query ID | Loại câu | Tool call và kết quả | Câu trả lời và citation | Nhãn, lý do |
|---|---|---|---|---|

- Đường dẫn trace, nhãn, lệnh chạy, thời gian và chi phí:
- Kết quả trước/sau, ví dụ lỗi, đánh đổi và giới hạn:

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
