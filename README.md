# Synthetic Respondents Bot (MVP)

Telegram bot + backend for synthetic respondent studies with SSR scoring.

## Quick Start

1. Copy env:
```bash
cp .env.example .env
```

2. Install:
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -e ../semantic-similarity-rating
```

3. Start infra:
```bash
docker compose up -d postgres redis
```

4. Run API:
```bash
uvicorn app.main:app --reload
```

5. Run worker:
```bash
celery -A app.workers.celery_app worker --loglevel=info
```

6. Run bot:
```bash
python -m app.bot.runner
```

## Bot Modes

`BOT_RUN_MODE` supports:
- `polling` (default): run Telegram polling loop via `python -m app.bot.runner`
- `webhook`: receive Telegram updates on FastAPI route `BOT_WEBHOOK_PATH`

### Polling mode
Set:
```bash
BOT_RUN_MODE=polling
```

Run:
```bash
uvicorn app.main:app --reload
celery -A app.workers.celery_app worker --loglevel=info
python -m app.bot.runner
```

### Webhook mode
Set:
```bash
BOT_RUN_MODE=webhook
BOT_WEBHOOK_PATH=/telegram/webhook
BOT_WEBHOOK_SECRET=replace_me
PUBLIC_BASE_URL=https://your-public-domain
```

Run:
```bash
uvicorn app.main:app --reload
celery -A app.workers.celery_app worker --loglevel=info
```

In webhook mode polling bot process is not required.

## Notes
- Input formats: `txt`, `csv`
- Output report: PDF
- History persisted in Postgres
- Response language mirrors input language (`ru`/`en`)
- You can override purchase-intent wording with `/set_question`
