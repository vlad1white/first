from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .claude_client import review_code

app = FastAPI(title="AI Code Reviewer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ReviewRequest(BaseModel):
    code: str
    language: str | None = None


MAX_CODE_LENGTH = 20_000


@app.post("/api/review")
def review(req: ReviewRequest) -> dict:
    code = req.code.strip()
    if not code:
        raise HTTPException(status_code=400, detail="Code must not be empty")
    if len(code) > MAX_CODE_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Code is too long ({len(code)} chars, max {MAX_CODE_LENGTH}).",
        )

    try:
        return review_code(code, req.language)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
