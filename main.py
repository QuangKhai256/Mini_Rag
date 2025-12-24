import argparse
from hashlib import sha256
from pathlib import Path
from typing import Dict, List, Tuple

from src.chunking import build_chunks
from src.embedding import encode_texts, load_model
from src.loaders import load_document
from src.vectordb import get_collection, query_chunks, upsert_chunks
from src.answerers import build_answerer
from src.cache import load_cache, append_cache


def ingest(
    file_path: Path,
    model_path: str | Path,
    db_path: Path,
    collection_name: str,
    chunk_size: int,
    chunk_overlap: int,
    device: str | None,
    batch_size: int,
    cache_dir: Path,
) -> Tuple[object, object]:
    if not file_path.exists():
        raise FileNotFoundError(file_path)

    pages = load_document(file_path)
    raw_chunks, _, metas = build_chunks(file_path, pages, chunk_size, chunk_overlap)
    if not raw_chunks:
        raise ValueError("No text found to ingest.")

    seen_hashes: Dict[str, bool] = {}
    chunks: List[str] = []
    ids: List[str] = []
    metas_dedup: List[dict] = []
    hashes: List[str] = []
    for chunk, meta in zip(raw_chunks, metas):
        h = sha256(chunk.encode("utf-8")).hexdigest()
        if h in seen_hashes:
            continue
        seen_hashes[h] = True
        chunk_id = f"sha256_{h}"
        chunks.append(chunk)
        ids.append(chunk_id)
        meta_copy = dict(meta)
        meta_copy["hash"] = h
        metas_dedup.append(meta_copy)
        hashes.append(h)

    source_key = sha256(str(file_path).encode("utf-8")).hexdigest()
    cache_path = cache_dir / f"embeddings_{source_key}.jsonl"
    cache = load_cache(cache_path)

    missing_pairs = [(h, c) for h, c in zip(hashes, chunks) if h not in cache]
    model = load_model(model_path, device=device)
    if missing_pairs:
        print(f"Encoding {len(missing_pairs)} / {len(chunks)} new chunks (batch_size={batch_size})...")
        missing_embeddings = encode_texts(
            model,
            [c for _, c in missing_pairs],
            normalize=True,
            batch_size=batch_size,
        )
        append_cache(cache_path, zip((h for h, _ in missing_pairs), missing_embeddings))
        for h, emb in zip((h for h, _ in missing_pairs), missing_embeddings):
            cache[h] = emb
    else:
        print("All chunks reused from cache; skip encoding.")

    embeddings = [cache[h] for h in hashes]

    collection = get_collection(db_path, collection_name)
    upsert_chunks(collection, ids, chunks, metas_dedup, embeddings)
    print(f"Ingested {len(chunks)} deduped chunks into collection '{collection_name}'.")
    return model, collection


def interactive_query(model, collection, top_k: int, mode: str):
    answerer = build_answerer(prefer_gemini=True)
    while True:
        query = input("Query (blank to exit): ").strip()
        if not query:
            break
        q_emb = encode_texts(model, [query], normalize=True)[0]
        results = query_chunks(collection, q_emb, top_k)

        for rank, (doc, meta, dist) in enumerate(results, start=1):
            source = meta.get("source", "") if isinstance(meta, dict) else ""
            page = meta.get("page", "?") if isinstance(meta, dict) else "?"
            preview = (doc or "")[:500].replace("\n", " ")
            print(f"#{rank} | dist={dist:.4f} | source={source} | page={page}\n  {preview}\n")

        if mode == "answer":
            context_chunks = [doc for doc, _, _ in results if doc]
            answer = answerer.answer(query, context_chunks)
            print("ANSWER:\n" + answer + "\n")


def parse_args():
    parser = argparse.ArgumentParser(description="Mini-RAG with ChromaDB (modular)")
    parser.add_argument("--file", required=True, help="Path to PDF/DOCX/TXT file")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", help="Path or name of SentenceTransformer model")
    parser.add_argument("--db", default="./chroma_db", help="ChromaDB persist directory")
    parser.add_argument("--collection", default="my_docs", help="Collection name")
    parser.add_argument("--chunk-size", type=int, default=800, help="Chunk size (chars)")
    parser.add_argument("--chunk-overlap", type=int, default=150, help="Chunk overlap (chars)")
    parser.add_argument("--top-k", type=int, default=3, help="Top-k results when querying")
    parser.add_argument("--device", default=None, help="Force device for SentenceTransformer (e.g., cpu or cuda)")
    parser.add_argument("--mode", choices=["retrieval", "answer"], default="retrieval", help="retrieval: show chunks; answer: synthesize answer from context")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for encoding embeddings")
    parser.add_argument("--cache-dir", default="./cache", help="Directory for embedding cache files")
    return parser.parse_args()


def main():
    args = parse_args()
    file_path = Path(args.file).resolve()
    db_path = Path(args.db)

    model, collection = ingest(
        file_path=file_path,
        model_path=args.model,
        db_path=db_path,
        collection_name=args.collection,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        device=args.device,
        batch_size=args.batch_size,
        cache_dir=Path(args.cache_dir),
    )

    interactive_query(model, collection, args.top_k, args.mode)


if __name__ == "__main__":
    main()
