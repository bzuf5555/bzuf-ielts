import logging
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..utils.formatters import format_speaking_feedback, format_transcript

logger = logging.getLogger(__name__)
MAX_MESSAGE_LENGTH = 4000

# ─── IELTS Speaking Questions ────────────────────────────────────

PART1_QUESTIONS = [
    "Do you work or are you a student? Tell me about what you do.",
    "What kind of food do you enjoy eating most? Why?",
    "How do you usually spend your weekends?",
    "What type of music do you enjoy listening to? Why?",
    "Do you prefer living in a big city or a small town? Why?",
    "What are your main hobbies or interests?",
    "How often do you use public transport?",
    "Do you enjoy reading? What kind of books or articles do you read?",
    "What do you do to stay healthy?",
    "How important is social media in your daily life?",
    "Do you prefer indoor or outdoor activities? Why?",
    "What is your hometown like? Do you enjoy living there?",
]

PART2_CUES = [
    (
        "Describe a place you have visited that you particularly enjoyed.",
        "• where the place is\n• when you went there\n• what you did there\n• and explain why you enjoyed it so much"
    ),
    (
        "Describe a person who has had a great influence on your life.",
        "• who this person is\n• how long you have known them\n• how they influenced you\n• and explain why their influence was so important"
    ),
    (
        "Describe a time when you worked very hard to achieve something.",
        "• what the goal was\n• how long it took\n• what difficulties you faced\n• and explain how you felt when you achieved it"
    ),
    (
        "Describe a memorable event from your childhood.",
        "• what the event was\n• where and when it took place\n• who was involved\n• and explain why you remember it so well"
    ),
    (
        "Describe a skill you would like to learn in the future.",
        "• what the skill is\n• why you want to learn it\n• how you plan to learn it\n• and explain how it would benefit your life"
    ),
    (
        "Describe an interesting book or film you have recently read or watched.",
        "• what it was about\n• when you read/watched it\n• what you liked most about it\n• and explain why you would recommend it to others"
    ),
    (
        "Describe a time when you helped someone.",
        "• who you helped\n• why they needed help\n• how you helped them\n• and explain how you felt about helping them"
    ),
]

PART3_QUESTIONS = [
    "How important is it for young people to travel abroad?",
    "Do you think technology has made people more or less sociable? Why?",
    "How has the role of education changed in modern society?",
    "What are the advantages and disadvantages of working from home?",
    "How do you think cities will change in the next 50 years?",
    "How important is it to preserve traditional cultures and customs?",
    "Do you think people today are more or less healthy than in the past? Why?",
    "How has social media affected the way people communicate?",
    "What role should governments play in protecting the environment?",
    "Do you think it is better to have a few close friends or many acquaintances?",
    "How has the way people shop changed in recent years?",
    "Is it more important for children to study or to play? Why?",
]

# ─── Time limits per part ────────────────────────────────────────
PART_TIME_LIMITS = {
    1: {"min": 10, "max": 90,  "ideal": "20-45 soniya"},
    2: {"min": 30, "max": 180, "ideal": "60-120 soniya (1-2 daqiqa)"},
    3: {"min": 10, "max": 120, "ideal": "30-60 soniya"},
}

PART_LABELS = {
    1: "📝 Part 1 — Umumiy savollar",
    2: "🎯 Part 2 — Uzun nutq (Cue Card)",
    3: "💬 Part 3 — Munozara",
}


def _parts_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Part 1 — Umumiy savollar (20-45s)", callback_data="speaking_part_1")],
        [InlineKeyboardButton("🎯 Part 2 — Cue Card (60-120s)", callback_data="speaking_part_2")],
        [InlineKeyboardButton("💬 Part 3 — Munozara (30-60s)", callback_data="speaking_part_3")],
    ])


def _retry_keyboard(part: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"🔄 Yana {PART_LABELS[part].split('—')[0].strip()}", callback_data=f"speaking_part_{part}"),
            InlineKeyboardButton("📋 Boshqa part", callback_data="speaking_menu"),
        ],
    ])


async def send_part_question(update: Update, context: ContextTypes.DEFAULT_TYPE, part: int):
    """Send the question/cue card for the given part and save state."""
    limits = PART_TIME_LIMITS[part]

    if part == 1:
        question = random.choice(PART1_QUESTIONS)
        msg = (
            f"📝 *IELTS Speaking — Part 1*\n\n"
            f"❓ *Savol:*\n_{question}_\n\n"
            f"⏱️ Ideal vaqt: *{limits['ideal']}*\n"
            f"🎤 Ovozli xabar yuboring!"
        )
    elif part == 2:
        topic, bullets = random.choice(PART2_CUES)
        question = f"{topic} | {bullets}"
        msg = (
            f"🎯 *IELTS Speaking — Part 2*\n\n"
            f"📋 *Mavzu kartasi:*\n\n"
            f"*{topic}*\n\n"
            f"Quyidagilarni ayting:\n{bullets}\n\n"
            f"⏱️ Ideal vaqt: *{limits['ideal']}*\n"
            f"💡 Gapirish oldidan 1 daqiqa o'ylash mumkin\n"
            f"🎤 Ovozli xabar yuboring!"
        )
    else:
        question = random.choice(PART3_QUESTIONS)
        msg = (
            f"💬 *IELTS Speaking — Part 3*\n\n"
            f"❓ *Savol:*\n_{question}_\n\n"
            f"⏱️ Ideal vaqt: *{limits['ideal']}*\n"
            f"💡 Fikringizni asoslab, misollar keltiring\n"
            f"🎤 Ovozli xabar yuboring!"
        )

    context.user_data["speaking_part"] = part
    context.user_data["speaking_question"] = question

    target = update.callback_query.message if update.callback_query else update.message
    await target.reply_text(msg, parse_mode="Markdown")


