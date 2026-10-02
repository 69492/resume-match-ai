from fastapi import APIRouter, HTTPException

from app.schemas.llm_analysis import AnalysisRequest, AnalysisResponse
from app.services.analysis_service import AnalysisValidationError, generate_analysis
from app.services.llm_service import LLMConfigurationError, LLMProviderError

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/generate", response_model=AnalysisResponse)
def generate_analysis_endpoint(request: AnalysisRequest) -> AnalysisResponse:
    try:
        return generate_analysis(request)
    except (LLMConfigurationError, AnalysisValidationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LLMProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
