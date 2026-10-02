from functools import lru_cache

from app.services.embedding_text_service import EmbeddingUnit

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model():
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(MODEL_NAME)
    except Exception as exc:
        raise RuntimeError("The local embedding model could not be loaded.") from exc


def generate_embeddings(units: list[EmbeddingUnit]) -> list[list[float]]:
    if not units:
        return []
    texts = [unit.text for unit in units]
    try:
        vectors = get_embedding_model().encode(
            texts, batch_size=len(texts), normalize_embeddings=True, convert_to_numpy=True
        )
        return [vector.astype(float).tolist() for vector in vectors]
    except Exception as exc:
        raise RuntimeError("The embedding model could not encode the requested text.") from exc
