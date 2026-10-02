from fastapi.testclient import TestClient

from app.main import app
from app.schemas.llm_analysis import LLMAnalysis
from app.schemas.verified_analysis import EvidenceVerificationRequest
from app.services.evidence_service import verify_analysis
from tests.test_llm_analysis import request, valid_response

client = TestClient(app)


def verification(analysis=None):
    value = valid_response() if analysis is None else analysis
    return EvidenceVerificationRequest(
        resume=request().resume,
        job_description=request().job_description,
        similarity=request().similarity,
        score=request().score,
        analysis=LLMAnalysis.model_validate(value),
    )


def test_valid_skill_evidence_and_project_are_verified():
    result = verify_analysis(verification())
    assert result.strong_matches[0].status == "verified"
    assert result.strong_matches[0].evidence.verified is True
    assert result.relevant_projects[0].status == "verified"
    assert result.relevant_projects[0].evidence.source_type == "resume_project"


def test_minor_formatting_difference_is_corrected_to_authoritative_evidence():
    value = valid_response()
    value["strong_matches"][0]["evidence"] = "Built Python APIs."
    result = verify_analysis(verification(value))
    assert result.strong_matches[0].status == "verified"
    assert result.strong_matches[0].evidence.text == "Built Python APIs"


def test_unsupported_skill_and_project_are_rejected():
    value = valid_response()
    value["strong_matches"] = [{"skill": "Docker", "similarity": 0.9, "evidence": "Used Docker"}]
    value["relevant_projects"] = [{"project": "Invented Project", "reason": "It is relevant"}]
    result = verify_analysis(verification(value))
    assert result.strong_matches[0].status == "rejected"
    assert result.relevant_projects[0].status == "rejected"


def test_similarity_and_category_mismatch_use_authoritative_values():
    value = valid_response()
    value["strong_matches"][0]["similarity"] = 0.99
    value["strong_matches"][0]["evidence"] = "Built Python APIs"
    result = verify_analysis(verification(value))
    assert result.strong_matches[0].similarity == 0.9
    assert result.strong_matches[0].status == "corrected"

    value = valid_response()
    value["strong_matches"] = []
    value["partial_matches"] = [{"skill": "Python", "similarity": 0.9, "evidence": "Built Python APIs"}]
    result = verify_analysis(verification(value))
    assert result.partial_matches[0].status == "corrected"
    assert result.partial_matches[0].similarity == 0.9


def test_missing_skill_validation_and_fake_page_number():
    value = valid_response()
    value["missing_skills"] = [{"skill": "Python"}]
    result = verify_analysis(verification(value))
    assert result.missing_skills[0].status == "corrected"

    value = valid_response()
    value["strong_matches"][0]["evidence"] = {"text": "Built Python APIs", "page_number": 99}
    result = verify_analysis(verification(value))
    assert result.strong_matches[0].evidence.page_number is None
    assert result.strong_matches[0].evidence.status == "corrected"


def test_unsupported_claim_recommendation_and_summary_are_rejected():
    value = valid_response()
    value["recommendations"] = ["You already have extensive AWS experience."]
    value["summary"] = "The candidate has five years of AWS experience."
    result = verify_analysis(verification(value))
    assert result.recommendations[0].status == "rejected"
    assert result.summary_status == "rejected"
    assert result.summary == ""


def test_validation_counts_and_score_authority():
    value = valid_response()
    value["relevant_projects"] = [{"project": "Nope", "reason": "invented"}]
    result = verify_analysis(verification(value))
    report = result.validation_summary
    assert report.total_claims == report.verified_claims + report.corrected_claims + report.rejected_claims
    assert report.rejected_claims >= 1
    assert result.score.overall_score == 76.0


def test_verification_endpoint():
    payload = verification().model_dump(mode="json")
    response = client.post("/api/analysis/verify", json=payload)
    assert response.status_code == 200
    assert response.json()["score"]["overall_score"] == 76.0
