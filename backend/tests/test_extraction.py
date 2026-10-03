from io import BytesIO

import fitz
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def pdf(text: str) -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    data = document.tobytes()
    document.close()
    return data


def post(path: str, text: str, filename: str = "document.pdf"):
    return client.post(path, files={"file": (filename, BytesIO(pdf(text)), "application/pdf")})


def test_resume_extraction_is_structured_and_page_aware():
    response = post("/api/resume/extract", "Skills\nPython\nReact.js\nAWS\nExperience\nDeveloper")
    body = response.json()
    assert response.status_code == 200
    assert body["programming_languages"] == ["Python"]
    assert body["frameworks"] == ["React"]
    assert body["cloud"] == ["AWS"]
    assert body["experience"][0]["page_number"] == 1


def test_resume_missing_sections_are_empty_and_unsupported_skills_are_not_invented():
    body = post("/api/resume/extract", "Summary\nA thoughtful developer.").json()
    assert body["skills"] == []
    assert body["cloud"] == []
    assert body["projects"] == []


def test_resume_duplicates_and_capitalization_are_normalized():
    body = post("/api/resume/extract", "Skills\npython\nPython 3\nReact.js\nreact").json()
    assert body["skills"] == ["Python", "React"]


def test_resume_alternate_headings_are_supported():
    body = post("/api/resume/extract", "Technical Skills\nDocker\nWork Experience\nEngineer\nAcademic Background\nBSc").json()
    assert body["tools"] == ["Docker"]
    assert body["experience"][0]["text"] == "Engineer"
    assert body["education"][0]["text"] == "BSc"


def test_jd_required_and_preferred_skills_are_separated():
    body = post("/api/job-description/extract", "Required Skills\nPython\nFastAPI\nPreferred Skills\nAWS\nResponsibilities\nBuild APIs").json()
    assert "Python" in body["required_skills"]
    assert "FastAPI" in body["required_skills"]
    assert "AWS" in body["preferred_skills"]
    assert "AWS" not in body["required_skills"]
    assert body["responsibilities"] == ["Build APIs"]


def test_jd_missing_sections_and_empty_input_are_rejected_cleanly():
    body = post("/api/job-description/extract", "Role overview only").json()
    assert body["required_skills"] == []
    assert body["responsibilities"] == []
    response = client.post("/api/job-description/extract", files={"file": ("x.txt", b"", "text/plain")})
    assert response.status_code == 400


def test_jd_unknown_technology_is_preserved_with_source_metadata():
    body = post("/api/job-description/extract", "Required Skills\nExperience with Snowflake and Terraform\nPreferred Skills\nExperience with Datadog").json()
    assert any("Snowflake" in value for value in body["required_skills"])
    assert any("Datadog" in value for value in body["preferred_skills"])
    assert body["required_sources"][0]["page_number"] == 1
    assert "Snowflake" in body["required_sources"][0]["source_text"]


def test_jd_arbitrary_technical_requirement_is_not_dropped():
    body = post("/api/job-description/extract", "Technical Requirements\nDesign event-driven services using an internal message protocol and schema registry.").json()
    assert body["required_skills"] == ["Design event-driven services using an internal message protocol and schema registry."]


def test_jd_qualifications_and_preferred_sections_keep_classification():
    body = post("/api/job-description/extract", "Qualifications\nThree years building data pipelines.\nNice to Have\nExperience mentoring engineers.").json()
    assert body["required_skills"] == ["Three years building data pipelines."]
    assert body["preferred_skills"] == ["Experience mentoring engineers."]


def test_jd_responsibility_only_is_analyzable():
    body = post("/api/job-description/extract", "Responsibilities\nOwn the data quality program and coordinate incident response.").json()
    assert body["required_skills"] == []
    assert body["responsibilities"] == ["Own the data quality program and coordinate incident response."]


def test_jd_without_controlled_vocabulary_is_still_analyzable():
    body = post("/api/job-description/extract", "Must Have\nLead customer discovery workshops and document product decisions.").json()
    assert body["required_skills"] == ["Lead customer discovery workshops and document product decisions."]
    assert body["programming_languages"] == []


def test_non_pdf_resume_is_rejected():
    response = client.post("/api/resume/extract", files={"file": ("resume.txt", b"Python", "text/plain")})
    assert response.status_code == 400
