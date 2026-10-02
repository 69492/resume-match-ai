import re
from collections.abc import Iterable

from app.services.pdf_service import ExtractedPage

HEADING_ALIASES = {
    "skills": {"skills", "technical skills", "core skills"},
    "programming_languages": {"programming languages", "languages"},
    "frameworks": {"frameworks", "frameworks and libraries"},
    "tools": {"tools", "software", "technologies"},
    "experience": {"experience", "work experience", "professional experience", "employment"},
    "projects": {"projects", "personal projects", "academic projects"},
    "education": {"education", "academic background"},
    "certifications": {"certifications", "certificates"},
    "required": {"requirements", "required qualifications", "required skills", "must have"},
    "preferred": {"preferred qualifications", "preferred skills", "nice to have"},
    "responsibilities": {"responsibilities", "what you'll do", "duties"},
    "technologies": {"technologies", "technology stack"},
}

SKILL_GROUPS = {
    "programming_languages": ["Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Ruby", "PHP", "SQL"],
    "frameworks": ["FastAPI", "Django", "Flask", "React", "Angular", "Vue", "Spring", ".NET", "Node.js"],
    "libraries": ["Pandas", "NumPy", "TensorFlow", "PyTorch", " scikit-learn"],
    "tools": ["Git", "Docker", "Kubernetes", "Jenkins", "Linux", "Postman"],
    "databases": ["PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Oracle"],
    "cloud": ["AWS", "Azure", "Google Cloud", "GCP", "Heroku"],
}

CANONICAL = {"python 3": "Python", "react.js": "React", "reactjs": "React", "postgres": "PostgreSQL", "gcp": "GCP"}


def normalize_lines(text: str) -> list[str]:
    return [line.strip(" •\t-") for line in text.replace("\r", "").split("\n") if line.strip()]


def sections(pages: list[ExtractedPage]) -> dict[str, list[tuple[str, int, str]]]:
    found: dict[str, list[tuple[str, int, str]]] = {}
    current = "body"
    for page in pages:
        for line in normalize_lines(page.text):
            key = next((key for key, aliases in HEADING_ALIASES.items() if line.lower().rstrip(":") in aliases), None)
            if key:
                current = key
                continue
            found.setdefault(current, []).append((line, page.page_number, page.text))
    return found


def unique(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        lowered = value.lower().strip()
        canonical = CANONICAL.get(lowered, value)
        for term in sum(SKILL_GROUPS.values(), []):
            if lowered == term.lower() or lowered == f"{term.lower()} 3":
                canonical = term.strip()
                break
        if canonical.lower() not in seen:
            seen.add(canonical.lower())
            result.append(canonical)
    return result


def vocabulary_matches(text: str) -> dict[str, list[str]]:
    result = {}
    for group, terms in SKILL_GROUPS.items():
        result[group] = unique(term for term in terms if re.search(r"(?<!\w)" + re.escape(term.strip()) + r"(?!\w)", text, re.I))
    return result
