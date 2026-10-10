from app.schemas.llm_analysis import AnalysisRequest, AnalysisResponse, AnalysisScore, LLMAnalysis
from app.services.llm_service import LLMService
from app.services.match_normalization import match_key


class AnalysisValidationError(ValueError):
    pass


def _authoritative_matches(request: AnalysisRequest):
    return {match_key(match.requirement): match for match in request.similarity.matches}


def _sanitize_analysis(request: AnalysisRequest, analysis: LLMAnalysis) -> LLMAnalysis:
    """Keep only claims represented by Phase 5, repairing harmless label variants."""
    matches = _authoritative_matches(request)

    def valid_match(item, expected: str):
        source = matches.get(match_key(item.skill))
        if source is None:
            return None
        if source.category != expected:
            raise AnalysisValidationError(f"Unsupported {expected} match: {item.skill}")
        if abs(item.similarity - source.similarity) > 1e-6:
            raise AnalysisValidationError(f"Similarity changed for match: {item.skill}")
        return item.model_copy(update={"skill": source.requirement, "similarity": source.similarity})

    strong = []
    for item in analysis.strong_matches:
        repaired = valid_match(item, "strong")
        if repaired is None:
            raise AnalysisValidationError(f"Unsupported strong match: {item.skill}")
        strong.append(repaired)
    # An extra partial claim is safely discarded. It has no Phase 5 authority
    # and therefore cannot enter verification or affect the deterministic score.
    partial = [repaired for item in analysis.partial_matches if (repaired := valid_match(item, "partial")) is not None]
    missing = []
    for item in analysis.missing_skills:
        source = matches.get(match_key(item.skill))
        if source and source.category == "missing":
            missing.append(item.model_copy(update={"skill": source.requirement}))
        elif source is None:
            raise AnalysisValidationError(f"Unsupported missing skill: {item.skill}")
    projects = []
    project_keys = {match_key(project.name or project.text): project for project in request.resume.projects if (project.name or project.text).strip()}
    for item in analysis.relevant_projects:
        project = project_keys.get(match_key(item.project))
        if project:
            projects.append(item.model_copy(update={"project": project.name or project.text}))
        else:
            raise AnalysisValidationError(f"Unsupported project: {item.project}")
    return analysis.model_copy(update={
        "strong_matches": strong,
        "partial_matches": partial,
        "missing_skills": missing,
        "relevant_projects": projects,
    })


def generate_analysis(request: AnalysisRequest, llm_service: LLMService | None = None) -> AnalysisResponse:
    if not request.similarity.matches:
        raise AnalysisValidationError("Analysis requires at least one similarity result.")
    service = llm_service or LLMService()
    analysis = _sanitize_analysis(request, service.analyze_match(request))
    score = request.score
    return AnalysisResponse(
        score=AnalysisScore(
            overall_score=score.overall_score,
            score_label=score.score_label,
            required_score=score.required_score,
            preferred_score=score.preferred_score,
        ),
        analysis=analysis,
    )
