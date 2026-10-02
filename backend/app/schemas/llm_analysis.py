from pydantic import BaseModel, Field

from app.schemas.extraction import JobDescription, ResumeProfile
from app.schemas.scoring import MatchScoreResponse
from app.schemas.similarity import SimilarityResponse


class AnalysisEvidence(BaseModel):
    text: str = Field(..., min_length=1)
    source_type: str | None = None
    page_number: int | None = Field(default=None, ge=1)


class AnalysisMatch(BaseModel):
    skill: str = Field(..., min_length=1)
    similarity: float = Field(..., ge=-1, le=1)
    evidence: str | AnalysisEvidence | None = None


class MissingSkill(BaseModel):
    skill: str = Field(..., min_length=1)


class RelevantProject(BaseModel):
    project: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=1)
    evidence: str | None = None


class LLMAnalysis(BaseModel):
    strong_matches: list[AnalysisMatch] = []
    partial_matches: list[AnalysisMatch] = []
    missing_skills: list[MissingSkill] = []
    relevant_projects: list[RelevantProject] = []
    recommendations: list[str] = []
    summary: str = ""


class AnalysisRequest(BaseModel):
    resume: ResumeProfile
    job_description: JobDescription
    similarity: SimilarityResponse
    score: MatchScoreResponse


class AnalysisScore(BaseModel):
    overall_score: float = Field(..., ge=0, le=100)
    score_label: str
    required_score: float = Field(..., ge=0, le=100)
    preferred_score: float = Field(..., ge=0, le=100)


class AnalysisResponse(BaseModel):
    score: AnalysisScore
    analysis: LLMAnalysis
