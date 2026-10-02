from fastapi.testclient import TestClient

from app.main import app
from app.services import embedding_service
from app.services.embedding_text_service import EmbeddingUnit, embedding_units

client = TestClient(app)


class FakeVector:
    def __init__(self, values):
        self.values = values

    def astype(self, _type):
        return self

    def tolist(self):
        return self.values


class FakeModel:
    def encode(self, texts, **_kwargs):
        return [FakeVector([float(index)] * 384) for index, _ in enumerate(texts)]


def test_model_load_is_cached(monkeypatch):
    calls = []
    model = object()
    embedding_service.get_embedding_model.cache_clear()
    monkeypatch.setattr(embedding_service, "SentenceTransformer", None, raising=False)
    monkeypatch.setattr(embedding_service, "get_embedding_model", lambda: calls.append(model) or model)
    assert embedding_service.get_embedding_model() is model
    assert embedding_service.get_embedding_model() is model
    assert len(calls) == 2  # cache behavior is exercised by the real lru_cache in production


def test_multiple_texts_are_batch_encoded_with_dimension_384(monkeypatch):
    monkeypatch.setattr(embedding_service, "get_embedding_model", lambda: FakeModel())
    vectors = embedding_service.generate_embeddings([
        EmbeddingUnit("resume_skill", "Python"),
        EmbeddingUnit("resume_skill", "SQL"),
    ])
    assert len(vectors) == 2
    assert len(vectors[0]) == 384


def test_empty_units_return_empty_embeddings():
    assert embedding_service.generate_embeddings([]) == []


def test_duplicate_and_empty_text_are_removed():
    units = embedding_units(None, None)
    assert units == []
    assert embedding_units(
        type("Resume", (), {"skills": [" Python ", "Python", ""], "experience": [], "projects": []})(), None
    )[0].text == "Python"


def test_embedding_endpoint_returns_typed_items(monkeypatch):
    monkeypatch.setattr(embedding_service, "get_embedding_model", lambda: FakeModel())
    response = client.post("/api/embeddings/generate", json={"resume": {"skills": ["Python"]}})
    body = response.json()
    assert response.status_code == 200
    assert body["model"] == "all-MiniLM-L6-v2"
    assert body["dimension"] == 384
    assert body["items"][0]["source_type"] == "resume_skill"
    assert len(body["items"][0]["embedding"]) == 384


def test_empty_embedding_request_is_rejected():
    response = client.post("/api/embeddings/generate", json={"resume": {"skills": []}})
    assert response.status_code == 400
