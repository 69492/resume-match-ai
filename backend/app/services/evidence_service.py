import re
from difflib import SequenceMatcher

from app.schemas.llm_analysis import AnalysisEvidence, AnalysisMatch, LLMAnalysis
from app.schemas.similarity import SimilarityMatch, SimilarityResponse
from app.schemas.verified_analysis import (
    EvidenceItem,
    EvidenceVerificationRequest,
    ValidationSummary,
    VerifiedAnalysis,
    VerifiedMatch,
    VerifiedMissingSkill,
    VerifiedProject,
    VerifiedRecommendation,
)


def _key(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))


def _tokens(value: str) -> set[str]:
    return set(_key(value).split())


def _text_similarity(first: str, second: str) -> float:
    first_key, second_key = _key(first), _key(second)
    if not first_key or not second_key:
        return 0.0
    overlap = len(_tokens(first) & _tokens(second)) / max(1, len(_tokens(first)))
    sequence = SequenceMatcher(None, first_key, second_key).ratio()
    return max(overlap, sequence)


def _source_items(request: EvidenceVerificationRequest) -> list[tuple[str, str | None, int | None]]:
    resume = request.resume
    sources: list[tuple[str, str | None, int | None]] = []
    if resume.text.strip():
        sources.append((resume.text, "resume_document", None))
    for text in resume.skills + resume.programming_languages + resume.frameworks + resume.libraries + resume.tools + resume.databases + resume.cloud:
        sources.append((text, "resume_skill", None))
    for collection, source_type in (
        (resume.experience, "resume_experience"),
        (resume.projects, "resume_project"),
        (resume.education, "resume_education"),
        (resume.certifications, "resume_certification"),
    ):
        for item in collection:
            sources.append((item.source_text or item.text or getattr(item, "name", None) or "", source_type, item.page_number))
            if item.text and item.text != (item.source_text or ""):
                sources.append((item.text, source_type, item.page_number))
    return [(text, source_type, page) for text, source_type, page in sources if text.strip()]


def _similarity_map(similarity: SimilarityResponse) -> dict[str, SimilarityMatch]:
    return {_key(item.requirement): item for item in similarity.matches}


def _evidence(
    claim: str | AnalysisEvidence | None,
    authoritative: SimilarityMatch | None,
    sources: list[tuple[str, str | None, int | None]],
) -> EvidenceItem:
    if not claim:
        if authoritative and authoritative.matched_text:
            return EvidenceItem(
                text=authoritative.matched_text,
                source_type=authoritative.matched_source_type,
                page_number=authoritative.matched_page_number,
                verified=True,
                confidence=1.0,
                status="verified",
            )
        return EvidenceItem()

    claim_text = claim.text if isinstance(claim, AnalysisEvidence) else claim
    candidates = sources
    if authoritative and authoritative.matched_text:
        candidates = [(authoritative.matched_text, authoritative.matched_source_type, authoritative.matched_page_number), *sources]
    best = max(candidates, key=lambda item: _text_similarity(claim_text, item[0]), default=None)
    confidence = _text_similarity(claim_text, best[0]) if best else 0.0
    if best and confidence >= 0.72:
        status = "verified" if _key(claim_text) == _key(best[0]) else "corrected"
        if isinstance(claim, AnalysisEvidence) and (claim.page_number != best[2] or (claim.source_type and claim.source_type != best[1])):
            status = "corrected"
        return EvidenceItem(text=best[0], source_type=best[1], page_number=best[2], verified=True, confidence=confidence, status=status)
    return EvidenceItem(text=None, verified=False, confidence=confidence, status="rejected")


def _match_claim(item: AnalysisMatch, expected_category: str, matches: dict[str, SimilarityMatch], sources: list[tuple[str, str | None, int | None]]) -> VerifiedMatch:
    authoritative = matches.get(_key(item.skill))
    if authoritative is None:
        return VerifiedMatch(skill=item.skill, similarity=item.similarity, evidence=EvidenceItem(), status="rejected")
    category_status = "verified" if authoritative.category == expected_category else "corrected"
    similarity_status = "corrected" if abs(item.similarity - authoritative.similarity) > 1e-6 else category_status
    evidence = _evidence(item.evidence, authoritative, sources)
    status = "rejected" if evidence.status == "rejected" else similarity_status
    return VerifiedMatch(skill=authoritative.requirement, similarity=authoritative.similarity, evidence=evidence, status=status)


