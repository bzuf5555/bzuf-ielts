import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from ..utils.validators import validate_voice_duration
from ..utils.formatters import format_speaking_feedback, format_transcript
from .speaking_parts_handler import handle_parts_voice

logger = logging.getLogger(__name__)
MAX_MESSAGE_LENGTH = 4000


async def speaking_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    voice = update.message.voice
    if not voice:
        await update.message.reply_text("❌ Ovozli xabar topilmadi.")
        return

    db = context.bot_data.get("db")
    speaking_agent = context.bot_data.get("speaking_agent")
    stt_service = context.bot_data.get("stt_service")

    if not speaking_agent or not stt_service:
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

    # ── Parts mode: delegate to parts handler ──────────────────
    if context.user_data.get("speaking_part"):
        await handle_parts_voice(update, context, voice, db, speaking_agent, stt_service)
        return

    # ── General speaking mode ───────────────────────────────────
    valid, error_msg = validate_voice_duration(voice.duration)
    if not valid:
        await update.message.reply_text(f"❌ {error_msg}")
        return

    processing_msg = await update.message.reply_text(
        f"🎙️ *Nutq qabul qilindi!*\n⏱️ {voice.duration} soniya\n\n🔄 Ovozdan matn ajratilmoqda...",
        parse_mode="Markdown",
    )

    try:
        file = await context.bot.get_file(voice.file_id)
        transcript, audio_duration = await stt_service.process_voice_message(file.file_path)

        await processing_msg.edit_text(
            "✅ *Matn ajratildi!*\n\n📊 IELTS mezonlari bo'yicha baholanmoqda...",
            parse_mode="Markdown",
        )

        feedback, model_used, elapsed_ms = await speaking_agent.analyze(transcript, audio_duration)

        if db:
            await db.save_submission({
                "user_id": user.id,
                "submission_type": "speaking",
                "original_text": transcript[:2000],
                "feedback": feedback.model_dump(),
                "overall_band": feedback.overall_band,
                "word_count": len(transcript.split()),
                "duration_seconds": int(audio_duration),
                "model_used": model_used,
                "processing_time_ms": elapsed_ms,
                "created_at": datetime.utcnow(),
            })

        await processing_msg.delete()

        transcript_text = format_transcript(transcript)
        await update.message.reply_text(transcript_text[:MAX_MESSAGE_LENGTH], parse_mode="Markdown")

        feedback_text = format_speaking_feedback(feedback, audio_duration)
        if len(feedback_text) > MAX_MESSAGE_LENGTH:
            feedback_text = feedback_text[:MAX_MESSAGE_LENGTH] + "\n_(qisqartirildi)_"
        await update.message.reply_text(feedback_text, parse_mode="Markdown")

    except ValueError as e:
        logger.warning(f"Speaking validation error (user {user.id}): {e}")
        await processing_msg.edit_text(f"❌ {str(e)}")
    except Exception as e:
        logger.error(f"Speaking analysis error (user {user.id}): {e}", exc_info=True)
        await processing_msg.edit_text(
            "❌ Nutqni tahlil qilishda xatolik yuz berdi.\n\nIltimos, keyinroq urinib ko'ring."
        )
