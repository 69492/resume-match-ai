from io import BytesIO

import fitz
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def pdf(text="Resume text"):
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    value = document.tobytes()
    document.close()
    return value


def test_pipeline_rejects_invalid_content_type_and_path_traversal_filename():
    response = client.post(
        "/api/analyze",
        files={"resume": ("../../secret.pdf", pdf(), "text/html"), "job_description": ("jd.pdf", pdf("Python"), "application/pdf")},
    )
    assert response.status_code == 400
    assert "PDF content" in response.json()["detail"]


def test_pipeline_rejects_empty_and_invalid_signature_uploads():
    response = client.post(
        "/api/analyze",
        files={"resume": ("resume.pdf", b"", "application/pdf"), "job_description": ("jd.pdf", pdf(), "application/pdf")},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"]

    response = client.post(
        "/api/analyze",
        files={"resume": ("resume.pdf", b"not a PDF", "application/pdf"), "job_description": ("jd.pdf", pdf(), "application/pdf")},
    )
    assert response.status_code == 400
    assert "valid PDF" in response.json()["detail"]


def test_unsupported_methods_and_cors_are_safe():
    assert client.get("/api/analyze").status_code == 405
    response = client.options("/api/analyze", headers={"Origin": "http://evil.example", "Access-Control-Request-Method": "POST"})
    assert response.headers.get("access-control-allow-origin") != "*"


def test_error_responses_do_not_expose_paths_or_credentials():
    response = client.post("/api/analyze", files={"resume": ("resume.txt", b"x", "text/plain"), "job_description": ("jd.pdf", pdf(), "application/pdf")})
    body = response.text
    assert "Traceback" not in body
    assert "C:\\Users" not in body
    assert "LLM_API_KEY" not in body


def test_html_in_document_is_data_not_executable_content():
    response = client.post("/api/documents/extract", files={"file": ("resume.pdf", pdf("<script>alert(1)</script>"), "application/pdf")})
    assert response.status_code == 200
    assert "<script>" in response.json()["text"]
