# Mini-RAG với ChromaDB

## Cấu trúc thư mục
- data/: đặt tài liệu nguồn (PDF, DOCX, TXT, v.v.) để nạp vào ChromaDB.
- chroma_db/: sẽ tự sinh khi khởi tạo/ghi dữ liệu bằng ChromaDB.
- all-MiniLM-L6-v2/: đã có sẵn mô hình sentence-transformers.

## Chạy dự án (2 terminal)
### 1) Backend (FastAPI)
- Tùy chọn tạo virtualenv
```
python -m venv .venv
.\.venv\Scripts\activate
```
- Cài đặt phụ thuộc
```
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```
- Chạy server (http://localhost:8000)
```
uvicorn backend.app.main:app --reload --port 8000
```

### 2) Frontend (Vite React TS)
- Cài node modules
```
cd frontend
npm install
```
- Cấu hình API (nếu backend không chạy cùng host/port), tạo file `.env` trong frontend:
```
VITE_API_BASE_URL=http://localhost:8000
```
- Chạy dev server (http://localhost:5173)
```
npm run dev -- --port 5173
```

### Script nhanh (Windows)
- Mở 2 cửa sổ: chạy `run_dev.bat`
- Hoặc riêng lẻ: `run_backend.bat` và `run_frontend.bat`

Truy cập UI tại http://localhost:5173

## Ghi chú triển khai Mini-RAG
- Backend đang có khung FastAPI với /health; cần bổ sung /ingest (upload PDF/DOCX/TXT lưu vào ./data và ghi ChromaDB tại ./chroma_db) và /query (encode bằng ./all-MiniLM-L6-v2, truy vấn ChromaDB).
- Frontend đã có nút Ping backend, form upload, form query và vùng hiển thị kết quả; đang giả lập tới khi backend hoàn thiện.
