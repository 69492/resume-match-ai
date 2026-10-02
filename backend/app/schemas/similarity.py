from typing import Literal

from pydantic import BaseModel, Field, model_validator


class SimilarityEmbeddingItem(BaseModel):
    text: str
    embedding: list[float]
    source_type: str
    page_number: int | None = Field(default=None, ge=1)


class SimilarityRequest(BaseModel):
    resume_items: list[SimilarityEmbeddingItem] = []
    required_items: list[SimilarityEmbeddingItem] = []
    preferred_items: list[SimilarityEmbeddingItem] = []


class SimilarityMatch(BaseModel):
    requirement: str
    requirement_type: Literal["required", "preferred"]
    similarity: float = Field(..., ge=-1, le=1)
    category: Literal["strong", "partial", "missing"]
    matched_text: str | None = None
    matched_source_type: str | None = None
    matched_page_number: int | None = None


class SimilaritySummary(BaseModel):
    required_count: int
    preferred_count: int
    strong_count: int
    partial_count: int
    missing_count: int


class SimilarityResponse(BaseModel):
    matches: list[SimilarityMatch]
    summary: SimilaritySummary
