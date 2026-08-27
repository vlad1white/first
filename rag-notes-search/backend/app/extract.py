import io

from fastapi import HTTPException
from pypdf import PdfReader

SUPPORTED_SUFFIXES = {".txt", ".md", ".markdown", ".pdf"}


def extract_text(filename: str, content: bytes) -> str:
    suffix = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if suffix not in SUPPORTED_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {sorted(SUPPORTED_SUFFIXES)}",
        )

    if suffix == ".pdf":
        reader = PdfReader(io.BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)

    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1")
