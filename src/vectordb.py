from pathlib import Path
from typing import List, Sequence, Tuple

from chromadb import PersistentClient
from chromadb.config import Settings


def get_collection(db_path: Path, name: str):
    db_path.mkdir(parents=True, exist_ok=True)
    client = PersistentClient(path=str(db_path), settings=Settings())
    return client.get_or_create_collection(name=name)


def upsert_chunks(collection, ids: Sequence[str], documents: Sequence[str], metadatas: Sequence[dict], embeddings: Sequence[Sequence[float]]):
    if hasattr(collection, "upsert"):
        collection.upsert(ids=list(ids), documents=list(documents), metadatas=list(metadatas), embeddings=list(embeddings))
        return
    try:
        collection.add(ids=list(ids), documents=list(documents), metadatas=list(metadatas), embeddings=list(embeddings))
        return
    except Exception:
        try:
            collection.delete(ids=list(ids))
        except Exception:
            pass
        collection.add(ids=list(ids), documents=list(documents), metadatas=list(metadatas), embeddings=list(embeddings))


def query_chunks(collection, query_embedding: Sequence[float], top_k: int) -> List[Tuple[str, dict, float]]:
    result = collection.query(
        query_embeddings=[list(query_embedding)],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    dists = result.get("distances", [[]])[0]
    return list(zip(docs, metas, dists))
