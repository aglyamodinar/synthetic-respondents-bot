# Synthetic Respondents Bot (MVP)

Telegram bot + backend for synthetic respondent studies with SSR scoring.

## Deployment & Consulting

### RU
Хотите внедрить этого бота под ваш бизнес-кейс (маркетинг, продукт, креативы, UX-тесты)?

Пишите в Telegram: **[@aglamov](https://t.me/aglamov)**

Что прислать в первом сообщении:
- ниша или тип продукта
- сколько тестов в месяц планируете
- что хотите улучшить (конверсия, креативы, офферы, упаковка)

### EN
Need help deploying and customizing this bot for your use case (marketing, product, creatives, UX testing)?

Contact on Telegram: **[@aglamov](https://t.me/aglamov)**

Please include in your first message:
- your niche/product type
- expected testing volume per month
- your primary goal (conversion, creatives, offer testing, messaging)

## Quick Start

1. Copy env:
```bash
cp .env.example .env
```

2. Start all services in Docker (webhook mode):
```bash
docker compose up -d --build
```

3. Start all services in Docker (polling mode):
```bash
docker compose --profile polling up -d --build
```

4. Check status/logs:
```bash
docker compose ps
docker compose logs -f api worker
```

## Local Run (without Docker for app processes)

1. Install:
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -e ../semantic-similarity-rating
```

2. Start infra:
```bash
docker compose up -d postgres redis
```

3. Run API:
```bash
uvicorn app.main:app --reload
```

4. Run worker:
```bash
celery -A app.workers.celery_app worker --loglevel=info
```

5. Run bot:
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

Run in Docker:
```bash
docker compose --profile polling up -d --build
```

Run locally:
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

Run in Docker:
```bash
docker compose up -d --build
```

Run locally:
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
