import re
from dataclasses import dataclass
from io import BytesIO

import fitz


class PDFProcessingError(ValueError):
    """Expected PDF processing failure safe to expose to an API client."""


@dataclass(frozen=True)
class ExtractedPage:
    page_number: int
    text: str


@dataclass(frozen=True)
class ExtractedDocument:
    page_count: int
    text: str
    pages: list[ExtractedPage]


def clean_text(text: str) -> str:
    """Normalize whitespace while retaining line and paragraph structure."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf_text(pdf_bytes: bytes) -> ExtractedDocument:
    """Extract cleaned text from each page of an in-memory PDF."""
    if not pdf_bytes or not pdf_bytes.startswith(b"%PDF"):
        raise PDFProcessingError("The uploaded file is not a valid PDF.")

    try:
        document = fitz.open(stream=BytesIO(pdf_bytes), filetype="pdf")
    except Exception as exc:
        raise PDFProcessingError("The PDF is corrupted, unreadable, or password-protected.") from exc

    try:
        pages = [
            ExtractedPage(page_number=index + 1, text=clean_text(page.get_text("text")))
            for index, page in enumerate(document)
        ]
        text = "\n\n".join(page.text for page in pages if page.text)
        if not text:
            raise PDFProcessingError(
                "The PDF contains no extractable text. OCR is not implemented yet."
            )
        return ExtractedDocument(page_count=len(pages), text=text, pages=pages)
    except PDFProcessingError:
        raise
    except Exception as exc:
        raise PDFProcessingError("The PDF text could not be extracted.") from exc
    finally:
        document.close()
