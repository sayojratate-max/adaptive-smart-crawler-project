from __future__ import annotations
import pickle
from pathlib import Path
import numpy as np

from sentence_transformers import SentenceTransformer
import faiss

# Store index + mappings
BASE_DIR = Path(__file__).resolve().parent
INDEX_PATH = BASE_DIR / "output" / "faiss.index"
MAP_PATH = BASE_DIR / "output" / "faiss_map.pkl"

# Lightweight fast model (good quality)
MODEL_NAME = "all-MiniLM-L6-v2"

_model = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def build_faiss_index(docs: list[tuple[int, str]]) -> int:
    """
    docs: list of (doc_id, text_for_embedding)
    saves faiss index to output folder
    returns number indexed
    """
    if not docs:
        return 0

    model = get_model()
    texts = [t for _, t in docs]
    ids = [i for i, _ in docs]

    embeddings = model.encode(texts, normalize_embeddings=True)
    embeddings = np.array(embeddings, dtype="float32")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine similarity using normalized vectors
    index.add(embeddings)

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))

    with open(MAP_PATH, "wb") as f:
        pickle.dump(ids, f)

    return len(ids)


def semantic_search(query: str, top_k: int = 5) -> list[tuple[int, float]]:
    """
    returns list of (doc_id, score)
    """
    if not INDEX_PATH.exists() or not MAP_PATH.exists():
        return []

    model = get_model()
    q_emb = model.encode([query], normalize_embeddings=True)
    q_emb = np.array(q_emb, dtype="float32")

    index = faiss.read_index(str(INDEX_PATH))
    with open(MAP_PATH, "rb") as f:
        ids = pickle.load(f)

    scores, idxs = index.search(q_emb, top_k)

    results = []
    for j, score in zip(idxs[0], scores[0]):
        if j == -1:
            continue
        results.append((ids[j], float(score)))

    return results
