import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.similarity import SimilarityMatch, SimilarityResponse
from app.services.scoring_service import ScoringError, calculate_match_score

client = TestClient(app)


def match(requirement_type, similarity, category="partial"):
    return SimilarityMatch(
        requirement="requirement",
        requirement_type=requirement_type,
        similarity=similarity,
        category=category,
    )


def response(matches):
    return SimilarityResponse(
        matches=matches,
        summary={
            "required_count": sum(item.requirement_type == "required" for item in matches),
            "preferred_count": sum(item.requirement_type == "preferred" for item in matches),
            "strong_count": sum(item.category == "strong" for item in matches),
            "partial_count": sum(item.category == "partial" for item in matches),
            "missing_count": sum(item.category == "missing" for item in matches),
        },
    )


def test_exact_weighted_calculation():
    result = calculate_match_score(response([
        match("required", 0.90, "strong"), match("required", 0.80, "strong"),
        match("preferred", 0.60, "partial"), match("preferred", 0.70, "partial"),
    ]))
    assert result.required_score == pytest.approx(85.0)
    assert result.preferred_score == pytest.approx(65.0)
    assert result.overall_score == 81.0
    assert result.score_label == "Strong Match"


@pytest.mark.parametrize("matches, expected", [
    ([match("required", 0.8)], 80.0),
    ([match("preferred", 0.8)], 80.0),
    ([match("required", 1.0, "strong"), match("preferred", 1.0, "strong")], 100.0),
    ([match("required", -1.0, "missing")], 0.0),
])
def test_group_normalization_and_score_bounds(matches, expected):
    assert calculate_match_score(response(matches)).overall_score == expected


def test_counts_are_exposed_and_empty_input_is_rejected():
    result = calculate_match_score(response([
        match("required", 0.9, "strong"), match("required", 0.6, "partial"),
        match("preferred", -1.0, "missing"),
    ]))
    assert (result.required_count, result.preferred_count) == (2, 1)
    assert (result.strong_count, result.partial_count, result.missing_count) == (1, 1, 1)
    with pytest.raises(ScoringError):
        calculate_match_score(response([]))


def test_score_endpoint_accepts_phase_5_response():
    response = client.post("/api/score/analyze", json={
        "matches": [{"requirement": "Python", "requirement_type": "required", "similarity": 0.9, "category": "strong"}],
        "summary": {"required_count": 1, "preferred_count": 0, "strong_count": 1, "partial_count": 0, "missing_count": 0},
    })
    assert response.status_code == 200
    assert response.json()["overall_score"] == 90.0
