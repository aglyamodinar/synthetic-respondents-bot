PY=python3

.PHONY: init db api worker bot

init:
	$(PY) -m venv .venv
	. .venv/bin/activate && pip install -e . && pip install -e ../semantic-similarity-rating

db:
	docker compose up -d postgres redis
	. .venv/bin/activate && $(PY) scripts/init_db.py

api:
	. .venv/bin/activate && uvicorn app.main:app --reload

worker:
	. .venv/bin/activate && celery -A app.workers.celery_app worker --loglevel=info

bot:
	. .venv/bin/activate && $(PY) -m app.bot.runner

