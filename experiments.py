# Hướng dẫn: python experiments.py --file data\your_file.pdf --model .\all-MiniLM-L6-v2
# Cài đặt: python -m pip install -r requirements.txt
import argparse
from pathlib import Path
from typing import List, Tuple

from src.chunking import build_chunks
from src.embedding import encode_texts, load_model
from src.loaders import load_document
from src.vectordb import get_collection, query_chunks, upsert_chunks


Config = Tuple[int, int, int]


def ingest_for_config(
    file_path: Path,
    model,
    db_dir: Path,
    collection_name: str,
    chunk_size: int,
    overlap: int,
) -> None:
    pages = load_document(file_path)
    chunks, ids, metas = build_chunks(file_path, pages, chunk_size, overlap)
    embeddings = encode_texts(model, chunks, normalize=True)
    collection = get_collection(db_dir, collection_name)
    upsert_chunks(collection, ids, chunks, metas, embeddings)


def run_experiments(file_path: Path, model_path: Path, db_dir: Path) -> None:
    queries = [
        "Tóm tắt nội dung chính",
        "Các ý quan trọng cần lưu ý",
        "Chi tiết cụ thể về tài liệu",
    ]
    configs: List[Config] = [
        (500, 50, 3),
        (500, 50, 5),
        (500, 150, 3),
        (500, 150, 5),
        (500, 250, 3),
        (500, 250, 5),
        (800, 50, 3),
        (800, 50, 5),
        (800, 150, 3),
        (800, 150, 5),
        (800, 250, 3),
        (800, 250, 5),
        (1200, 50, 3),
        (1200, 50, 5),
        (1200, 150, 3),
        (1200, 150, 5),
        (1200, 250, 3),
        (1200, 250, 5),
    ]

    model = load_model(model_path)

    for chunk_size, overlap, top_k in configs:
        coll_name = f"exp_cs{chunk_size}_ov{overlap}_k{top_k}"
        ingest_for_config(file_path, model, db_dir, coll_name, chunk_size, overlap)
        collection = get_collection(db_dir, coll_name)

        print(f"\n=== Config: chunk_size={chunk_size}, overlap={overlap}, top_k={top_k} ===")
        for q in queries:
            q_emb = encode_texts(model, [q], normalize=True)[0]
            results = query_chunks(collection, q_emb, top_k)
            if not results:
                print(f"Query: {q} -> No results")
                continue
            doc, meta, dist = results[0]
            source = meta.get("source", "") if isinstance(meta, dict) else ""
            page = meta.get("page", "?") if isinstance(meta, dict) else "?"
            preview = (doc or "")[:200].replace("\n", " ")
            print(f"Query: {q}\n  top1_dist={dist:.4f} | source={source} | page={page}\n  preview: {preview}")


def parse_args():
    parser = argparse.ArgumentParser(description="Chunk/overlap/top_k sweep experiments")
    parser.add_argument("--file", required=True, help="Path to PDF/DOCX/TXT file")
    parser.add_argument("--model", required=True, help="Path or name of SentenceTransformer model")
    parser.add_argument("--db", default="./chroma_db_exp", help="ChromaDB directory for experiments")
    return parser.parse_args()


def main():
    args = parse_args()
    file_path = Path(args.file).resolve()
    if not file_path.exists():
        raise FileNotFoundError(file_path)
    model_path = Path(args.model)
    db_dir = Path(args.db)

    run_experiments(file_path, model_path, db_dir)


if __name__ == "__main__":
    main()
