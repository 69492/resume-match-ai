import math

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.similarity_service import SimilarityError, cosine_similarity

client = TestClient(app)


def item(text, vector, source="resume_skill", page=None):
    value = {"text": text, "embedding": vector, "source_type": source}
    if page:
        value["page_number"] = page
    return value


def test_cosine_similarity_basic_vectors():
    assert cosine_similarity([1, 0], [1, 0]) == pytest.approx(1)
    assert cosine_similarity([1, 0], [0, 1]) == pytest.approx(0)
    assert cosine_similarity([1, 0], [-1, 0]) == pytest.approx(-1)


@pytest.mark.parametrize("first, second, message", [
    ([1], [1, 2], "equal dimensions"),
    ([], [1], "non-empty"),
    ([math.nan], [1], "NaN"),
    ([math.inf], [1], "NaN or infinite"),
])
def test_invalid_vectors_raise_clear_errors(first, second, message):
    with pytest.raises(SimilarityError, match=message):
        cosine_similarity(first, second)


def test_best_match_thresholds_and_source_page_are_preserved():
    response = client.post("/api/similarity/analyze", json={
        "resume_items": [item("weak", [0.6, 0.8], page=1), item("best", [1, 0], page=2)],
        "required_items": [item("Python", [1, 0], "jd_required")],
        "preferred_items": [item("Cloud", [0.8, 0.6], "jd_preferred")],
    })
    body = response.json()
    assert response.status_code == 200
    assert body["matches"][0]["matched_text"] == "best"
    assert body["matches"][0]["category"] == "strong"
    assert body["matches"][0]["matched_page_number"] == 2
    assert body["matches"][1]["requirement_type"] == "preferred"


def test_partial_and_missing_thresholds():
    response = client.post("/api/similarity/analyze", json={
        "resume_items": [item("partial", [1, 0], page=1)],
        "required_items": [item("partial req", [0.7, 0.714142]), item("missing req", [-1, 0])],
    })
    categories = [match["category"] for match in response.json()["matches"]]
    assert categories == ["partial", "missing"]


def test_duplicates_and_empty_resume_are_handled():
    response = client.post("/api/similarity/analyze", json={
        "resume_items": [],
        "required_items": [item("Python", [1, 0]), item("Python", [1, 0])],
    })
    body = response.json()
    assert response.status_code == 200
    assert len(body["matches"]) == 1
    assert body["matches"][0]["matched_text"] is None
    assert body["summary"]["missing_count"] == 1
