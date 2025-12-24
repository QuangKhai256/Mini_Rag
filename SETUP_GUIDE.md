# Hướng dẫn Setup và Sử dụng Mini-RAG

## Vấn đề đã fix

### Vấn đề trước đây:
- Hệ thống chỉ trả về danh sách documents tương tự
- Không có câu trả lời tổng hợp/chi tiết cho câu hỏi của người dùng
- Người dùng phải tự đọc qua các chunks để tìm câu trả lời

### Giải pháp:
✅ Tích hợp LLM (Gemini) để sinh câu trả lời từ context
✅ Hiển thị câu trả lời chi tiết trên giao diện
✅ Vẫn giữ nguồn tham khảo (documents) để người dùng kiểm chứng

## Cài đặt

### 1. Cài đặt Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Cấu hình Gemini API (Tùy chọn nhưng khuyến nghị)

**Lấy API Key miễn phí:**
- Truy cập: https://aistudio.google.com/app/apikey
- Đăng nhập với Google account
- Tạo API key mới

**Thiết lập biến môi trường:**

Windows (PowerShell):
```powershell
$env:GEMINI_API_KEY="your-api-key-here"
```

Windows (CMD):
```cmd
set GEMINI_API_KEY=your-api-key-here
```

Linux/Mac:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

**Hoặc tạo file `.env` trong thư mục gốc:**
```
GEMINI_API_KEY=your-api-key-here
```

> **Lưu ý:** Nếu không cấu hình GEMINI_API_KEY, hệ thống sẽ dùng DummyAnswerer (chỉ tóm tắt context, không sinh câu trả lời thông minh).

### 3. Chạy Backend

```bash
# Từ thư mục backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Hoặc dùng file batch:
```bash
# Từ thư mục gốc
run_backend.bat
```

### 4. Cài đặt và Chạy Frontend

```bash
cd frontend
npm install
npm run dev
```

Hoặc dùng file batch:
```bash
# Từ thư mục gốc
run_frontend.bat
```

## Sử dụng

### 1. Ingest Documents
- Upload file (PDF, DOCX, TXT)
- Chọn collection name (mặc định: my_docs)
- Cấu hình chunk size và overlap
- Nhấn "Upload & Ingest"

### 2. Query với câu trả lời chi tiết
- Nhập câu hỏi
- Chọn collection (phải khớp với collection đã ingest)
- Số lượng kết quả (top_k)
- Nhấn "Tìm kiếm"

**Kết quả hiển thị:**
1. **Câu trả lời chi tiết** (ở trên) - Được sinh bởi LLM từ context
2. **Nguồn tham khảo** (ở dưới) - Các chunks được sử dụng để tạo câu trả lời

## Kiểm tra lỗi

### Backend không trả về câu trả lời:
```bash
# Kiểm tra GEMINI_API_KEY
echo $env:GEMINI_API_KEY  # Windows PowerShell
echo %GEMINI_API_KEY%      # Windows CMD
echo $GEMINI_API_KEY       # Linux/Mac
```

### Kiểm tra backend logs:
```bash
# Xem logs trong terminal chạy uvicorn
# Nếu thấy lỗi "No module named 'google.generativeai'"
pip install google-generativeai
```

### Frontend không hiển thị câu trả lời:
- Mở Developer Console (F12)
- Kiểm tra tab Network để xem response từ API
- Xem có field "answer" trong response không

## Test thử

### Ví dụ test với câu hỏi về tài liệu đã ingest:

1. **Ingest file intro.pdf** (hoặc file khác về RAG/ChromaDB)

2. **Query:**
   - Câu hỏi: "ChromaDB là gì?"
   - Kết quả mong đợi: Câu trả lời tổng hợp từ các chunks liên quan

3. **So sánh:**
   - **Trước:** Chỉ thấy list các chunks, phải tự đọc
   - **Sau:** Thấy câu trả lời rõ ràng + nguồn tham khảo

## API Endpoints

### POST /api/query
```json
{
  "question": "string",
  "collection": "my_docs",
  "top_k": 5,
  "model_dir": "./all-MiniLM-L6-v2",
  "use_llm": true
}
```

Response:
```json
{
  "question": "string",
  "collection": "string",
  "answer": "Câu trả lời chi tiết từ LLM...",
  "results": [
    {
      "rank": 1,
      "distance": 0.123,
      "metadata": {...},
      "text": "chunk content..."
    }
  ]
}
```

## Troubleshooting

### Lỗi: "No module named 'google'"
```bash
pip install google-generativeai
```

### Lỗi: "GEMINI_API_KEY not found" 
- Hệ thống vẫn chạy nhưng dùng DummyAnswerer
- Để có câu trả lời tốt, cần thiết lập GEMINI_API_KEY

### Câu trả lời không đúng/không liên quan:
1. Kiểm tra dữ liệu đã ingest có chứa thông tin cần thiết không
2. Tăng top_k để lấy nhiều context hơn
3. Thử chunk_size nhỏ hơn (500-600) để có chunks chính xác hơn

### Distance score cao (> 1.0):
- Distance càng nhỏ càng tốt (0 = perfect match)
- Nếu distance > 1.0, có thể câu hỏi không liên quan đến tài liệu
- Cần ingest thêm tài liệu phù hợp

## Cải tiến trong tương lai

- [ ] Thêm streaming response cho câu trả lời
- [ ] Support nhiều LLM khác nhau (OpenAI, Claude, etc.)
- [ ] Caching câu trả lời
- [ ] Hiển thị citation links cho từng câu trong answer
- [ ] Multi-collection query
