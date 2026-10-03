from io import BytesIO

import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient
from app.main import app

from app.schemas.extraction import Experience, JobDescription, Project, ResumeProfile
from app.schemas.llm_analysis import LLMAnalysis
from app.services import analysis_pipeline_service as pipeline
from app.services.analysis_pipeline_service import AnalysisPipelineError, analyze_documents
from app.services.llm_service import LLMRateLimitError
from app.services.pdf_service import ExtractedDocument, ExtractedPage, PDFProcessingError
from app.services.similarity_service import SimilarityError
from app.schemas.verified_analysis import VerifiedAnalysis
from tests.test_llm_analysis import valid_response

client = TestClient(app)


def upload(name="document.pdf", content=b"%PDF-1.7 data"):
    return UploadFile(filename=name, file=BytesIO(content))


def documents():
    return ExtractedDocument(1, "Python SmartSeat", [ExtractedPage(1, "Python SmartSeat")])


def setup_success(monkeypatch):
    resume = ResumeProfile(
        text="Python SmartSeat", skills=["Python"],
        projects=[Project(text="SmartSeat", name="SmartSeat", source_text="SmartSeat", page_number=1)],
        experience=[Experience(text="Python", source_text="Python", page_number=1)],
    )
    job = JobDescription(text="Python", required_skills=["Python"])
    monkeypatch.setattr(pipeline, "extract_pdf_text", lambda _: documents())
    monkeypatch.setattr(pipeline, "extract_resume", lambda *_: resume)
    monkeypatch.setattr(pipeline, "extract_job_description", lambda *_: job)
    monkeypatch.setattr(pipeline, "generate_embeddings", lambda units: [[1.0, 0.0] for _ in units])
    return resume, job


class MockLLM:
    def analyze_match(self, request):
        return LLMAnalysis.model_validate({
            "strong_matches": [{"skill": "Python", "similarity": 1.0, "evidence": "Python"}],
            "partial_matches": [], "missing_skills": [],
            "relevant_projects": [{"project": "SmartSeat", "reason": "Project evidence", "evidence": "SmartSeat"}],
            "recommendations": [], "summary": "Strong Python alignment.",
        })


@pytest.mark.anyio
async def test_complete_pipeline_uses_each_stage_once_and_keeps_score_authoritative(monkeypatch):
    setup_success(monkeypatch)
    calls = {"similarity": 0, "score": 0, "verification": 0}
    original_similarity = pipeline.analyze_similarity
    original_score = pipeline.calculate_match_score
    original_verify = pipeline.verify_analysis

    def similarity(*args):
        calls["similarity"] += 1
        return original_similarity(*args)

    def score(value):
        calls["score"] += 1
        return original_score(value)

    def verify(value):
        calls["verification"] += 1
        return original_verify(value)

    monkeypatch.setattr(pipeline, "analyze_similarity", similarity)
    monkeypatch.setattr(pipeline, "calculate_match_score", score)
    monkeypatch.setattr(pipeline, "verify_analysis", verify)
    result = await analyze_documents(upload("resume.pdf"), upload("jd.pdf"), llm_service=MockLLM())
    assert result.score.overall_score == 100.0
    assert result.score.score_label == "Excellent Match"
    assert calls == {"similarity": 1, "score": 1, "verification": 1}


@pytest.mark.anyio
async def test_invalid_uploads_are_rejected_without_storage(monkeypatch):
    with pytest.raises(AnalysisPipelineError, match="must be a PDF"):
        await analyze_documents(upload("resume.txt"), upload("jd.pdf"))
    with pytest.raises(AnalysisPipelineError, match="empty"):
        await analyze_documents(upload("resume.pdf", b""), upload("jd.pdf"))


