from dataclasses import dataclass

from app.schemas.extraction import JobDescription, ResumeProfile


@dataclass(frozen=True)
class EmbeddingUnit:
    source_type: str
    text: str


def _clean_units(units: list[EmbeddingUnit]) -> list[EmbeddingUnit]:
    result: list[EmbeddingUnit] = []
    seen: set[str] = set()
    for unit in units:
        text = " ".join(unit.text.split())
        key = f"{unit.source_type}:{text}"
        if text and key not in seen:
            seen.add(key)
            result.append(EmbeddingUnit(unit.source_type, text))
    return result


def resume_embedding_units(profile: ResumeProfile) -> list[EmbeddingUnit]:
    units = [EmbeddingUnit("resume_skill", value) for value in profile.skills]
    units.extend(EmbeddingUnit("resume_experience", item.text) for item in profile.experience)
    units.extend(EmbeddingUnit("resume_project", item.text) for item in profile.projects)
    return _clean_units(units)


def job_description_embedding_units(job: JobDescription) -> list[EmbeddingUnit]:
    units = [EmbeddingUnit("jd_required_skill", value) for value in job.required_skills]
    units.extend(EmbeddingUnit("jd_preferred_skill", value) for value in job.preferred_skills)
    units.extend(EmbeddingUnit("jd_responsibility", value) for value in job.responsibilities)
    units.extend(EmbeddingUnit("jd_experience_requirement", value) for value in job.experience_requirements)
    return _clean_units(units)


def embedding_units(resume: ResumeProfile | None, job: JobDescription | None) -> list[EmbeddingUnit]:
    units = resume_embedding_units(resume) if resume else []
    if job:
        units.extend(job_description_embedding_units(job))
    return _clean_units(units)
