from fastapi import APIRouter, HTTPException

from app.schemas.embedding import EMBEDDING_DIMENSION, MODEL_NAME, EmbeddingRequest, EmbeddingResponse
from app.services.embedding_service import generate_embeddings
from app.services.embedding_text_service import embedding_units

router = APIRouter(prefix="/api/embeddings", tags=["embeddings"])


@router.post("/generate", response_model=EmbeddingResponse)
def generate_embedding_endpoint(request: EmbeddingRequest) -> EmbeddingResponse:
    units = embedding_units(request.resume, request.job_description)
    if not units:
        raise HTTPException(status_code=400, detail="The supplied document contains no embeddable text.")
    try:
        vectors = generate_embeddings(units)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return EmbeddingResponse(
        model=MODEL_NAME,
        dimension=EMBEDDING_DIMENSION,
        items=[
            {"source_type": unit.source_type, "text": unit.text, "embedding": vector}
            for unit, vector in zip(units, vectors)
        ],
    )
