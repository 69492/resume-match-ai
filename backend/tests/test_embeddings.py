import math
import sys
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import embedding_service
from app.services.embedding_text_service import EmbeddingUnit, embedding_units

client = TestClient(app)


class FakeModel:
    def __init__(self, calls=None):
        self.calls = calls

    def embed(self, texts, batch_size=None):
        if self.calls is not None:
            self.calls.append((list(texts), batch_size))
        return ([1.0] * 384 for _ in texts)


def test_model_load_is_cached(monkeypatch):
    calls = []

    class FakeTextEmbedding:
        def __new__(cls, **kwargs):
            calls.append(kwargs)
            return object()

    monkeypatch.setitem(sys.modules, "fastembed", SimpleNamespace(TextEmbedding=FakeTextEmbedding))
    embedding_service.get_embedding_model.cache_clear()
    first = embedding_service.get_embedding_model()
    second = embedding_service.get_embedding_model()
    assert first is second
    assert len(calls) == 1
    assert calls[0]["providers"] == ["CPUExecutionProvider"]


def test_multiple_texts_are_batch_encoded_with_dimension_384(monkeypatch):
    calls = []
    monkeypatch.setattr(embedding_service, "get_embedding_model", lambda: FakeModel(calls))
    vectors = embedding_service.generate_embeddings([
        EmbeddingUnit("resume_skill", "Python"),
        EmbeddingUnit("resume_skill", "SQL"),
    ])
    assert len(vectors) == 2
    assert len(vectors[0]) == 384
    assert calls == [(["Python", "SQL"], 2)]
    assert math.sqrt(sum(value * value for value in vectors[0])) == pytest.approx(1.0)


def test_wrong_dimension_from_model_is_rejected(monkeypatch):
    class WrongModel:
        def embed(self, texts, batch_size=None):
            return ([1.0] * 3 for _ in texts)

    monkeypatch.setattr(embedding_service, "get_embedding_model", lambda: WrongModel())
    with pytest.raises(RuntimeError, match="dimension"):
        embedding_service.generate_embeddings([EmbeddingUnit("resume_skill", "Python")])


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
    assert body["model"] == "BAAI/bge-small-en-v1.5"
    assert body["dimension"] == 384
    assert body["items"][0]["source_type"] == "resume_skill"
    assert len(body["items"][0]["embedding"]) == 384


def test_empty_embedding_request_is_rejected():
    response = client.post("/api/embeddings/generate", json={"resume": {"skills": []}})
    assert response.status_code == 400
