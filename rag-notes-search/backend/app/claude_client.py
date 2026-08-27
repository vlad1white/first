from anthropic import Anthropic

from . import config
from .vector_store import Chunk

SYSTEM_PROMPT = """You are a research assistant answering questions strictly from the \
user's own notes, which are provided to you as numbered source excerpts.

Rules:
- Answer only using information contained in the sources below. Do not use outside knowledge.
- If the sources don't contain the answer, say so plainly instead of guessing.
- When you use a fact from a source, cite it inline like [1], [2] matching the source numbers.
- Answer in the same language the question was asked in.
- Be concise and direct."""


def _client() -> Anthropic:
    if not config.ANTHROPIC_API_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Copy backend/.env.example to backend/.env "
            "and add your key."
        )
    return Anthropic(api_key=config.ANTHROPIC_API_KEY)


def _format_sources(chunks: list[Chunk]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        parts.append(f"[{i}] (from \"{chunk.filename}\")\n{chunk.text}")
    return "\n\n".join(parts)


def answer_question(question: str, chunks: list[Chunk]) -> str:
    if not chunks:
        return (
            "В базе пока нет заметок — сначала загрузите хотя бы один документ, "
            "чтобы я мог искать в нём ответ."
        )

    sources_block = _format_sources(chunks)
    user_message = f"Sources:\n\n{sources_block}\n\nQuestion: {question}"

    response = _client().messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return "".join(block.text for block in response.content if block.type == "text")
