import asyncio

from aiogram import Bot, Dispatcher

from app.bot.handlers import router
from app.bot.webhook import remove_webhook, setup_webhook
from app.config import get_settings


async def main() -> None:
    settings = get_settings()
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is not configured.")
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    dp.include_router(router)
    if settings.bot_run_mode == "webhook":
        await setup_webhook()
        print(f"Webhook configured at {settings.bot_webhook_url}")
        return
    await remove_webhook()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
