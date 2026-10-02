import math
from collections.abc import Sequence

from app.core.similarity_config import PARTIAL_SIMILARITY_THRESHOLD, STRONG_SIMILARITY_THRESHOLD
from app.schemas.similarity import (
    SimilarityEmbeddingItem,
    SimilarityMatch,
    SimilarityResponse,
    SimilaritySummary,
)


class SimilarityError(ValueError):
    """Clear application error for invalid vectors."""


def cosine_similarity(first: Sequence[float], second: Sequence[float]) -> float:
    if not first or not second:
        raise SimilarityError("Embedding vectors must be non-empty.")
    if len(first) != len(second):
        raise SimilarityError("Embedding vectors must have equal dimensions.")
    if not all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in [*first, *second]):
        raise SimilarityError("Embedding vectors must contain only numeric values.")
    if not all(math.isfinite(value) for value in [*first, *second]):
        raise SimilarityError("Embedding vectors cannot contain NaN or infinite values.")
    first_norm = math.sqrt(sum(value * value for value in first))
    second_norm = math.sqrt(sum(value * value for value in second))
    if first_norm == 0 or second_norm == 0:
        raise SimilarityError("Embedding vectors cannot have zero magnitude.")
    return max(-1.0, min(1.0, sum(a * b for a, b in zip(first, second)) / (first_norm * second_norm)))


def similarity_category(value: float) -> str:
    if value >= STRONG_SIMILARITY_THRESHOLD:
        return "strong"
    if value >= PARTIAL_SIMILARITY_THRESHOLD:
        return "partial"
    return "missing"


def _unique_requirements(items: list[SimilarityEmbeddingItem]) -> list[SimilarityEmbeddingItem]:
    result = []
    seen = set()
    for item in items:
        key = (item.text.strip(), tuple(item.embedding))
        if item.text.strip() and key not in seen:
            seen.add(key)
            result.append(item)
    return result


def analyze_similarity(
    resume_items: list[SimilarityEmbeddingItem],
    required_items: list[SimilarityEmbeddingItem],
    preferred_items: list[SimilarityEmbeddingItem],
) -> SimilarityResponse:
    resume = _unique_requirements(resume_items)
    matches: list[SimilarityMatch] = []
    for requirement_type, requirements in (("required", required_items), ("preferred", preferred_items)):
        for requirement in _unique_requirements(requirements):
            best: tuple[float, SimilarityEmbeddingItem] | None = None
            for candidate in resume:
                value = cosine_similarity(requirement.embedding, candidate.embedding)
                if best is None or value > best[0]:
                    best = (value, candidate)
            if best is None:
                matches.append(SimilarityMatch(requirement=requirement.text, requirement_type=requirement_type, similarity=0.0, category="missing"))
            else:
                value, candidate = best
                matches.append(SimilarityMatch(
                    requirement=requirement.text, requirement_type=requirement_type,
                    similarity=value, category=similarity_category(value), matched_text=candidate.text,
                    matched_source_type=candidate.source_type, matched_page_number=candidate.page_number,
                ))
    counts = {category: sum(match.category == category for match in matches) for category in ("strong", "partial", "missing")}
    return SimilarityResponse(
        matches=matches,
        summary=SimilaritySummary(required_count=len(_unique_requirements(required_items)), preferred_count=len(_unique_requirements(preferred_items)), **{f"{key}_count": value for key, value in counts.items()}),
    )
