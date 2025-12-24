import hashlib
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import chromadb
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from pypdf import PdfReader
from docx import Document
from sentence_transformers import SentenceTransformer

# Add src directory to path to import answerers
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR / "src"))
from answerers import build_answerer

DATA_DIR = ROOT_DIR / "data"
DB_DIR = ROOT_DIR / "chroma_db"
# Mặc định đặt model trong thư mục models/all-MiniLM-L6-v2
MODEL_DIR = ROOT_DIR / "models" / "all-MiniLM-L6-v2"

# Simple in-process cache to avoid reloading the same model directory
MODEL_CACHE: Dict[str, SentenceTransformer] = {}

app = FastAPI(title="Mini-RAG API", version="0.1.0")

# Allow local dev origins; tighten in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "data_dir": str(DATA_DIR),
        "db_dir": str(DB_DIR),
        "model_dir": str(MODEL_DIR),
    }


def _ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DB_DIR.mkdir(parents=True, exist_ok=True)


def _resolve_model_path(model_path: Path) -> Path:
    # Thử lần lượt: tuyệt đối, ROOT/<path>, ROOT/models/<path>
    if model_path.is_absolute():
        return model_path
    candidate = (ROOT_DIR / model_path).resolve()
    if candidate.exists():
        return candidate
    candidate_models = (ROOT_DIR / "models" / model_path).resolve()
    return candidate_models


def _load_model(model_path: Path) -> SentenceTransformer:
    resolved = _resolve_model_path(model_path)
    if not resolved.exists():
        raise HTTPException(status_code=400, detail=f"Model directory not found: {resolved}")

    key = str(resolved)
    if key not in MODEL_CACHE:
        MODEL_CACHE[key] = SentenceTransformer(str(resolved))
    return MODEL_CACHE[key]


def _chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    clean = " ".join(text.split())
    if not clean:
        return []
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise HTTPException(status_code=400, detail="Invalid chunk_size/overlap")

    chunks: List[str] = []
    step = chunk_size - overlap
    for start in range(0, len(clean), step):
        chunk = clean[start : start + chunk_size]
        if chunk:
            chunks.append(chunk)
    return chunks


def _extract_pdf(path: Path) -> List[Tuple[int, str]]:
    reader = PdfReader(str(path))
    results: List[Tuple[int, str]] = []
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        results.append((idx + 1, text))
    return results


def _extract_docx(path: Path) -> str:
    doc = Document(str(path))
    parts = [para.text for para in doc.paragraphs if para.text]
    return "\n".join(parts)


def _extract_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _hash_id(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=str(DB_DIR))


@app.post("/api/ingest")
async def ingest(
    file: UploadFile = File(...),
    collection: str = Form("my_docs"),
    chunk_size: int = Form(800),
    overlap: int = Form(150),
    model_dir: str = Form(str(MODEL_DIR)),
) -> dict:
    _ensure_dirs()

    filename = file.filename or "uploaded_file"
    ext = Path(filename).suffix.lower()
    if ext not in {".pdf", ".docx", ".txt"}:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF/DOCX/TXT.")

    save_path = DATA_DIR / filename
    content = await file.read()
    save_path.write_bytes(content)

    # Extract text by type
    page_chunks: List[Tuple[int, List[str]]] = []
    if ext == ".pdf":
        extracted = _extract_pdf(save_path)
        for page_num, text in extracted:
            chunks = _chunk_text(text, chunk_size, overlap)
            if chunks:
                page_chunks.append((page_num, chunks))
    elif ext == ".docx":
        text = _extract_docx(save_path)
        chunks = _chunk_text(text, chunk_size, overlap)
        if chunks:
            page_chunks.append((1, chunks))
    else:  # .txt
        text = _extract_txt(save_path)
        chunks = _chunk_text(text, chunk_size, overlap)
        if chunks:
            page_chunks.append((1, chunks))

    if not page_chunks:
        raise HTTPException(status_code=400, detail="No text extracted from file.")

    model = _load_model(Path(model_dir))
    client = chromadb.PersistentClient(path=str(DB_DIR))
    coll = client.get_or_create_collection(name=collection)

    all_chunks: List[str] = []
    metadatas: List[dict] = []
    ids: List[str] = []

    for page_num, chunks in page_chunks:
        for idx, chunk in enumerate(chunks, start=1):
            all_chunks.append(chunk)
            ids.append(_hash_id(chunk))
            metadatas.append(
                {
                    "source": filename,
                    "page": page_num,
                    "chunk_in_page": idx,
                }
            )

    embeddings = model.encode(all_chunks, normalize_embeddings=True).tolist()

    coll.upsert(ids=ids, documents=all_chunks, embeddings=embeddings, metadatas=metadatas)

    return {
        "stored_chunks": len(all_chunks),
        "collection": collection,
        "source": filename,
    }


class QueryRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    question: str
    collection: str = "my_docs"
    top_k: int = 5
    model_dir: str = str(MODEL_DIR)


    use_llm: bool = True  # Whether to generate answer using LLM
@app.post("/api/query")
async def query(body: QueryRequest) -> dict:
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question is empty")
    if body.top_k <= 0:
        raise HTTPException(status_code=400, detail="top_k must be > 0")

    model = _load_model(Path(body.model_dir))
    client = _client()
    coll = client.get_or_create_collection(name=body.collection)

    query_emb = model.encode([body.question], normalize_embeddings=True).tolist()[0]
    result = coll.query(
        query_embeddings=[query_emb],
        n_results=body.top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    hits = []
    for idx, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), start=1):
        hits.append(
            {
                "rank": idx,
                "distance": dist,
                "metadata": meta,
                "text": doc,
            }
        )
# Generate answer using LLM if requested
    answer = None
    if body.use_llm and documents:
        answerer = build_answerer(prefer_gemini=True)
        answer = answerer.answer(body.question, documents)

    return {
        "question": body.question,
        "collection": body.collection,
        "results": hits,
        "answer": answer,  # Generated answer from LLMdy.collection,
        "results": hits,
    }


@app.get("/api/collections")
async def list_collections() -> dict:
    client = _client()
    cols = client.list_collections()
    return {"collections": [c.name for c in cols]}
