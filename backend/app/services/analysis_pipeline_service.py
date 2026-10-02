from fastapi import UploadFile

from app.core.config import MAX_PDF_SIZE_BYTES
from app.schemas.embedding import EmbeddingItem
from app.schemas.extraction import JobDescription, ResumeProfile
from app.schemas.llm_analysis import AnalysisRequest
from app.schemas.scoring import MatchScoreResponse
from app.schemas.similarity import SimilarityEmbeddingItem, SimilarityResponse
from app.schemas.verified_analysis import EvidenceVerificationRequest, VerifiedAnalysis
from app.services.analysis_service import generate_analysis
from app.services.embedding_service import generate_embeddings
from app.services.embedding_text_service import embedding_units
from app.services.evidence_service import verify_analysis
from app.services.jd_extraction_service import extract_job_description
from app.services.pdf_service import ExtractedDocument, PDFProcessingError, extract_pdf_text
from app.services.resume_extraction_service import extract_resume
from app.services.scoring_service import ScoringError, calculate_match_score
from app.services.similarity_service import SimilarityError, analyze_similarity


class AnalysisPipelineError(ValueError):
    """Safe, user-facing failure from the end-to-end analysis pipeline."""


async def _read_upload(file: UploadFile, label: str) -> ExtractedDocument:
    filename = file.filename or "uploaded.pdf"
    if not filename.lower().endswith(".pdf"):
        raise AnalysisPipelineError(f"The {label} must be a PDF file.")
    if file.content_type not in (None, "application/pdf", "application/octet-stream"):
        raise AnalysisPipelineError(f"The {label} must have PDF content.")
    data = await file.read(MAX_PDF_SIZE_BYTES + 1)
    if not data:
        raise AnalysisPipelineError(f"The {label} is empty.")
    if len(data) > MAX_PDF_SIZE_BYTES:
        raise AnalysisPipelineError(f"The {label} exceeds the configured size limit.")
    try:
        return extract_pdf_text(data)
    except PDFProcessingError as exc:
        raise AnalysisPipelineError(f"Could not process the {label}: {exc}") from exc


def _embedding_items(units, vectors: list[list[float]]) -> list[EmbeddingItem]:
    return [EmbeddingItem(source_type=unit.source_type, text=unit.text, embedding=vector) for unit, vector in zip(units, vectors)]


def _similarity_inputs(items: list[EmbeddingItem]) -> tuple[list[SimilarityEmbeddingItem], list[SimilarityEmbeddingItem], list[SimilarityEmbeddingItem]]:
    resume = [item for item in items if item.source_type.startswith("resume_")]
    required = [item for item in items if item.source_type.startswith("jd_required")]
    preferred = [item for item in items if item.source_type.startswith("jd_preferred")]
    def convert(group):
        return [SimilarityEmbeddingItem(text=item.text, embedding=item.embedding, source_type=item.source_type) for item in group]
    return (
        convert(resume), convert(required), convert(preferred),
    )


async def analyze_documents(resume_file: UploadFile, jd_file: UploadFile, llm_service=None) -> VerifiedAnalysis:
    resume_document, jd_document = await _read_upload(resume_file, "resume") , await _read_upload(jd_file, "job description")
    try:
        resume: ResumeProfile = extract_resume(resume_document.pages, resume_document.text)
        job_description: JobDescription = extract_job_description(jd_document.pages, jd_document.text)
    except Exception as exc:
        raise AnalysisPipelineError("The extracted document data could not be analyzed.") from exc

    units = embedding_units(resume, job_description)
    if not units:
        raise AnalysisPipelineError("The supplied documents contain no embeddable text.")
    try:
        vectors = generate_embeddings(units)
    except RuntimeError as exc:
        raise AnalysisPipelineError(str(exc)) from exc
    if len(vectors) != len(units) or any(not vector for vector in vectors):
        raise AnalysisPipelineError("The embedding service returned an invalid result.")
    items = _embedding_items(units, vectors)
    resume_items, required_items, preferred_items = _similarity_inputs(items)
    try:
        similarity: SimilarityResponse = analyze_similarity(resume_items, required_items, preferred_items)
    except SimilarityError as exc:
        raise AnalysisPipelineError("Similarity analysis failed.") from exc
    if not similarity.matches:
        raise AnalysisPipelineError("The job description contains no analyzable requirements.")
    try:
        score: MatchScoreResponse = calculate_match_score(similarity)
    except ScoringError as exc:
        raise AnalysisPipelineError("Deterministic scoring failed.") from exc
    analysis_request = AnalysisRequest(resume=resume, job_description=job_description, similarity=similarity, score=score)
    llm_result = generate_analysis(analysis_request, llm_service=llm_service)
    verification_request = EvidenceVerificationRequest(
        resume=resume,
        job_description=job_description,
        similarity=similarity,
        score=score,
        analysis=llm_result.analysis,
    )
    return verify_analysis(verification_request)
