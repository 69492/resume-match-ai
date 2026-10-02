from io import BytesIO

import fitz
from fastapi.testclient import TestClient

from app.main import app
from app.services.pdf_service import clean_text

client = TestClient(app)


def make_pdf(*texts: str) -> bytes:
    document = fitz.open()
    for text in texts:
        page = document.new_page()
        page.insert_text((72, 72), text)
    data = document.tobytes()
    document.close()
    return data


def upload(data: bytes, filename: str = "resume.pdf", content_type: str = "application/pdf"):
    return client.post(
        "/api/documents/extract",
        files={"file": (filename, BytesIO(data), content_type)},
    )


def test_valid_text_pdf_extracts_text():
    response = upload(make_pdf("Jane Doe\nPython Developer"))
    assert response.status_code == 200
    assert response.json()["text"] == "Jane Doe\nPython Developer"


def test_empty_pdf_returns_ocr_message():
    document = fitz.open()
    document.new_page()
    data = document.tobytes()
    document.close()
    response = upload(data)
    assert response.status_code == 400
    assert "OCR is not implemented" in response.json()["detail"]


def test_non_pdf_upload_is_rejected():
    response = upload(b"not a pdf", "resume.txt", "text/plain")
    assert response.status_code == 400


def test_corrupted_pdf_is_rejected():
    response = upload(b"%PDF-1.7 corrupted", "resume.pdf")
    assert response.status_code == 400


def test_multiple_pages_and_page_numbers_are_preserved():
    response = upload(make_pdf("Page one", "Page two"))
    body = response.json()
    assert body["page_count"] == 2
    assert [(page["page_number"], page["text"]) for page in body["pages"]] == [
        (1, "Page one"),
        (2, "Page two"),
    ]
    assert body["text"] == "Page one\n\nPage two"


def test_whitespace_cleaning():
    assert clean_text("  Skills   \n\n\n\n  Python\t\t\n") == "Skills\n\nPython"
