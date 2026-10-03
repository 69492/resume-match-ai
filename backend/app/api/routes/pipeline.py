import math

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.analysis_pipeline_service import AnalysisPipelineError, analyze_documents
from app.services.analysis_service import AnalysisValidationError
from app.services.llm_service import LLMConfigurationError, LLMProviderError, LLMRateLimitError
from app.schemas.verified_analysis import VerifiedAnalysis

router = APIRouter(tags=["analysis"])


@router.post("/api/analyze", response_model=VerifiedAnalysis)
async def analyze_endpoint(
    resume: UploadFile = File(...),
    job_description: UploadFile = File(...),
):
    try:
        return await analyze_documents(resume, job_description)
    except (AnalysisPipelineError, LLMConfigurationError, AnalysisValidationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LLMRateLimitError as exc:
        headers = {"Retry-After": str(max(1, math.ceil(exc.retry_after)))} if exc.retry_after is not None else None
        raise HTTPException(status_code=429, detail=str(exc), headers=headers) from exc
    except LLMProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="The analysis could not be completed.") from exc
