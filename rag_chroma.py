import argparse
import os
from pathlib import Path
from typing import List, Tuple

from chromadb import PersistentClient
from chromadb.config import Settings
from docx import Document
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


def load_text_with_pages(file_path: Path) -> List[Tuple[int, str]]:
    """Return list of (page_number, text) pairs extracted from file."""
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(file_path))
        pages = []
        for i, page in enumerate(reader.pages):
            txt = page.extract_text() or ""
            pages.append((i + 1, txt))
        return pages
    if suffix in {".docx", ".doc"}:
        doc = Document(str(file_path))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return [(1, "\n".join(paragraphs))]
    if suffix == ".txt":
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        return [(1, text)]
    raise ValueError(f"Unsupported file type: {suffix}")


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    text = " ".join(text.split())  # normalize whitespace
    if not text:
        return []
    chunks = []
    step = max(1, chunk_size - overlap)
    start = 0
    while start < len(text):
        chunk = text[start : start + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
        start += step
    return chunks


def build_ids(base: str, page: int, count: int) -> List[str]:
    safe_base = base.replace(" ", "_")
    return [f"{safe_base}_p{page}_c{i:04d}" for i in range(count)]


def ensure_collection(client: PersistentClient, name: str):
    return client.get_or_create_collection(name=name)


def safe_upsert(collection, ids, documents, metadatas, embeddings):
    if hasattr(collection, "upsert"):
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        return
    try:
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )
    except Exception:
        try:
            collection.delete(ids=ids)
        except Exception:
            pass
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )


def ingest(args):
    file_path = Path(args.file).resolve()
    if not file_path.exists():
        raise FileNotFoundError(file_path)

    pages = load_text_with_pages(file_path)
    all_chunks = []
    all_meta = []

    for page_num, text in pages:
        chunks = chunk_text(text, args.chunk_size, args.chunk_overlap)
        if not chunks:
            continue
        ids = build_ids(file_path.stem, page_num, len(chunks))
        all_chunks.extend(zip(ids, chunks, [page_num] * len(chunks)))

    if not all_chunks:
        raise ValueError("No text found to ingest.")

    model = SentenceTransformer(str(args.model), device=args.device)
    documents = [chunk for _, chunk, _ in all_chunks]
    embeddings = model.encode(documents, normalize_embeddings=True).tolist()

    ids = [cid for cid, _, _ in all_chunks]
    metadatas = [
        {
            "source": str(file_path),
            "page": page,
        }
        for _, _, page in all_chunks
    ]

    Path(args.db).mkdir(parents=True, exist_ok=True)
    client = PersistentClient(path=str(args.db), settings=Settings())
    collection = ensure_collection(client, args.collection)
    safe_upsert(collection, ids, documents, metadatas, embeddings)
    print(f"Ingested {len(documents)} chunks into collection '{args.collection}'.")

    return model, collection


def interactive_query(model, collection, top_k: int):
    while True:
        query = input("Query (blank to exit): ").strip()
        if not query:
            break
        q_emb = model.encode([query], normalize_embeddings=True).tolist()[0]
        result = collection.query(
            query_embeddings=[q_emb],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        dists = result.get("distances", [[]])[0]

        for rank, (doc, meta, dist) in enumerate(zip(docs, metas, dists), start=1):
            source = meta.get("source", "") if isinstance(meta, dict) else ""
            page = meta.get("page", "?") if isinstance(meta, dict) else "?"
            preview = (doc or "")[:500].replace("\n", " ")
            print(
                f"#{rank} | dist={dist:.4f} | source={source} | page={page}\n  {preview}\n"
            )


def main():
    parser = argparse.ArgumentParser(description="Mini-RAG with ChromaDB")
    parser.add_argument("--file", required=True, help="Path to PDF/DOCX/TXT file")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", help="Path or name of SentenceTransformer model")
    parser.add_argument("--db", default="./chroma_db", help="ChromaDB persist directory")
    parser.add_argument("--collection", default="my_docs", help="Collection name")
    parser.add_argument("--chunk-size", type=int, default=800, help="Chunk size (chars)")
    parser.add_argument("--chunk-overlap", type=int, default=150, help="Chunk overlap (chars)")
    parser.add_argument("--top-k", type=int, default=3, help="Top-k results when querying")
    parser.add_argument("--device", default=None, help="Force device for SentenceTransformer (e.g., cpu or cuda)")

    args = parser.parse_args()

    model, collection = ingest(args)
    interactive_query(model, collection, args.top_k)


if __name__ == "__main__":
    main()
