from pathlib import Path
from typing import List, Tuple

PageText = List[Tuple[int, str]]


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    normalized = " ".join(text.split())
    if not normalized:
        return []
    chunks: List[str] = []
    step = max(1, chunk_size - overlap)
    start = 0
    while start < len(normalized):
        piece = normalized[start : start + chunk_size]
        if piece.strip():
            chunks.append(piece)
        start += step
    return chunks


def build_chunks(doc_path: Path, pages: PageText, chunk_size: int, overlap: int) -> Tuple[List[str], List[str], List[dict]]:
    chunks: List[str] = []
    ids: List[str] = []
    metas: List[dict] = []
    base = doc_path.stem.replace(" ", "_")
    for page_num, text in pages:
        page_chunks = chunk_text(text, chunk_size, overlap)
        for idx, chunk in enumerate(page_chunks):
            chunks.append(chunk)
            ids.append(f"{base}_p{page_num}_c{idx:04d}")
            metas.append({"source": str(doc_path), "page": page_num})
    return chunks, ids, metas
