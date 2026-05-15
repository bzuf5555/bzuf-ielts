import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from ..utils.validators import validate_writing_text, detect_writing_task_type, count_words
from ..utils.formatters import format_writing_feedback, format_corrected_writing

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 4000


async def writing_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("❌ Bo'sh xabar. Iltimos, ingliz tilida esse yuboring.")
        return
    await _process_writing(update, context, text)


async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if not document:
        return

    allowed_mimes = [
        "text/plain",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]
    if document.mime_type not in allowed_mimes and not document.file_name.endswith((".txt", ".docx", ".doc")):
        await update.message.reply_text("❌ Faqat .txt yoki .docx formatdagi hujjatlar qabul qilinadi.")
        return

    if document.file_size and document.file_size > 500 * 1024:
        await update.message.reply_text("❌ Fayl hajmi 500KB dan oshmasligi kerak.")
        return

    processing_msg = await update.message.reply_text("📥 Hujjat o'qilmoqda...")
    try:
        file = await context.bot.get_file(document.file_id)
        content = await file.download_as_bytearray()
        text = content.decode("utf-8", errors="ignore").strip()
        if not text:
            await processing_msg.edit_text("❌ Hujjat bo'sh yoki o'qib bo'lmadi.")
            return
        await processing_msg.delete()
        await _process_writing(update, context, text)
    except Exception as e:
        logger.error(f"Document handler error: {e}")
        await processing_msg.edit_text("❌ Hujjatni o'qishda xatolik. Matnni to'g'ridan-to'g'ri yuboring.")


async def _process_writing(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    user = update.effective_user
    db = context.bot_data.get("db")
    writing_agent = context.bot_data.get("writing_agent")

    if not writing_agent:
        await update.message.reply_text("❌ Tizimda xatolik. Keyinroq urinib ko'ring.")
        return

    if db:
        allowed = await db.check_rate_limit(user.id)
        if not allowed:
            await update.message.reply_text(
                "⏳ *Soatlik cheklov:* 1 soatda ko'pi bilan 10 ta tahlil.\n\nKeyinroq urinib ko'ring.",
                parse_mode="Markdown",
            )
            return

    valid, error_msg = validate_writing_text(text)
    if not valid:
        await update.message.reply_text(f"❌ {error_msg}")
        return

    word_count = count_words(text)
    task_type = detect_writing_task_type(text)
    task_label = "Task 1" if task_type == "task1" else "Task 2"

    if task_type == "task1" and word_count < 150:
        await update.message.reply_text(
            f"ℹ️ Matn {word_count} so'zdan iborat. IELTS Task 1 uchun kamida 150 so'z tavsiya etiladi.",
        )
    elif task_type == "task2" and word_count < 250:
        await update.message.reply_text(
            f"ℹ️ Matn {word_count} so'zdan iborat. IELTS Task 2 uchun kamida 250 so'z tavsiya etiladi.",
        )

    processing_msg = await update.message.reply_text(
        f"⏳ *IELTS Writing {task_label} tahlil qilinmoqda...*\n📏 {word_count} so'z — biroz kuting.",
        parse_mode="Markdown",
    )

    try:
        feedback, model_used, elapsed_ms = await writing_agent.analyze(text, task_type)

        if db:
            submission_doc = {
                "user_id": user.id,
                "submission_type": "writing",
                "original_text": text[:3000],
                "feedback": feedback.model_dump(),
                "overall_band": feedback.overall_band,
                "word_count": word_count,
                "model_used": model_used,
                "processing_time_ms": elapsed_ms,
                "created_at": datetime.utcnow(),
            }
            await db.save_submission(submission_doc)

        await processing_msg.delete()

        feedback_text = format_writing_feedback(feedback, word_count)
        if len(feedback_text) > MAX_MESSAGE_LENGTH:
            feedback_text = feedback_text[:MAX_MESSAGE_LENGTH] + "\n\n_(Matn qisqartirildi)_"
        await update.message.reply_text(feedback_text, parse_mode="Markdown")

        if feedback.corrected_text:
            corrected = format_corrected_writing(feedback)
            if len(corrected) > MAX_MESSAGE_LENGTH:
                corrected = corrected[:MAX_MESSAGE_LENGTH] + "..."
            await update.message.reply_text(corrected, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Writing analysis error (user {user.id}): {e}", exc_info=True)
        await processing_msg.edit_text(
            "❌ Tahlil jarayonida xatolik yuz berdi.\n\nIltimos, keyinroq urinib ko'ring yoki /help ni bosing."
        )
