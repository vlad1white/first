import time

import httpx

from . import config

BASE_URL = "https://www.alphavantage.co/query"

# Alpha Vantage's free tier is limited to 25 requests/day, so every response
# is cached in-memory for CACHE_TTL_SECONDS to avoid burning the quota on
# repeated lookups of the same ticker.
_cache: dict[str, tuple[float, dict]] = {}


class AlphaVantageError(Exception):
    pass


def _get(params: dict) -> dict:
    if not config.ALPHA_VANTAGE_API_KEY:
        raise AlphaVantageError(
            "ALPHA_VANTAGE_API_KEY is not set. Copy backend/.env.example to "
            "backend/.env and add a free key from alphavantage.co."
        )

    cache_key = str(sorted(params.items()))
    cached = _cache.get(cache_key)
    if cached and time.time() - cached[0] < config.CACHE_TTL_SECONDS:
        return cached[1]

    params = {**params, "apikey": config.ALPHA_VANTAGE_API_KEY}
    resp = httpx.get(BASE_URL, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    # Alpha Vantage always answers with HTTP 200; throttling and errors show
    # up as a "Note" / "Information" / "Error Message" key instead.
    for key in ("Note", "Information", "Error Message"):
        if key in data:
            raise AlphaVantageError(data[key])

    _cache[cache_key] = (time.time(), data)
    return data


def get_quote(symbol: str) -> dict:
    data = _get({"function": "GLOBAL_QUOTE", "symbol": symbol})
    quote = data.get("Global Quote") or {}
    if not quote:
        raise AlphaVantageError(f"No quote data found for symbol '{symbol}'.")
    return {
        "symbol": quote.get("01. symbol", symbol),
        "price": float(quote.get("05. price", 0)),
        "change": float(quote.get("09. change", 0)),
        "change_percent": quote.get("10. change percent", "0%").rstrip("%"),
        "previous_close": float(quote.get("08. previous close", 0)),
        "volume": int(quote.get("06. volume", 0)),
        "latest_trading_day": quote.get("07. latest trading day", ""),
    }


def get_daily_history(symbol: str, days: int = 30) -> list[dict]:
    data = _get(
        {"function": "TIME_SERIES_DAILY", "symbol": symbol, "outputsize": "compact"}
    )
    series = data.get("Time Series (Daily)") or {}
    points = [
        {"date": date, "close": float(values["4. close"])}
        for date, values in sorted(series.items())[-days:]
    ]
    return points


def get_news(symbol: str, limit: int = 6) -> list[dict]:
    data = _get({"function": "NEWS_SENTIMENT", "tickers": symbol, "limit": str(limit)})
    feed = data.get("feed") or []
    news = []
    for item in feed[:limit]:
        ticker_sentiment = next(
            (t for t in item.get("ticker_sentiment", []) if t.get("ticker") == symbol),
            None,
        )
        news.append(
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "source": item.get("source", ""),
                "summary": item.get("summary", ""),
                "sentiment_label": (ticker_sentiment or {}).get(
                    "ticker_sentiment_label", item.get("overall_sentiment_label", "")
                ),
            }
        )
    return news
