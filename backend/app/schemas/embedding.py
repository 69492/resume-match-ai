from pydantic import BaseModel, Field, model_validator

from app.schemas.extraction import JobDescription, ResumeProfile

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384


class EmbeddingItem(BaseModel):
    source_type: str
    text: str
    embedding: list[float]


class EmbeddingResponse(BaseModel):
    model: str
    dimension: int = Field(..., ge=1)
    items: list[EmbeddingItem]


class EmbeddingRequest(BaseModel):
    resume: ResumeProfile | None = None
    job_description: JobDescription | None = None

    @model_validator(mode="after")
    def require_document(self):
        if self.resume is None and self.job_description is None:
            raise ValueError("Provide resume or job_description data.")
        return self
