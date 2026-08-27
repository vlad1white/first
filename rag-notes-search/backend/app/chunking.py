import re

from . import config


def _split_into_sentences(text: str) -> list[str]:
    # Keep it simple and dependency-free: split on sentence-ending
    # punctuation followed by whitespace, while preserving paragraph breaks.
    text = text.replace("\r\n", "\n")
    parts = re.split(r"(?<=[.!?])\s+(?=[A-ZА-Я0-9])|\n{2,}", text)
    return [p.strip() for p in parts if p.strip()]


def chunk_text(
    text: str,
    chunk_size: int = config.CHUNK_SIZE,
    overlap: int = config.CHUNK_OVERLAP,
) -> list[str]:
    """Greedily pack sentences into ~chunk_size character windows with overlap."""
    sentences = _split_into_sentences(text)
    if not sentences:
        return []

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for sentence in sentences:
        if current_len + len(sentence) + 1 > chunk_size and current:
            chunk = " ".join(current)
            chunks.append(chunk)
            # Build overlap from the tail of the previous chunk.
            overlap_text = chunk[-overlap:] if overlap > 0 else ""
            current = [overlap_text] if overlap_text else []
            current_len = len(overlap_text)

        current.append(sentence)
        current_len += len(sentence) + 1

    if current:
        chunks.append(" ".join(current))

    return [c.strip() for c in chunks if c.strip()]
