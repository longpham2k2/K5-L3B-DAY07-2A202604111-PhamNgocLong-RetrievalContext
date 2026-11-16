# Day 7 — Agentic RAG

**Bài cá nhân · Python 3.11+ · tiếp nối Day 6**

Dùng embedding và vector store từ Day 6 để xây một agent biết tìm bằng chứng, trả lời có nguồn và nhận biết khi không đủ thông tin. Bạn tự chọn kiến trúc, số tool và cách tổ chức retrieval.

> **Tùy chọn:** [Gợi ý dùng AI để lập trình](AGENT_SETUP.md) giúp bạn làm lab; phần này không bắt buộc và không tính điểm.

## Bài cần làm

![Agent tìm tài liệu trong kho Day 6 và trả lời có nguồn](assets/retrieval-pipeline.svg)

1. Kết nối dữ liệu, embedding và vector store Day 6.
2. Xây agent dùng model thật và ít nhất một khả năng truy xuất dữ liệu. Agent có thể dùng nhiều tool và nhiều lượt gọi.
3. Thử **ít nhất 3 phương pháp retrieval khác nhau**, trong đó có dense retrieval dùng vector store Day 6. Tự chọn các phương pháp còn lại; xem [gợi ý](GUIDE.md#2-thử-các-phương-pháp-retrieval).
4. Thử nhiều cấu hình, benchmark, phân tích lỗi và chọn cấu hình tốt trên **dev**; sau đó đánh giá trên **test**.

Benchmark tối thiểu có **24 câu**: dev gồm 15 câu có đáp án và 2 câu thiếu bằng chứng; test gồm 5 câu có đáp án và 2 câu thiếu bằng chứng. Xem [benchmark](BENCHMARK.md) và [rubric](RUBRIC.md).

## Thử thách nâng cao · +15 điểm

Index một tài liệu thực tế từ **100 trang** có bảng, ảnh và biểu đồ; xây agent truy xuất và trả lời các câu hỏi về nội dung đó. Hoàn thành [thử thách nâng cao](ADVANCED.md) và đạt **ít nhất 90% benchmark test** để nhận 15 điểm bonus. Phần cơ bản tối đa 85 điểm; toàn bài tối đa 100 điểm.

## Bắt đầu

1. Đọc [hướng dẫn](GUIDE.md), [rubric](RUBRIC.md) và [quy tắc](RULES.md).
2. Tạo repo cá nhân theo [cách nộp bài](SUBMISSION.md), chuẩn bị đầu ra Day 6 và model hỗ trợ tool calling.
3. Dùng hoặc thay thế [starter](starter/README.md); bạn cần kết nối model và vector store thật.
4. Chạy `python -m unittest discover -s tests -v`. Test mock chỉ kiểm tra code, không phải benchmark agent thật.

![Các bước thử nghiệm trên dev và đánh giá trên test](assets/experiment-loop.svg)

Nộp code, cách chạy, cấu hình, benchmark, trace và [báo cáo](report/individual/MSSV_HoTen.md). Thời gian ở [checkpoints](CHECKPOINTS.md) là gợi ý, có thể điều chỉnh theo lớp và phạm vi thử nghiệm.

## Corpus

OpenStax *Principles of Data Science*, Chapter 1 "What Are Data and Data Science?". Authors: Shaun V. Ault, Soohyun Nam Liao, Larry Musolino (senior contributing authors). The corpus is PDF pages 19–63 (printed pages 9–53), 45 pages. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

The Day 6 repo's `data/manifest.json` records the source, the page list and the counting rule. The PDF is not committed. To reproduce:
1. Download it from https://openstax.org/details/books/principles-data-science.
2. Save it as `data/raw/Principles-of-Data-Science-WEB.pdf` in the Day 6 repo.
3. Check it is the same version: `shasum -a 256` must print `6b47205459a2f4e25a2b2a86369e674a26a5ae566a4cc428dd31047670692398` (37,337,845 bytes). A newer OpenStax PDF may shift page numbers.

Excerpts of the book are stored in `data/day6/` (chunk text in `chunks.json`; evidence quotes in `questions.json` and `evidence_map.json`) and in any agent traces or results this repo produces. They come from *Principles of Data Science* by OpenStax, licensed CC BY-NC-SA 4.0. Access for free at openstax.org.

Changes: the text was extracted from the PDF, normalized (whitespace, running headers and footers removed, hyphenated words re-joined) and split into paragraph chunks. These excerpts are shared under the same CC BY-NC-SA 4.0 license, for non-commercial educational use only.

The benchmark questions, expected answers and absence reasons were written for this lab and are not part of the book.
