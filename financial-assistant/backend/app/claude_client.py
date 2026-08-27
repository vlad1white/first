from anthropic import Anthropic

from . import config

SYSTEM_PROMPT = """You are a plain-language financial explainer for a retail \
investor. You are given a stock's latest quote, a short recent price history \
and a handful of recent news headlines with sentiment labels.

Rules:
- Explain what's happening with the stock and, if the news gives a plausible \
reason, why it might be moving — but never present a guess as certain fact.
- Mention 1-3 concrete risks or things worth watching, grounded in the data \
you were given (not generic disclaimers).
- This is educational information, not investment advice — say so briefly \
once, don't repeat it.
- Be concise: 3-5 short paragraphs or a short paragraph plus a few bullets.
- Answer in the same language the user's question was asked in (default to \
Russian if no question was given).
- Do not invent numbers that are not present in the provided data."""


def _client() -> Anthropic:
    if not config.ANTHROPIC_API_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Copy backend/.env.example to backend/.env "
            "and add your key."
        )
    return Anthropic(api_key=config.ANTHROPIC_API_KEY)


def explain_stock(symbol: str, quote: dict, history: list[dict], news: list[dict], question: str | None) -> str:
    history_str = ", ".join(f"{p['date']}: {p['close']}" for p in history) or "n/a"
    news_str = "\n".join(
        f"- ({n['sentiment_label']}) {n['title']} — {n['summary'][:200]} [{n['source']}]"
        for n in news
    ) or "No recent news available."

    data_block = f"""Symbol: {symbol}
Latest price: {quote['price']} (change {quote['change']}, {quote['change_percent']}%)
Previous close: {quote['previous_close']}
Latest trading day: {quote['latest_trading_day']}
Volume: {quote['volume']}

Recent daily closes: {history_str}

Recent news:
{news_str}"""

    user_message = data_block + (f"\n\nUser question: {question}" if question else "\n\nExplain what's going on with this stock.")

    response = _client().messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return "".join(block.text for block in response.content if block.type == "text")
