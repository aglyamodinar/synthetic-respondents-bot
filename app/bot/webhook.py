from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.types import Update

from app.bot.handlers import router
from app.config import get_settings

settings = get_settings()
bot = Bot(token=settings.bot_token) if settings.bot_token else None
dp = Dispatcher()
dp.include_router(router)


async def setup_webhook() -> None:
    if not bot:
        raise RuntimeError("BOT_TOKEN is not configured.")
    if not settings.bot_webhook_url:
        raise RuntimeError("PUBLIC_BASE_URL is required for webhook mode.")
    await bot.set_webhook(
        url=settings.bot_webhook_url,
        secret_token=settings.bot_webhook_secret or None,
        drop_pending_updates=False,
    )


async def remove_webhook() -> None:
    if bot:
        await bot.delete_webhook(drop_pending_updates=False)


async def process_update(payload: dict) -> None:
    if not bot:
        raise RuntimeError("BOT_TOKEN is not configured.")
    update = Update.model_validate(payload)
    await dp.feed_update(bot, update)

