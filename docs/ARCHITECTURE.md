# Architecture (MVP)

- Telegram Bot (`aiogram`) accepts study setup and files.
- Bot writes studies/stimuli to Postgres and enqueues run in Celery.
- Celery worker executes pipeline:
  1) OpenRouter generation
  2) SSR scoring to Likert PMFs
  3) Metrics aggregation
  4) PDF artifact generation
- FastAPI provides health/status/metrics endpoints.
- Redis is used for queue backend and generation cache.
