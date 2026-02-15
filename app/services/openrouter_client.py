from __future__ import annotations

import httpx

from app.config import get_settings

settings = get_settings()


class OpenRouterClient:
    def __init__(self) -> None:
        self.base_url = settings.openrouter_base_url.rstrip("/")
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model

    async def generate_response(
        self,
        prompt: str,
        language: str,
        model: str | None = None,
        max_tokens: int | None = None,
    ) -> dict:
        model_name = model or self.model
        max_t = max_tokens or settings.max_output_tokens
        body = {
            "model": model_name,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a synthetic survey respondent. Reply as one consumer in plain text."
                        if language == "en"
                        else "Ты синтетический респондент опроса. Отвечай как один потребитель простым текстом."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": max_t,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions", json=body, headers=headers
            )
            response.raise_for_status()
            payload = response.json()

        content = payload["choices"][0]["message"]["content"].strip()
        usage = payload.get("usage", {})
        return {
            "text": content,
            "model": payload.get("model", model_name),
            "usage": {
                "prompt_tokens": int(usage.get("prompt_tokens", 0)),
                "completion_tokens": int(usage.get("completion_tokens", 0)),
            },
        }

