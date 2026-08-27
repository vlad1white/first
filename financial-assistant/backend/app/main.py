from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .alpha_vantage import AlphaVantageError, get_daily_history, get_news, get_quote
from .claude_client import explain_stock

app = FastAPI(title="Financial Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExplainRequest(BaseModel):
    symbol: str
    question: str | None = None


class ExplainResponse(BaseModel):
    quote: dict
    history: list[dict]
    news: list[dict]
    explanation: str


def _fetch_market_data(symbol: str) -> tuple[dict, list[dict], list[dict]]:
    symbol = symbol.strip().upper()
    if not symbol:
        raise HTTPException(status_code=400, detail="Symbol must not be empty")
    try:
        quote = get_quote(symbol)
        history = get_daily_history(symbol)
        news = get_news(symbol)
    except AlphaVantageError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return quote, history, news


@app.get("/api/quote/{symbol}")
def quote(symbol: str) -> dict:
    q, history, news = _fetch_market_data(symbol)
    return {"quote": q, "history": history, "news": news}


@app.post("/api/explain", response_model=ExplainResponse)
def explain(req: ExplainRequest) -> ExplainResponse:
    q, history, news = _fetch_market_data(req.symbol)
    try:
        explanation = explain_stock(req.symbol.strip().upper(), q, history, news, req.question)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return ExplainResponse(quote=q, history=history, news=news, explanation=explanation)


frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
