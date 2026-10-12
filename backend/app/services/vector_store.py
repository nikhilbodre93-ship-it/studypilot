import math
import re
from typing import List, Dict, Any, Optional
from collections import Counter


class VectorStore:
    """
    Lightweight, deterministic vector retriever for topic materials.
    Uses TF-IDF cosine similarity for offline local dev/testing,
    with an interface compatible with Chroma/pgvector for production.
    """

    def __init__(self):
        # topic_id -> list of chunk dicts
        # chunk dict: {"chunk_id": str, "citation": str, "page": int, "text": str, "vector": dict}
        self._stores: Dict[int, List[Dict[str, Any]]] = {}

    def _tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r"\b[a-zA-Z0-9_]{3,}\b", text)]

    def _compute_vector(self, text: str) -> Dict[str, float]:
        tokens = self._tokenize(text)
        if not tokens:
            return {}
        counts = Counter(tokens)
        length = math.sqrt(sum(c * c for c in counts.values()))
        if length == 0:
            return {}
        return {term: count / length for term, count in counts.items()}

    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        intersection = set(vec1.keys()) & set(vec2.keys())
        return sum(vec1[t] * vec2[t] for t in intersection)

    def add_chunks(self, topic_id: int, chunks: List[Dict[str, Any]]) -> None:
        if topic_id not in self._stores:
            self._stores[topic_id] = []
        for ch in chunks:
            ch["vector"] = self._compute_vector(ch["text"])
            self._stores[topic_id].append(ch)

    def search(self, topic_id: int, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        chunks = self._stores.get(topic_id, [])
        if not chunks:
            return []

        query_vec = self._compute_vector(query)
        if not query_vec:
            return chunks[:top_k]

        scored = []
        for ch in chunks:
            score = self._cosine_similarity(query_vec, ch.get("vector", {}))
            scored.append((score, ch))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [ch for score, ch in scored[:top_k]]

    def clear_topic(self, topic_id: int) -> None:
        if topic_id in self._stores:
            del self._stores[topic_id]


# Global in-memory vector store instance
global_vector_store = VectorStore()
