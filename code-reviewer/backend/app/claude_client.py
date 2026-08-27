from anthropic import Anthropic

from . import config
from .schema import REVIEW_TOOL

SYSTEM_PROMPT = """You are a meticulous senior code reviewer. You will be \
given a snippet of code (and optionally its language). Review it for:
- correctness bugs (logic errors, edge cases, off-by-one, null/undefined handling)
- security issues (injection, unsafe deserialization, secrets, etc.)
- performance problems
- style and readability
- missing test coverage for risky logic

Only report issues you actually see evidence for in the given code — do not \
invent problems to pad the list. If the code looks solid, say so and return \
few or no issues. Always respond by calling the submit_code_review tool."""


def _client() -> Anthropic:
    if not config.ANTHROPIC_API_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Copy backend/.env.example to backend/.env "
            "and add your key."
        )
    return Anthropic(api_key=config.ANTHROPIC_API_KEY)


def review_code(code: str, language: str | None) -> dict:
    lang_hint = f" (language: {language})" if language else ""
    user_message = f"Review this code{lang_hint}:\n\n```\n{code}\n```"

    response = _client().messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        tools=[REVIEW_TOOL],
        tool_choice={"type": "tool", "name": "submit_code_review"},
        messages=[{"role": "user", "content": user_message}],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "submit_code_review":
            return block.input

    raise RuntimeError("Claude did not return a structured review.")
