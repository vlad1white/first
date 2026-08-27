# AI Portfolio Projects

Три небольших full-stack приложения на Claude API, каждое демонстрирует
свой AI-паттерн. Все — FastAPI-бэкенд + ваниль HTML/CSS/JS фронтенд без
сборки, чтобы запускались одной командой.

| Проект | Паттерн | Папка |
|---|---|---|
| 📓 **RAG Notes Search** | Семантический поиск по своим заметкам: чанкинг → локальные эмбеддинги (fastembed) → векторный поиск → ответ Claude строго по найденным фрагментам с цитатами | [`rag-notes-search/`](./rag-notes-search) |
| 📈 **Financial Assistant** | Живые рыночные данные (Alpha Vantage: котировка, история, новости) → Claude объясняет движение акции и риски простым языком | [`financial-assistant/`](./financial-assistant) |
| 🔍 **AI Code Reviewer** | Structured output: код отправляется Claude с forced tool-use по JSON-схеме, ответ рендерится карточками с багами/советами | [`code-reviewer/`](./code-reviewer) |

## Быстрый старт

Каждый проект самодостаточен — свой `backend/requirements.txt`,
`.env.example` и фронтенд, который бэкенд раздаёт сам. Общий паттерн
запуска:

```bash
cd <project>/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # вписать ключи API
uvicorn app.main:app --reload --port 8000
```

Дальше — `http://localhost:8000`. Подробности, нужные API-ключи и
описание архитектуры — в README каждого проекта.

## Общее для всех трёх

- **Anthropic SDK** — во всех проектах Claude вызывается напрямую через
  `anthropic` Python SDK, без обёрток вроде LangChain, чтобы было видно
  сам паттерн работы с API (system prompt, structured output через
  tool use, RAG-контекст).
- **Без сборки фронтенда** — чистый HTML/CSS/JS, бэкенд раздаёт статику
  сам (`StaticFiles`), так что не нужен Node/npm для запуска.
- **Свои ключи** — каждый проект требует `ANTHROPIC_API_KEY`; RAG
  использует локальные эмбеддинги (без доп. ключа), финансовый ассистент
  дополнительно требует бесплатный `ALPHA_VANTAGE_API_KEY`.
