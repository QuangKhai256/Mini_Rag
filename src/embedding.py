from pathlib import Path
from typing import List, Sequence, Union

from sentence_transformers import SentenceTransformer


def load_model(model_path: Union[str, Path], device: str | None = None) -> SentenceTransformer:
    return SentenceTransformer(str(model_path), device=device)


def encode_texts(
    model: SentenceTransformer,
    texts: Sequence[str],
    normalize: bool = True,
    batch_size: int = 32,
) -> List[List[float]]:
    if not texts:
        return []
    embeddings = model.encode(
        list(texts), normalize_embeddings=normalize, batch_size=batch_size
    )
    try:
        return embeddings.tolist()
    except AttributeError:
        return [list(e) for e in embeddings]
