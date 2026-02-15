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

## Notes
- Input formats: `txt`, `csv`
- Output report: PDF
- History persisted in Postgres
- Response language mirrors input language (`ru`/`en`)

