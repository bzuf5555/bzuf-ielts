from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import ContextTypes

# ─── Keyboard button labels ───────────────────────────────────────
BTN_PART1 = "📝 Part 1"
BTN_PART2 = "🎯 Part 2"
BTN_PART3 = "💬 Part 3"
BTN_STATS = "📊 Statistika"
BTN_HISTORY = "📚 Tarix"
BTN_HELP = "ℹ️ Yordam"

CONTACT_REQUEST_TEXT = """👋 Assalomu aleykum, *{name}*!

🎯 Men *BZUF IELTS Bot* — IELTS imtihoniga tayyorlanishingizga yordam beruvchi AI yordamchi.

📱 Botdan foydalanish uchun telefon raqamingizni ulashing.
Pastdagi tugmani bosing 👇"""

WELCOME_TEXT = """✅ *Telefon raqam saqlandi!*

👋 Xush kelibsiz, *{name}*!

📚 *Nima qila olaman?*

✍️ *Writing:* Ingliz tilida esse yuboring → IELTS bali + tahlil
🎤 *Speaking:* Pastdagi tugmalardan Part tanlang → savol oling → ovoz yuboring

Boshlash uchun quyidagi tugmalardan birini bosing 👇"""

ALREADY_REGISTERED_TEXT = """👋 Xush kelibsiz, *{name}*!

🎤 Speaking uchun pastdagi tugmalardan Part tanlang.
✍️ Writing uchun ingliz tilida esse yuboring."""

HELP_TEXT = """ℹ️ *BZUF IELTS Bot — Yordam*

*Speaking (pastki tugmalar):*
• 📝 Part 1 — Tanish mavzular (20-45s)
• 🎯 Part 2 — Cue Card (60-120s)
• 💬 Part 3 — Munozara (30-60s)

*Writing (matn yuboring):*
• Ingliz tilida esse yuboring
• Task 1: 150-200 so'z
• Task 2: 250-350 so'z

*IELTS Ball Tizimi (0-9):*
• 9.0 — Mutaxassis | 8.0 — Juda yaxshi
• 7.0 — Yaxshi | 6.0 — Vakolatli
• 5.0 — Oddiy | 4.0 — Cheklangan

*Buyruqlar:*
/start /help /history /stats /speaking"""


def main_keyboard():
    """Persistent bottom keyboard shown to all registered users."""
    return ReplyKeyboardMarkup(
        [
            [BTN_PART1, BTN_PART2, BTN_PART3],
            [BTN_STATS, BTN_HISTORY, BTN_HELP],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def _contact_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Telefon raqamni ulashish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def _info_inline_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✍️ Writing haqida", callback_data="info_writing"),
            InlineKeyboardButton("🎤 Speaking haqida", callback_data="info_speaking"),
        ],
    ])


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or user.username or "Foydalanuvchi"
    db = context.bot_data.get("db")

    if not db:
        await update.message.reply_text("❌ Tizimda xatolik. Keyinroq urinib ko'ring.")
        return

    await db.get_or_create_user(user.id, user.username, user.first_name)
    has_phone = await db.has_phone_number(user.id)

    if not has_phone:
        await update.message.reply_text(
            CONTACT_REQUEST_TEXT.format(name=name),
            parse_mode="Markdown",
            reply_markup=_contact_keyboard(),
        )
    else:
        await update.message.reply_text(
            ALREADY_REGISTERED_TEXT.format(name=name),
            parse_mode="Markdown",
            reply_markup=main_keyboard(),
        )


async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    contact = update.message.contact

    if contact is None:
        return

    if contact.user_id != user.id:
        await update.message.reply_text(
            "❌ Iltimos, faqat o'z telefon raqamingizni ulashing.",
            reply_markup=_contact_keyboard(),
        )
        return

    db = context.bot_data.get("db")
    if db:
        await db.save_phone_number(user.id, contact.phone_number)

    name = user.first_name or user.username or "Foydalanuvchi"
    await update.message.reply_text(
        WELCOME_TEXT.format(name=name),
        parse_mode="Markdown",
        reply_markup=main_keyboard(),
    )
    await update.message.reply_text(
        "Ko'proq ma'lumot uchun 👇",
        reply_markup=_info_inline_keyboard(),
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        HELP_TEXT,
        parse_mode="Markdown",
        reply_markup=main_keyboard(),
    )


async def keyboard_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles bottom keyboard button presses."""
    text = update.message.text

    if text == BTN_HELP:
        await help_handler(update, context)
    elif text == BTN_STATS:
        from .history_handler import stats_handler
        await stats_handler(update, context)
    elif text == BTN_HISTORY:
        from .history_handler import history_handler
        await history_handler(update, context)
    elif text in (BTN_PART1, BTN_PART2, BTN_PART3):
        part_map = {BTN_PART1: 1, BTN_PART2: 2, BTN_PART3: 3}
        part = part_map[text]
        from .speaking_parts_handler import send_part_question
        await send_part_question(update, context, part)


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "noop":
        return
    elif query.data == "info_writing":
        await query.message.reply_text(
            "✍️ *Writing haqida:*\n\nIngliz tilida esse yuboring. Bot Task 1 yoki Task 2 ekanligini avtomatik aniqlab, 4 mezon bo'yicha IELTS bali beradi:\n\n• Vazifani bajarish\n• Izchillik va bog'liqlik\n• Leksik boylik\n• Grammatik to'g'rilik\n\n*Task 1 (150-200 so'z):* Grafik, jadval, jarayon\n*Task 2 (250-350 so'z):* Esse, fikr-mulohaza",
            parse_mode="Markdown",
        )
    elif query.data == "info_speaking":
        await query.message.reply_text(
            "🎤 *Speaking haqida:*\n\nPastdagi tugmalardan Part tanlang, savol oling va ovozli xabar yuboring.\n\n• 📝 Part 1 — Qisqa javoblar (20-45s)\n• 🎯 Part 2 — Uzun nutq (60-120s)\n• 💬 Part 3 — Munozara (30-60s)",
            parse_mode="Markdown",
        )
    elif query.data == "show_stats":
        db = context.bot_data.get("db")
        if db:
            from ..utils.formatters import format_stats
            stats = await db.get_user_stats(query.from_user.id)
            await query.message.reply_text(format_stats(stats), parse_mode="Markdown")
    elif query.data == "speaking_menu":
        from .speaking_parts_handler import speaking_menu_handler
        await speaking_menu_handler(update, context)