def _recommendation(text: str, missing: set[str], partial: set[str]) -> VerifiedRecommendation:
    lower = text.casefold()
    target = next((skill for skill in [*missing, *partial] if skill in lower), None)
    unsupported_claim = any(phrase in lower for phrase in ("already have", "already work", "years of", "extensive experience"))
    if target and not unsupported_claim:
        basis = "missing JD requirement" if target in missing else "partial JD requirement"
        return VerifiedRecommendation(text=text, grounded_in=f"{target} is a {basis}.", status="verified")
    return VerifiedRecommendation(text=text, grounded_in="", status="rejected")


def _summary_status(summary: str, missing: set[str], resume_text: str) -> str:
    lower = summary.casefold()
    for skill in missing:
        if re.search(rf"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+years?.{{0,35}}\b{re.escape(skill)}\b", lower):
            return "rejected"
        if re.search(rf"\b{re.escape(skill)}\b.{{0,25}}(?:experience|expertise|worked extensively)", lower):
            return "rejected"
    # A summary may interpret known data, but it cannot assert a named missing skill.
    return "verified" if summary.strip() else "verified"


def verify_analysis(request: EvidenceVerificationRequest) -> VerifiedAnalysis:
    matches = _similarity_map(request.similarity)
    sources = _source_items(request)
    counts = {"verified": 0, "corrected": 0, "rejected": 0}

    def count(status: str) -> None:
        counts[status] += 1

    strong: list[VerifiedMatch] = []
    for item in request.analysis.strong_matches:
        result = _match_claim(item, "strong", matches, sources)
        strong.append(result)
        count(result.status)
    partial: list[VerifiedMatch] = []
    for item in request.analysis.partial_matches:
        result = _match_claim(item, "partial", matches, sources)
        partial.append(result)
        count(result.status)

    missing: list[VerifiedMissingSkill] = []
    for item in request.analysis.missing_skills:
        authoritative = matches.get(_key(item.skill))
        if authoritative and authoritative.category == "missing":
            result = VerifiedMissingSkill(skill=authoritative.requirement, verified=True, status="verified")
        elif authoritative:
            result = VerifiedMissingSkill(skill=authoritative.requirement, verified=True, status="corrected")
        else:
            result = VerifiedMissingSkill(skill=item.skill, verified=False, status="rejected")
        missing.append(result)
        count(result.status)

    projects: list[VerifiedProject] = []
    project_map = {_key(project.name or project.text): project for project in request.resume.projects}
    for item in request.analysis.relevant_projects:
        project = project_map.get(_key(item.project))
        if project:
            source = project.source_text or project.text
            evidence = _evidence(item.evidence or project.text, None, [(source, "resume_project", project.page_number)])
            result = VerifiedProject(project=project.name or project.text, evidence=evidence, status="verified" if evidence.verified else "rejected")
        else:
            result = VerifiedProject(project=item.project, evidence=EvidenceItem(), status="rejected")
        projects.append(result)
        count(result.status)

    missing_keys = {_key(item.skill) for item in missing if item.status != "rejected"}
    partial_keys = {_key(item.skill) for item in partial if item.status != "rejected"}
    recommendations = []
    for item in request.analysis.recommendations:
        result = _recommendation(item, missing_keys, partial_keys)
        recommendations.append(result)
        count(result.status)

    summary_status = _summary_status(request.analysis.summary, missing_keys, request.resume.text)
    count(summary_status)
    return VerifiedAnalysis(
        score=request.score,
        strong_matches=strong,
        partial_matches=partial,
        missing_skills=missing,
        relevant_projects=projects,
        recommendations=recommendations,
        summary=request.analysis.summary if summary_status == "verified" else "",
        summary_status=summary_status,
        validation_summary=ValidationSummary(
            total_claims=sum(counts.values()),
            verified_claims=counts["verified"],
            corrected_claims=counts["corrected"],
            rejected_claims=counts["rejected"],
        ),
    )
