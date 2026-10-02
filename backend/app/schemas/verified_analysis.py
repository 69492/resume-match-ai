from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.extraction import JobDescription, ResumeProfile
from app.schemas.llm_analysis import LLMAnalysis
from app.schemas.scoring import MatchScoreResponse
from app.schemas.similarity import SimilarityResponse

ValidationStatus = Literal["verified", "corrected", "rejected"]


class EvidenceItem(BaseModel):
    text: str | None = None
    source_type: str | None = None
    page_number: int | None = Field(default=None, ge=1)
    verified: bool = False
    confidence: float = Field(default=0.0, ge=0, le=1)
    status: ValidationStatus = "rejected"


class VerifiedMatch(BaseModel):
    skill: str
    similarity: float = Field(..., ge=-1, le=1)
    evidence: EvidenceItem
    status: ValidationStatus


class VerifiedMissingSkill(BaseModel):
    skill: str
    verified: bool
    status: ValidationStatus


class VerifiedProject(BaseModel):
    project: str
    evidence: EvidenceItem
    status: ValidationStatus


class VerifiedRecommendation(BaseModel):
    text: str
    grounded_in: str
    status: ValidationStatus


class ValidationSummary(BaseModel):
    total_claims: int = Field(..., ge=0)
    verified_claims: int = Field(..., ge=0)
    corrected_claims: int = Field(..., ge=0)
    rejected_claims: int = Field(..., ge=0)


class VerifiedAnalysis(BaseModel):
    score: MatchScoreResponse
    strong_matches: list[VerifiedMatch] = []
    partial_matches: list[VerifiedMatch] = []
    missing_skills: list[VerifiedMissingSkill] = []
    relevant_projects: list[VerifiedProject] = []
    recommendations: list[VerifiedRecommendation] = []
    summary: str = ""
    summary_status: ValidationStatus = "verified"
    validation_summary: ValidationSummary


class EvidenceVerificationRequest(BaseModel):
    resume: ResumeProfile
    job_description: JobDescription
    similarity: SimilarityResponse
    score: MatchScoreResponse
    analysis: LLMAnalysis
