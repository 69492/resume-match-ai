import re

from app.schemas.extraction import JobDescription, RequirementSource
from app.services.extraction_utils import sections, unique, vocabulary_matches
from app.services.pdf_service import ExtractedPage


_REQUIREMENT_CUE = re.compile(
    r"\b(?:must|required|requires|required to|need(?:s)? to|experience with|experience in|"
    r"proficien(?:t|cy) in|knowledge of|familiar(?:ity)? with|ability to|skilled in|"
    r"years? of experience|degree in|bachelor(?:'s)?|master(?:'s)?|responsible for|you will)\b",
    re.I,
)
_NOISE = re.compile(
    r"\b(?:equal opportunity|eeo|benefits?|compensation|salary|pay range|location|"
    r"apply(?: now| here)?|how to apply|send your resume|about (?:us|the company)|"
    r"we are an? |our company|privacy policy|visa sponsorship)\b",
    re.I,
)
_BULLET = re.compile(r"^(?:[•●▪◦*-]|\d+[.)])\s*")


def _clean(value: str) -> str:
    return " ".join(value.strip().split())


def _meaningful(line: str, *, section: str) -> bool:
    value = _clean(line)
    if not value or _NOISE.search(value):
        return False
    if len(value) < 3 or value.endswith(":"):
        return False
    return section in {"required", "preferred", "responsibilities", "experience", "education", "skills"} or bool(_REQUIREMENT_CUE.search(value))


def _source(items: list[tuple[str, int, str]], requirement_type: str) -> list[RequirementSource]:
    result: list[RequirementSource] = []
    seen: set[str] = set()
    for line, page, page_text in items:
        value = _clean(line)
        key = value.casefold()
        if value and key not in seen:
            seen.add(key)
            result.append(RequirementSource(text=value, page_number=page, source_text=page_text, requirement_type=requirement_type))
    return result


def _generic_requirement_items(grouped: dict[str, list[tuple[str, int, str]]]) -> list[tuple[str, int, str]]:
    """Retain unheaded requirement sentences without inventing skill names."""
    items = []
    for line, page, page_text in grouped.get("body", []):
        candidate = _BULLET.sub("", _clean(line))
        if _meaningful(candidate, section="body"):
            items.append((candidate, page, page_text))
    return items


def extract_job_description(pages: list[ExtractedPage], text: str) -> JobDescription:
    grouped = sections(pages)
    required_items = [item for key in ("required", "skills") for item in grouped.get(key, []) if _meaningful(item[0], section=key)]
    preferred_items = [item for item in grouped.get("preferred", []) if _meaningful(item[0], section="preferred")]
    responsibility_items = [item for item in grouped.get("responsibilities", []) if _meaningful(item[0], section="responsibilities")]
    experience_items = [item for item in grouped.get("experience", []) if _meaningful(item[0], section="experience")]
    education_items = [item for item in grouped.get("education", []) if _meaningful(item[0], section="education")]
    required_items.extend(_generic_requirement_items(grouped))

    required_sources = _source(required_items, "required")
    preferred_sources = _source(preferred_items, "preferred")
    responsibility_sources = _source(responsibility_items, "responsibility")
    experience_sources = _source(experience_items, "experience")
    education_sources = _source(education_items, "education")
    required_text = [item.text for item in required_sources]
    preferred_text = [item.text for item in preferred_sources]
    matches = vocabulary_matches(text)
    required_matches = vocabulary_matches("\n".join(required_text))
    preferred_matches = vocabulary_matches("\n".join(preferred_text))

    return JobDescription(
        text=text,
        required_skills=unique(required_text + sum(required_matches.values(), [])),
        preferred_skills=unique(preferred_text + sum(preferred_matches.values(), [])),
        programming_languages=matches["programming_languages"],
        frameworks=matches["frameworks"],
        tools=matches["tools"],
        databases=matches["databases"],
        cloud=matches["cloud"],
        experience_requirements=unique(item.text for item in experience_sources),
        education_requirements=unique(item.text for item in education_sources),
        responsibilities=unique(item.text for item in responsibility_sources),
        required_sources=required_sources,
        preferred_sources=preferred_sources,
        responsibility_sources=responsibility_sources,
        experience_requirement_sources=experience_sources,
        education_requirement_sources=education_sources,
    )
