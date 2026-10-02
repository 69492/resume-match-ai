from app.schemas.extraction import Certification, Education, Experience, Project, ResumeProfile
from app.services.extraction_utils import sections, unique, vocabulary_matches
from app.services.pdf_service import ExtractedPage


def extract_resume(pages: list[ExtractedPage], text: str) -> ResumeProfile:
    grouped = sections(pages)
    matches = vocabulary_matches(text)
    skills = unique([line for line, _, _ in grouped.get("skills", [])] + sum(matches.values(), []))

    def source_items(key: str) -> list[tuple[str, int, str]]:
        return grouped.get(key, [])

    return ResumeProfile(
        text=text,
        skills=skills,
        programming_languages=matches["programming_languages"],
        frameworks=matches["frameworks"],
        libraries=matches["libraries"],
        tools=matches["tools"],
        databases=matches["databases"],
        cloud=matches["cloud"],
        experience=[Experience(text=x, page_number=p, source_text=s) for x, p, s in source_items("experience")],
        projects=[Project(text=x, name=x, page_number=p, source_text=s) for x, p, s in source_items("projects")],
        education=[Education(text=x, degree=x, page_number=p, source_text=s) for x, p, s in source_items("education")],
        certifications=[Certification(text=x, name=x, page_number=p, source_text=s) for x, p, s in source_items("certifications")],
    )
