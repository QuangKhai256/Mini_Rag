import os
from typing import List, Sequence


class DummyAnswerer:
    def answer(self, query: str, context_chunks: Sequence[str]) -> str:
        if not context_chunks:
            return "Không đủ dữ liệu trong CONTEXT để trả lời."
        # Simple offline heuristic: echo key chunks and remind constraints
        joined = " \n".join(context_chunks)
        return (
            "(Dummy) Trả lời dựa trên CONTEXT, không thêm ngoài liệu. "
            f"Câu hỏi: {query}\n\nTóm tắt: {joined[:1200]}"
        )


class GeminiAnswerer:
    def __init__(self) -> None:
        self._client = None
        self._model_name = "gemini-1.5-flash"
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return
        try:
            import google.generativeai as genai  # type: ignore

            genai.configure(api_key=api_key)
            self._client = genai.GenerativeModel(self._model_name)
        except Exception:
            self._client = None

    def answer(self, query: str, context_chunks: Sequence[str]) -> str:
        if not context_chunks:
            return "Không đủ dữ liệu trong CONTEXT để trả lời."
        if not self._client:
            return DummyAnswerer().answer(query, context_chunks)

        context = "\n\n".join(context_chunks)
        prompt = (
            "Chỉ dùng thông tin trong CONTEXT; nếu thiếu thì nói không đủ dữ liệu.\n"
            "CONTEXT:\n" + context + "\n\nCÂU HỎI: " + query
        )
        try:
            resp = self._client.generate_content(prompt)
            text = getattr(resp, "text", None) or "".join(getattr(resp, "candidates", []) or [])
            return text or DummyAnswerer().answer(query, context_chunks)
        except Exception:
            return DummyAnswerer().answer(query, context_chunks)


def build_answerer(prefer_gemini: bool = True):
    if prefer_gemini:
        ans = GeminiAnswerer()
        if getattr(ans, "_client", None):
            return ans
    return DummyAnswerer()
