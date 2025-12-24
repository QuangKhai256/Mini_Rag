# Báo cáo Mini-RAG + ChromaDB

## 1) Thông tin tài liệu (điền sau khi chọn)
- Tên file: _______________________________
- Định dạng: PDF / DOCX / TXT
- Chủ đề: _______________________________
- Số trang / độ dài: ______________________

## 2) Pipeline (6 bước)
1. Nạp tài liệu: đọc PDF/DOCX/TXT, trích văn bản theo trang.
2. Làm sạch & chia khối: normalize khoảng trắng, chunk_size=..., overlap=..., sinh ID ổn định theo hash.
3. Mã hóa embedding: dùng SentenceTransformer (local) với batch_size=..., normalize_embeddings=True.
4. Lưu vector store: ghi vào ChromaDB (duckdb+parquet), collection theo tên cấu hình.
5. Truy vấn: nhận câu hỏi, encode query, lấy top-k chunks kèm metadata (source, page, hash).
6. Trả lời (tùy chọn): ghép CONTEXT từ top-k; nếu có GEMINI_API_KEY dùng Gemini, nếu không dùng DummyAnswerer (echo/tóm tắt).

## 3) Các truy vấn đã thử
| # | Câu hỏi | Kết quả tóm tắt (ngắn) |
|---|---------|------------------------|
| 1 | _______________________________ | _______________________________ |
| 2 | _______________________________ | _______________________________ |
| 3 | _______________________________ | _______________________________ |

## 4) Nhận xét & đề xuất
- Chất lượng hiện tại: ______________________________________________
- Hạn chế quan sát: ________________________________________________
- Đề xuất cải thiện:
  - Chunking: thử kích thước/overlap khác (ví dụ 500/50, 800/150, 1200/250), dedup hash để giảm trùng.
  - Model: cân nhắc bản lớn hơn (e.g., all-mpnet-base-v2) nếu tài nguyên cho phép.
  - top_k: điều chỉnh 3-10 tùy câu hỏi; tăng khi cần phủ rộng ngữ cảnh.
  - Làm sạch: loại bỏ heading/footer lặp, ký tự nhiễu trước khi chunk.
  - Cache: giữ embedding cache để chạy lại nhanh; kiểm tra collection name theo config để so sánh.
