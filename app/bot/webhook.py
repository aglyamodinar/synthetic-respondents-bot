from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.utils.token import TokenValidationError

from app.bot.handlers import router
from app.config import get_settings

settings = get_settings()
dp = Dispatcher()
dp.include_router(router)
bot: Bot | None = None


def get_bot() -> Bot:
    global bot
    if bot is not None:
        return bot
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is not configured.")
    try:
        bot = Bot(token=settings.bot_token)
    except TokenValidationError as exc:
        raise RuntimeError("BOT_TOKEN is invalid.") from exc
    return bot


async def setup_webhook() -> None:
    current_bot = get_bot()
    if not settings.bot_webhook_url:
        raise RuntimeError("PUBLIC_BASE_URL is required for webhook mode.")
    await current_bot.set_webhook(
        url=settings.bot_webhook_url,
        secret_token=settings.bot_webhook_secret or None,
        drop_pending_updates=False,
    )


async def remove_webhook() -> None:
    if not settings.bot_token:
        return
    try:
        current_bot = get_bot()
    except RuntimeError:
        return
    await current_bot.delete_webhook(drop_pending_updates=False)


async def process_update(payload: dict) -> None:
    current_bot = get_bot()
    update = Update.model_validate(payload)
    await dp.feed_update(current_bot, update)
