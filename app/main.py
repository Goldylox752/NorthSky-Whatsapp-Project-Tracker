import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import init_db, get_db
from app.handlers import handle_message
from app.whatsapp import whatsapp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="WhatsApp Project Tracker",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"status": "ok", "service": "WhatsApp Project Tracker"}


@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        logger.info("Webhook verified successfully")
        return Response(content=hub_challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook")
async def receive_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    logger.info(f"Incoming webhook: {body}")

    try:
        entry = body.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return {"status": "ignored"}

        message = messages[0]
        from_number = message.get("from")
        message_id = message.get("id")
        message_type = message.get("type")

        if message_type != "text":
            await whatsapp.send_text(from_number, "I only understand text messages for now.")
            return {"status": "unsupported_type"}

        if from_number != settings.allowed_phone_number:
            logger.warning(f"Unauthorized number: {from_number}")
            return {"status": "unauthorized"}

        text = message["text"]["body"]

        try:
            await whatsapp.mark_as_read(message_id)
        except Exception as e:
            logger.warning(f"Could not mark as read: {e}")

        reply = await handle_message(text, db)
        await whatsapp.send_text(from_number, reply)

        return {"status": "ok"}

    except Exception as e:
        logger.exception("Error processing webhook")
        return {"status": "error", "detail": str(e)}