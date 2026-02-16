import asyncio

from aiogram import Bot

from app.bot.webhook import dp, remove_webhook, setup_webhook
from app.config import get_settings


async def main() -> None:
    settings = get_settings()
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is not configured.")
    bot = Bot(token=settings.bot_token)
    if settings.bot_run_mode == "webhook":
        await setup_webhook()
        print(f"Webhook configured at {settings.bot_webhook_url}")
        return
    await remove_webhook()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
