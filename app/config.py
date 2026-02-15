from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    bot_token: str = ""
    bot_run_mode: str = "polling"
    bot_webhook_path: str = "/telegram/webhook"
    bot_webhook_secret: str = ""
    public_base_url: str = ""
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "openai/gpt-5-nano"

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/synthbot"
    async_database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/synthbot"
    )
    redis_url: str = "redis://localhost:6379/0"

    reports_dir: str = "./artifacts/reports"
    cache_salt: str = "v1"

    default_question_ru: str = (
        "Насколько вероятно, что вы купите этот продукт, если он будет доступен "
        "по обычной для категории цене? Объясните кратко, почему."
    )
    default_question_en: str = (
        "How likely are you to buy this product if it is available at a typical category "
        "price? Briefly explain why."
    )

    ssr_model_name: str = "all-MiniLM-L6-v2"
    max_output_tokens: int = 80

    @property
    def bot_webhook_url(self) -> str:
        if not self.public_base_url:
            return ""
        return self.public_base_url.rstrip("/") + self.bot_webhook_path

    @property
    def reports_path(self) -> Path:
        return Path(self.reports_dir)


@lru_cache
def get_settings() -> Settings:
    return Settings()
