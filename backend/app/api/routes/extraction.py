from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import MAX_PDF_SIZE_BYTES
from app.schemas.extraction import JobDescription, ResumeProfile
from app.services.jd_extraction_service import extract_job_description
from app.services.pdf_service import PDFProcessingError, extract_pdf_text
from app.services.resume_extraction_service import extract_resume

router = APIRouter(tags=["extraction"])


async def _read_pdf(file: UploadFile):
    filename = file.filename or "uploaded.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only .pdf files are accepted.")
    if file.content_type not in (None, "application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="The uploaded file must have PDF content.")
    data = await file.read(MAX_PDF_SIZE_BYTES + 1)
    if not data:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(data) > MAX_PDF_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="The PDF exceeds the configured size limit.")
    try:
        return filename, extract_pdf_text(data)
    except PDFProcessingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/api/resume/extract", response_model=ResumeProfile)
async def extract_resume_endpoint(file: UploadFile = File(...)) -> ResumeProfile:
    _, document = await _read_pdf(file)
    return extract_resume(document.pages, document.text)


@router.post("/api/job-description/extract", response_model=JobDescription)
async def extract_job_description_endpoint(file: UploadFile = File(...)) -> JobDescription:
    _, document = await _read_pdf(file)
    return extract_job_description(document.pages, document.text)
