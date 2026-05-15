import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import NetworkError, TimedOut, BadRequest, Forbidden

logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    error = context.error

    if isinstance(error, (NetworkError, TimedOut)):
        logger.warning(f"Network/timeout error: {error}")
        return

    if isinstance(error, Forbidden):
        logger.warning(f"Bot blocked by user: {error}")
        return

    if isinstance(error, BadRequest):
        if "Message is not modified" in str(error):
            return
        if "can't parse entities" in str(error).lower():
            logger.warning(f"Markdown parse error: {error}")
            if isinstance(update, Update) and update.effective_message:
                try:
                    await update.effective_message.reply_text(
                        "❌ Xabar formatlashda xatolik. Keyinroq urinib ko'ring."
                    )
                except Exception:
                    pass
            return

    logger.error(f"Unhandled error for update {update}: {error}", exc_info=error)

    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ Kutilmagan xatolik yuz berdi.\n\n/start buyrug'ini bosib qayta boshlang."
            )
        except Exception:
            pass
