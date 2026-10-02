from fastapi import APIRouter, HTTPException

from app.schemas.scoring import MatchScoreResponse
from app.schemas.similarity import SimilarityResponse
from app.services.scoring_service import ScoringError, calculate_match_score

router = APIRouter(prefix="/api/score", tags=["scoring"])


@router.post("/analyze", response_model=MatchScoreResponse)
def analyze_score(request: SimilarityResponse) -> MatchScoreResponse:
    try:
        return calculate_match_score(request)
    except ScoringError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
