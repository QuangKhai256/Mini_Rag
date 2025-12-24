import json
from pathlib import Path
from typing import Dict, Iterable, Tuple, Sequence


def load_cache(cache_path: Path) -> Dict[str, Sequence[float]]:
    if not cache_path.exists():
        return {}
    cache: Dict[str, Sequence[float]] = {}
    with cache_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                h = obj.get("hash")
                emb = obj.get("embedding")
                if h and emb is not None:
                    cache[h] = emb
            except Exception:
                continue
    return cache


def append_cache(cache_path: Path, entries: Iterable[Tuple[str, Sequence[float]]]) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("a", encoding="utf-8") as f:
        for h, emb in entries:
            rec = {"hash": h, "embedding": emb}
            f.write(json.dumps(rec) + "\n")
