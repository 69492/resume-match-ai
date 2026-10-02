from pydantic import BaseModel, Field


class MatchScoreResponse(BaseModel):
    """Deterministic semantic alignment score for a resume and job description."""

    overall_score: float = Field(..., ge=0, le=100)
    score_label: str
    required_score: float = Field(..., ge=0, le=100)
    preferred_score: float = Field(..., ge=0, le=100)
    required_weight: float = Field(..., ge=0, le=1)
    preferred_weight: float = Field(..., ge=0, le=1)
    required_count: int = Field(..., ge=0)
    preferred_count: int = Field(..., ge=0)
    strong_count: int = Field(..., ge=0)
    partial_count: int = Field(..., ge=0)
    missing_count: int = Field(..., ge=0)
