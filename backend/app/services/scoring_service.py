import math

from app.core.scoring_config import (
    PREFERRED_WEIGHT,
    REQUIRED_WEIGHT,
    SCORE_BANDS,
)
from app.schemas.scoring import MatchScoreResponse
from app.schemas.similarity import SimilarityResponse


class ScoringError(ValueError):
    """Raised when similarity results cannot produce a score."""


def _normalized_similarity(value: float) -> float:
    """Clamp cosine similarity to the usable score range [0, 1]."""
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
        raise ScoringError("Similarity values must be finite numbers.")
    return max(0.0, min(1.0, float(value)))


def _score_label(score: float) -> str:
    for minimum, label in SCORE_BANDS:
        if score >= minimum:
            return label
    return SCORE_BANDS[-1][1]


def _average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def calculate_match_score(similarity: SimilarityResponse) -> MatchScoreResponse:
    """Calculate a score from Phase 5 results without re-running similarity."""
    if not similarity.matches:
        raise ScoringError("At least one required or preferred requirement is needed to calculate a score.")

    required_values = [
        _normalized_similarity(match.similarity)
        for match in similarity.matches
        if match.requirement_type == "required"
    ]
    preferred_values = [
        _normalized_similarity(match.similarity)
        for match in similarity.matches
        if match.requirement_type == "preferred"
    ]

    required_score = _average(required_values)
    preferred_score = _average(preferred_values)
    if required_values and preferred_values:
        overall = required_score * REQUIRED_WEIGHT + preferred_score * PREFERRED_WEIGHT
    elif required_values:
        overall = required_score
    elif preferred_values:
        overall = preferred_score
    else:
        raise ScoringError("At least one required or preferred requirement is needed to calculate a score.")

    overall = max(0.0, min(100.0, overall * 100.0))
    required_percent = max(0.0, min(100.0, required_score * 100.0))
    preferred_percent = max(0.0, min(100.0, preferred_score * 100.0))
    counts = {category: sum(match.category == category for match in similarity.matches)
              for category in ("strong", "partial", "missing")}

    return MatchScoreResponse(
        overall_score=round(overall, 1),
        score_label=_score_label(overall),
        required_score=required_percent,
        preferred_score=preferred_percent,
        required_weight=REQUIRED_WEIGHT,
        preferred_weight=PREFERRED_WEIGHT,
        required_count=len(required_values),
        preferred_count=len(preferred_values),
        strong_count=counts["strong"],
        partial_count=counts["partial"],
        missing_count=counts["missing"],
    )
