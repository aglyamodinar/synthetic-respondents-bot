from fastapi import FastAPI, Header, HTTPException, Request

from app.api.routes import router as api_router
from app.bot.webhook import process_update, remove_webhook, setup_webhook
from app.config import get_settings

app = FastAPI(title="Synthetic Respondents API", version="0.1.0")
app.include_router(api_router)
settings = get_settings()


@app.on_event("startup")
async def startup_event() -> None:
    if settings.bot_run_mode == "webhook":
        await setup_webhook()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    if settings.bot_run_mode == "webhook":
        await remove_webhook()


async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict:
    if settings.bot_webhook_secret:
        if x_telegram_bot_api_secret_token != settings.bot_webhook_secret:
            raise HTTPException(status_code=403, detail="Invalid webhook secret")
    payload = await request.json()
    await process_update(payload)
    return {"ok": True}


app.add_api_route(settings.bot_webhook_path, telegram_webhook, methods=["POST"])
