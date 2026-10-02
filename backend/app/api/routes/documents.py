from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import MAX_PDF_SIZE_BYTES
from app.schemas.document import DocumentExtractionResponse, DocumentPage
from app.services.pdf_service import PDFProcessingError, extract_pdf_text

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/extract", response_model=DocumentExtractionResponse)
async def extract_document(file: UploadFile = File(...)) -> DocumentExtractionResponse:
    """Extract page-aware text from one uploaded PDF, without persisting it."""
    filename = file.filename or "uploaded.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only .pdf files are accepted.")
    if file.content_type not in (None, "application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="The uploaded file must have PDF content.")

    pdf_bytes = await file.read(MAX_PDF_SIZE_BYTES + 1)
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(pdf_bytes) > MAX_PDF_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="The PDF exceeds the configured size limit.")

    try:
        extracted = extract_pdf_text(pdf_bytes)
    except PDFProcessingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unexpected PDF processing error.") from exc

    return DocumentExtractionResponse(
        filename=filename,
        page_count=extracted.page_count,
        text=extracted.text,
        pages=[DocumentPage(page_number=page.page_number, text=page.text) for page in extracted.pages],
    )
