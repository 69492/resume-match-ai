import math
import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.analysis_pipeline_service import AnalysisPipelineError, analyze_documents
from app.services.analysis_service import AnalysisValidationError
from app.services.llm_service import LLMConfigurationError, LLMProviderError, LLMRateLimitError
from app.schemas.verified_analysis import VerifiedAnalysis

router = APIRouter(tags=["analysis"])
logger = logging.getLogger(__name__)


def _safe_failure_reason(exc: Exception) -> str:
    """Classify client-visible failures without logging document-derived values."""
    message = str(exc).casefold()
    if isinstance(exc, AnalysisValidationError):
        if message.startswith("unsupported partial match"):
            return "unsupported_partial_match"
        if message.startswith("unsupported strong match"):
            return "unsupported_strong_match"
        if message.startswith("unsupported missing skill"):
            return "unsupported_missing_skill"
        if message.startswith("unsupported project"):
            return "unsupported_project"
        if message.startswith("similarity changed"):
            return "similarity_changed"
        return "analysis_validation_error"
    if isinstance(exc, LLMConfigurationError):
        return "llm_configuration_error"
    if isinstance(exc, AnalysisPipelineError):
        if "job description contains no analyzable" in message:
            return "no_job_requirements"
        if "deterministic scoring failed" in message:
            return "scoring_failure"
        if "similarity analysis failed" in message:
            return "similarity_failure"
        if "embedding" in message:
            return "embedding_failure"
        if "extracted document data" in message:
            return "document_extraction_failure"
        if "pdf" in message:
            return "invalid_pdf_input"
        return "analysis_pipeline_error"
    return "analysis_request_error"


@router.post("/api/analyze", response_model=VerifiedAnalysis)
async def analyze_endpoint(
    resume: UploadFile = File(...),
    job_description: UploadFile = File(...),
):
    try:
        return await analyze_documents(resume, job_description)
    except (AnalysisPipelineError, LLMConfigurationError, AnalysisValidationError) as exc:
        logger.warning("Analysis request rejected status=400 reason=%s", _safe_failure_reason(exc))
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LLMRateLimitError as exc:
        headers = {"Retry-After": str(max(1, math.ceil(exc.retry_after)))} if exc.retry_after is not None else None
        raise HTTPException(status_code=429, detail=str(exc), headers=headers) from exc
    except LLMProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="The analysis could not be completed.") from exc
