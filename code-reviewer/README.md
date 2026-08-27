# 🔍 AI Code Reviewer

Вставляешь код — Claude возвращает структурированный разбор (баги,
security, performance, стиль, тест-покрытие) в виде JSON, который
рендерится карточками с цветовой кодировкой по серьёзности.

## Как это работает

Вместо того чтобы парсить свободный текст ответа, бэкенд заставляет
Claude вызвать один конкретный **tool** с фиксированной JSON-схемой
(`backend/app/schema.py`) через `tool_choice={"type": "tool", "name": "submit_code_review"}`
(`backend/app/claude_client.py`). Модель обязана вернуть:

```json
{
  "summary": "...",
  "overall_score": 7,
  "issues": [
    {
      "severity": "critical | warning | suggestion",
      "category": "bug | security | performance | style | best-practice | test-coverage",
      "line": 42,
      "title": "...",
      "description": "...",
      "suggestion": "..."
    }
  ]
}
```

Это надёжнее, чем просить модель «верни JSON» в тексте и парсить его
руками — Anthropic API гарантирует, что `tool_use` блок соответствует
схеме по структуре, так что фронтенду достаточно один раз десериализовать
`block.input` и отрендерить карточки.

## Запуск

```bash
cd code-reviewer/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# впишите ANTHROPIC_API_KEY в .env

uvicorn app.main:app --reload --port 8000
```

Открыть `http://localhost:8000`, вставить код, нажать «Проверить код».

## API

| Метод  | Путь          | Описание                                                        |
|--------|---------------|-------------------------------------------------------------------|
| `POST` | `/api/review` | `{"code": "...", "language": "python"}` → структурированный разбор |

## Стек

FastAPI · Anthropic SDK (Claude, forced tool use для structured output) ·
ваниль HTML/CSS/JS без сборки.
