FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY synthetic-respondents-bot /app/synthetic-respondents-bot
COPY semantic-similarity-rating /app/semantic-similarity-rating

WORKDIR /app/synthetic-respondents-bot

RUN pip install --upgrade pip && \
    pip install -e /app/semantic-similarity-rating && \
    pip install -e .
