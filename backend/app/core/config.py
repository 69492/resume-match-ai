import os


def _max_pdf_size_bytes() -> int:
    try:
        size_mb = float(os.getenv("MAX_PDF_SIZE_MB", "10"))
    except ValueError:
        size_mb = 10
    return max(1, int(size_mb * 1024 * 1024))


MAX_PDF_SIZE_BYTES = _max_pdf_size_bytes()
