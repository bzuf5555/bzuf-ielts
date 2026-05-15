import asyncio
import logging
import sys
from aiohttp import web
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from .config import settings
from .services.groq_service import GroqService
from .services.mongodb_service import MongoDBService
from .services.stt_service import STTService
from .agents.writing_agent import WritingAgent
from .agents.speaking_agent import SpeakingAgent
from .handlers.start_handler import (
    start_handler, help_handler, callback_handler,
    contact_handler, keyboard_button_handler,
    BTN_PART1, BTN_PART2, BTN_PART3, BTN_STATS, BTN_HISTORY, BTN_HELP,
)
from .handlers.writing_handler import writing_handler, document_handler
from .handlers.speaking_handler import speaking_handler
from .handlers.speaking_parts_handler import speaking_menu_handler, part_callback_handler
from .handlers.history_handler import history_handler, stats_handler
from .handlers.error_handler import error_handler

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def build_application() -> Application:
    app = Application.builder().token(settings.telegram_bot_token).build()

    groq_svc = GroqService(settings.groq_api_key)
    db_svc = MongoDBService(settings.mongodb_uri)
    stt_svc = STTService(groq_svc)
    writing_ag = WritingAgent(groq_svc)
    speaking_ag = SpeakingAgent(groq_svc)

    app.bot_data["db"] = db_svc
    app.bot_data["groq"] = groq_svc
    app.bot_data["stt_service"] = stt_svc
    app.bot_data["writing_agent"] = writing_ag
    app.bot_data["speaking_agent"] = speaking_ag

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("speaking", speaking_menu_handler))
    app.add_handler(CommandHandler("history", history_handler))
    app.add_handler(CommandHandler("stats", stats_handler))
    app.add_handler(CallbackQueryHandler(part_callback_handler, pattern="^speaking_part_"))
    app.add_handler(CallbackQueryHandler(part_callback_handler, pattern="^speaking_menu$"))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    app.add_handler(MessageHandler(filters.VOICE, speaking_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, document_handler))
    # Keyboard buttons must be caught BEFORE writing_handler
    keyboard_btns = filters.Text([BTN_PART1, BTN_PART2, BTN_PART3, BTN_STATS, BTN_HISTORY, BTN_HELP])
    app.add_handler(MessageHandler(keyboard_btns, keyboard_button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, writing_handler))
    app.add_error_handler(error_handler)

    return app


async def health_check(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok", "service": "bzuf-ielts-bot", "version": "1.0.0"})


async def handle_webhook(request: web.Request, app: Application) -> web.Response:
    try:
        data = await request.json()
        update = Update.de_json(data, app.bot)
        await app.process_update(update)
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
    return web.Response(status=200)


async def run_webhook(app: Application, port: int):
    webhook_url = settings.webhook_url
    logger.info(f"Starting webhook mode on port {port} → {webhook_url}")

    webserver = web.Application()
    webserver.router.add_get("/health", health_check)
    webserver.router.add_post("/webhook", lambda req: handle_webhook(req, app))

    runner = web.AppRunner(webserver)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Web server on 0.0.0.0:{port}")

    await app.initialize()
    await app.bot.set_webhook(
        url=webhook_url,
        allowed_updates=["message", "callback_query", "contact"],
        drop_pending_updates=True,
    )
    logger.info(f"Webhook registered: {webhook_url}")
    await app.start()

    try:
        logger.info("Bot running (webhook). Ctrl+C to stop.")
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down...")
    finally:
        await app.stop()
        await app.shutdown()
        await runner.cleanup()
        db: MongoDBService = app.bot_data.get("db")
        if db:
            await db.close()


async def run_polling(app: Application):
    logger.info("Starting polling mode (development)")
    db: MongoDBService = app.bot_data.get("db")
    if db:
        await db.setup_indexes()

    await app.initialize()
    await app.bot.delete_webhook(drop_pending_updates=True)
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)

    logger.info("Bot running (polling). Ctrl+C to stop.")
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down...")
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
        if db:
            await db.close()


async def main():
    logger.info("=== BZUF IELTS Bot Starting ===")
    app = build_application()

    if settings.is_production:
        db: MongoDBService = app.bot_data.get("db")
        if db:
            await db.setup_indexes()
        await run_webhook(app, settings.port)
    else:
        await run_polling(app)


if __name__ == "__main__":
    asyncio.run(main())
