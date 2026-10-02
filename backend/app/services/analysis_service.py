from app.schemas.llm_analysis import AnalysisRequest, AnalysisResponse, AnalysisScore, LLMAnalysis
from app.services.llm_service import LLMService


class AnalysisValidationError(ValueError):
    pass


def _key(value: str) -> str:
    return " ".join(value.casefold().split())


def _validate_business_rules(request: AnalysisRequest, analysis: LLMAnalysis) -> None:
    matches = {_key(match.requirement): match for match in request.similarity.matches}
    for item in [*analysis.strong_matches, *analysis.partial_matches]:
        source = matches.get(_key(item.skill))
        expected = "strong" if item in analysis.strong_matches else "partial"
        if source is None or source.category != expected:
            raise AnalysisValidationError(f"Unsupported {expected} match: {item.skill}")
        if abs(item.similarity - source.similarity) > 1e-6:
            raise AnalysisValidationError(f"Similarity changed for match: {item.skill}")
    for item in analysis.missing_skills:
        source = matches.get(_key(item.skill))
        if source is None or source.category != "missing":
            raise AnalysisValidationError(f"Unsupported missing skill: {item.skill}")

    projects = {
        _key(project.name or project.text)
        for project in request.resume.projects
        if (project.name or project.text).strip()
    }
    for item in analysis.relevant_projects:
        if _key(item.project) not in projects:
            raise AnalysisValidationError(f"Unsupported project: {item.project}")


def generate_analysis(request: AnalysisRequest, llm_service: LLMService | None = None) -> AnalysisResponse:
    if not request.similarity.matches:
        raise AnalysisValidationError("Analysis requires at least one similarity result.")
    service = llm_service or LLMService()
    analysis = service.analyze_match(request)
    _validate_business_rules(request, analysis)
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
