# 📈 Financial Assistant

Вводишь тикер — приложение тянет реальные рыночные данные (котировку,
историю цен, свежие новости с sentiment-разметкой) через Alpha Vantage и
просит Claude объяснить простым языком, что происходит с акцией, почему
она могла двигаться и какие есть риски.

## Как это работает

1. **Данные** — бэкенд запрашивает у [Alpha Vantage](https://www.alphavantage.co/)
   три эндпоинта: `GLOBAL_QUOTE` (текущая цена/изменение), `TIME_SERIES_DAILY`
   (история для спарклайна) и `NEWS_SENTIMENT` (новости + метка настроения
   bullish/bearish/neutral) — `backend/app/alpha_vantage.py`.
2. **Кэш** — свободный тариф Alpha Vantage жёстко ограничен (25
   запросов/день), поэтому ответы кэшируются в памяти на
   `CACHE_TTL_SECONDS` (по умолчанию 15 минут), чтобы не сжигать квоту.
3. **Объяснение** — котировка, история и новости передаются Claude одним
   структурированным блоком; модель объясняет ситуацию, называет
   вероятные причины движения (не выдавая догадки за факты) и риски —
   `backend/app/claude_client.py`.
4. Можно задать свой вопрос вторым полем («почему упала на этой неделе?») —
   он добавляется к промпту.

## Запуск

```bash
cd financial-assistant/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# впишите ANTHROPIC_API_KEY и ALPHA_VANTAGE_API_KEY в .env
# (бесплатный ключ Alpha Vantage: https://www.alphavantage.co/support/#api-key)

uvicorn app.main:app --reload --port 8000
```

Открыть `http://localhost:8000`.

> Бесплатный тариф Alpha Vantage даёт всего 25 запросов в день — этого
> достаточно для демонстрации, но не для активного использования.
> Каждый разбор тикера тратит 3 запроса (quote + history + news).

## API

| Метод  | Путь                  | Описание                                   |
|--------|-----------------------|---------------------------------------------|
| `GET`  | `/api/quote/{symbol}` | Сырые данные: котировка, история, новости    |
| `POST` | `/api/explain`        | `{"symbol": "AAPL", "question": "..."}` → данные + объяснение Claude |

## Стек

FastAPI · httpx · Alpha Vantage API · Anthropic SDK (Claude) · ваниль
HTML/CSS/JS (SVG-спарклайн без библиотек).

## Дисклеймер

Это учебный проект, а не инвестиционный совет. Объяснения строятся на
данных бесплатного API и могут быть неполными или с задержкой.
