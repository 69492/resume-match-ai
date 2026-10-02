import math
from functools import lru_cache

from app.schemas.embedding import EMBEDDING_DIMENSION, MODEL_NAME
from app.services.embedding_text_service import EmbeddingUnit


@lru_cache(maxsize=1)
def get_embedding_model():
    """Load the quantized ONNX model once per backend process, on first use."""
    try:
        from fastembed import TextEmbedding

        return TextEmbedding(
            model_name=MODEL_NAME,
            providers=["CPUExecutionProvider"],
        )
    except Exception as exc:
        raise RuntimeError("The FastEmbed ONNX model could not be loaded.") from exc


def _normalized_vector(vector) -> list[float]:
    values = [float(value) for value in vector]
    if len(values) != EMBEDDING_DIMENSION:
        raise RuntimeError("The embedding model returned an unexpected vector dimension.")
    if not all(math.isfinite(value) for value in values):
        raise RuntimeError("The embedding model returned invalid vector values.")
    norm = math.sqrt(sum(value * value for value in values))
    if norm == 0:
        raise RuntimeError("The embedding model returned a zero vector.")
    return [value / norm for value in values]


def generate_embeddings(units: list[EmbeddingUnit]) -> list[list[float]]:
    if not units:
        return []
    try:
        # FastEmbed yields one vector at a time while performing batched ONNX inference.
        vectors = get_embedding_model().embed(
            [unit.text for unit in units],
            batch_size=len(units),
        )
        return [_normalized_vector(vector) for vector in vectors]
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError("The embedding model could not encode the requested text.") from exc
