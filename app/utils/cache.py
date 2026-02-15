import hashlib
import json

import redis

from app.config import get_settings

settings = get_settings()
redis_client = redis.from_url(settings.redis_url, decode_responses=True)


def make_cache_key(payload: dict) -> str:
    packed = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    data = f"{settings.cache_salt}:{packed}".encode("utf-8")
    digest = hashlib.sha256(data).hexdigest()
    return f"synth:{digest}"


def get_cached_json(key: str) -> dict | None:
    raw = redis_client.get(key)
    return json.loads(raw) if raw else None


def set_cached_json(key: str, payload: dict, ttl_seconds: int = 7 * 24 * 3600) -> None:
    redis_client.setex(key, ttl_seconds, json.dumps(payload, ensure_ascii=False))

