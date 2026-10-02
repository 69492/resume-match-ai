from fastapi import APIRouter, HTTPException

from app.schemas.similarity import SimilarityRequest, SimilarityResponse
from app.services.similarity_service import SimilarityError, analyze_similarity

router = APIRouter(prefix="/api/similarity", tags=["similarity"])


@router.post("/analyze", response_model=SimilarityResponse)
def analyze_similarity_endpoint(request: SimilarityRequest) -> SimilarityResponse:
    try:
        return analyze_similarity(request.resume_items, request.required_items, request.preferred_items)
    except SimilarityError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