@pytest.mark.anyio
async def test_resume_and_jd_extraction_failures(monkeypatch):
    monkeypatch.setattr(pipeline, "extract_pdf_text", lambda _: (_ for _ in ()).throw(PDFProcessingError("bad PDF")))
    with pytest.raises(AnalysisPipelineError, match="Could not process the resume"):
        await analyze_documents(upload("resume.pdf"), upload("jd.pdf"))

    setup_success(monkeypatch)
    monkeypatch.setattr(pipeline, "extract_job_description", lambda *_: (_ for _ in ()).throw(ValueError("bad JD")))
    with pytest.raises(AnalysisPipelineError, match="extracted document data"):
        await analyze_documents(upload("resume.pdf"), upload("jd.pdf"), llm_service=MockLLM())


@pytest.mark.anyio
@pytest.mark.parametrize("stage, message", [("embedding", "embedding"), ("similarity", "Similarity analysis"), ("score", "Deterministic scoring")])
async def test_pipeline_stage_failures_are_safe(monkeypatch, stage, message):
    setup_success(monkeypatch)
    if stage == "embedding":
        monkeypatch.setattr(pipeline, "generate_embeddings", lambda _: (_ for _ in ()).throw(RuntimeError("embedding failure")))
    elif stage == "similarity":
        monkeypatch.setattr(pipeline, "analyze_similarity", lambda *_: (_ for _ in ()).throw(SimilarityError("similarity failure")))
    else:
        monkeypatch.setattr(pipeline, "calculate_match_score", lambda _: (_ for _ in ()).throw(pipeline.ScoringError("score failure")))
    with pytest.raises(AnalysisPipelineError, match=message):
        await analyze_documents(upload("resume.pdf"), upload("jd.pdf"), llm_service=MockLLM())


@pytest.mark.anyio
async def test_llm_failure_is_not_replaced_with_fake_analysis(monkeypatch):
    setup_success(monkeypatch)
    class FailingLLM:
        def analyze_match(self, request):
            raise RuntimeError("provider failure")
    with pytest.raises(RuntimeError, match="provider failure"):
        await analyze_documents(upload("resume.pdf"), upload("jd.pdf"), llm_service=FailingLLM())


def test_analyze_endpoint_validates_multipart_input():
    response = client.post(
        "/api/analyze",
        files={"resume": ("resume.txt", b"not pdf", "text/plain"), "job_description": ("jd.pdf", b"%PDF", "application/pdf")},
    )
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


def test_analyze_endpoint_returns_verified_result(monkeypatch):
    verified = VerifiedAnalysis.model_validate({
        "score": {"overall_score": 100, "score_label": "Excellent Match", "required_score": 100, "preferred_score": 0, "required_weight": 0.8, "preferred_weight": 0.2, "required_count": 1, "preferred_count": 0, "strong_count": 1, "partial_count": 0, "missing_count": 0},
        "strong_matches": [], "partial_matches": [], "missing_skills": [], "relevant_projects": [],
        "recommendations": [], "summary": "", "summary_status": "verified",
        "validation_summary": {"total_claims": 0, "verified_claims": 0, "corrected_claims": 0, "rejected_claims": 0},
    })

    async def fake_pipeline(*args, **kwargs):
        return verified

    monkeypatch.setattr("app.api.routes.pipeline.analyze_documents", fake_pipeline)
    response = client.post(
        "/api/analyze",
        files={"resume": ("resume.pdf", b"%PDF", "application/pdf"), "job_description": ("jd.pdf", b"%PDF", "application/pdf")},
    )
    assert response.status_code == 200
    assert response.json()["score"]["overall_score"] == 100


def test_analyze_endpoint_returns_429_for_exhausted_llm_rate_limit(monkeypatch):
    async def rate_limited(*args, **kwargs):
        raise LLMRateLimitError(retry_after=7)

    monkeypatch.setattr("app.api.routes.pipeline.analyze_documents", rate_limited)
    response = client.post(
        "/api/analyze",
        files={"resume": ("resume.pdf", b"%PDF", "application/pdf"), "job_description": ("jd.pdf", b"%PDF", "application/pdf")},
    )
    assert response.status_code == 429
    assert response.headers["retry-after"] == "7"
    assert "rate limit" in response.json()["detail"]
