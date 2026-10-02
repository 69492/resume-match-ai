from fastapi import APIRouter

from app.schemas.verified_analysis import EvidenceVerificationRequest, VerifiedAnalysis
from app.services.evidence_service import verify_analysis

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/verify", response_model=VerifiedAnalysis)
def verify_analysis_endpoint(request: EvidenceVerificationRequest) -> VerifiedAnalysis:
    return verify_analysis(request)
