from app.schemas.extraction import JobDescription
from app.services.extraction_utils import sections, unique, vocabulary_matches
from app.services.pdf_service import ExtractedPage


def extract_job_description(pages: list[ExtractedPage], text: str) -> JobDescription:
    grouped = sections(pages)
    matches = vocabulary_matches(text)
    required_text = [line for line, _, _ in grouped.get("required", [])]
    preferred_text = [line for line, _, _ in grouped.get("preferred", [])]
    required_matches = vocabulary_matches("\n".join(required_text))
    preferred_matches = vocabulary_matches("\n".join(preferred_text))
    required = unique(required_text + sum(required_matches.values(), []))
    preferred = unique(preferred_text + sum(preferred_matches.values(), []))
    return JobDescription(
        text=text,
        required_skills=required,
        preferred_skills=preferred,
        programming_languages=matches["programming_languages"],
        frameworks=matches["frameworks"],
        tools=matches["tools"],
        databases=matches["databases"],
        cloud=matches["cloud"],
        experience_requirements=unique(line for line, _, _ in grouped.get("experience", [])),
        education_requirements=unique(line for line, _, _ in grouped.get("education", [])),
        responsibilities=unique(line for line, _, _ in grouped.get("responsibilities", [])),
    )
