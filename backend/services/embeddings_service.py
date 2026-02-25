"""
Vector embeddings service - FAISS-based semantic search.
Enable by installing: pip install sentence-transformers faiss-cpu

Usage (when enabled):
    from services.embeddings_service import EmbeddingsService
    emb = EmbeddingsService()
    emb.add_resume(id=1, text="...")
    scores = emb.search("python developer job description")
"""
import os

EMBEDDINGS_ENABLED = os.getenv("ENABLE_EMBEDDINGS", "false").lower() == "true"

if EMBEDDINGS_ENABLED:
    try:
        from sentence_transformers import SentenceTransformer
        import faiss
        import numpy as np

        class EmbeddingsService:
            """FAISS-based semantic search for resume-job matching."""

            def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
                self.model = SentenceTransformer(model_name)
                self.dimension = self.model.get_sentence_embedding_dimension()
                self.index = faiss.IndexFlatIP(self.dimension)  # Inner product (cosine with normalized)
                self.id_map = []  # Maps index position to resume id

            def add_resume(self, id: int, text: str):
                emb = self.model.encode([text], normalize_embeddings=True)
                self.index.add(emb.astype("float32"))
                self.id_map.append(id)

            def search(self, query: str, top_k: int = 5):
                q_emb = self.model.encode([query], normalize_embeddings=True).astype("float32")
                scores, indices = self.index.search(q_emb, min(top_k, len(self.id_map)))
                return [
                    {"id": self.id_map[i], "score": float(scores[0][j])}
                    for j, i in enumerate(indices[0])
                    if 0 <= i < len(self.id_map)
                ]

    except ImportError:
        EMBEDDINGS_ENABLED = False


_instance = None

def get_embeddings_service():
    """Returns a singleton EmbeddingsService if enabled, else None."""
    global _instance
    if EMBEDDINGS_ENABLED:
        if _instance is None:
            _instance = EmbeddingsService()
        return _instance
    return None