async def speaking_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Part 1/2/3 info (now mainly used from /speaking command)."""
    text = (
        "🎤 *IELTS Speaking Amaliyoti*\n\n"
        "Pastdagi tugmalardan Part tanlang:\n\n"
        "📝 *Part 1* — Tanish mavzular (20-45 soniya)\n"
        "🎯 *Part 2* — Cue Card, uzun nutq (60-120 soniya)\n"
        "💬 *Part 3* — Abstrakt savol, munozara (30-60 soniya)"
    )
    target = update.callback_query.message if update.callback_query else update.message
    await target.reply_text(text, parse_mode="Markdown")


async def part_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline Part 1/2/3 callback buttons."""
    query = update.callback_query
    await query.answer()

    data = query.data
    if data == "speaking_menu":
        await speaking_menu_handler(update, context)
        return

    part = int(data.split("_")[-1])
    await send_part_question(update, context, part)


async def handle_parts_voice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    voice,
    db,
    speaking_agent,
    stt_service,
):
    """Called from speaking_handler when user is in parts mode."""
    user = update.effective_user
    part = context.user_data.get("speaking_part")
    question = context.user_data.get("speaking_question", "")
    limits = PART_TIME_LIMITS[part]

    # Time validation
    duration = voice.duration
    if duration < limits["min"]:
        await update.message.reply_text(
            f"⚠️ Ovoz juda qisqa ({duration} soniya).\n"
            f"*{PART_LABELS[part]}* uchun kamida *{limits['min']} soniya* gapiring.\n\n"
            f"Qaytadan urinib ko'ring 👇",
            parse_mode="Markdown",
            reply_markup=_retry_keyboard(part),
        )
        return
    if duration > limits["max"]:
        await update.message.reply_text(
            f"⚠️ Ovoz juda uzun ({duration} soniya). Ko'pi bilan {limits['max']} soniya.",
        )

    processing_msg = await update.message.reply_text(
        f"🎙️ *{PART_LABELS[part]}*\n"
        f"⏱️ {duration} soniya | 🔄 Ovozdan matn ajratilmoqda...",
        parse_mode="Markdown",
    )

    try:
        file = await context.bot.get_file(voice.file_id)
        transcript, audio_duration = await stt_service.process_voice_message(file.file_path)

        await processing_msg.edit_text(
            f"✅ Matn tayyor!\n📊 IELTS Part {part} mezonlari bo'yicha baholanmoqda...",
            parse_mode="Markdown",
        )

        feedback, model_used, elapsed_ms = await speaking_agent.analyze_part(
            transcript, audio_duration, part, question
        )

        # Save to MongoDB
        if db:
            await db.save_submission({
                "user_id": user.id,
                "submission_type": "speaking",
                "speaking_part": part,
                "original_text": transcript[:2000],
                "question": question[:500],
                "feedback": feedback.model_dump(),
                "overall_band": feedback.overall_band,
                "word_count": len(transcript.split()),
                "duration_seconds": int(audio_duration),
                "model_used": model_used,
                "processing_time_ms": elapsed_ms,
                "created_at": datetime.utcnow(),
            })

        # Clear state
        context.user_data.pop("speaking_part", None)
        context.user_data.pop("speaking_question", None)

        await processing_msg.delete()

        # Transcript
        transcript_text = format_transcript(transcript)
        await update.message.reply_text(
            transcript_text[:MAX_MESSAGE_LENGTH], parse_mode="Markdown"
        )

        # Part header + feedback
        header = f"*{PART_LABELS[part]} — Natijalar*\n\n"
        feedback_text = header + format_speaking_feedback(feedback, audio_duration)
        if len(feedback_text) > MAX_MESSAGE_LENGTH:
            feedback_text = feedback_text[:MAX_MESSAGE_LENGTH] + "\n_(qisqartirildi)_"
        await update.message.reply_text(
            feedback_text, parse_mode="Markdown",
            reply_markup=_retry_keyboard(part),
        )

    except ValueError as e:
        await processing_msg.edit_text(f"❌ {str(e)}")
    except Exception as e:
        logger.error(f"Parts voice error (user {user.id}, part {part}): {e}", exc_info=True)
        await processing_msg.edit_text(
            "❌ Tahlil qilishda xatolik yuz berdi. Keyinroq urinib ko'ring."
        )
