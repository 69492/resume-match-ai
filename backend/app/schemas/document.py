from pydantic import BaseModel, Field


class DocumentPage(BaseModel):
    page_number: int = Field(..., ge=1)
    text: str


class DocumentExtractionResponse(BaseModel):
    filename: str
    page_count: int = Field(..., ge=0)
    text: str
    pages: list[DocumentPage]
