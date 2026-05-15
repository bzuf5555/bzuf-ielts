from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import ContextTypes

# ─── Button labels ────────────────────────────────────────────────
BTN_SPEAKING = "🎤 SPEAKING"
BTN_WRITING  = "✍️ WRITING"
BTN_PART1    = "📝 Part 1"
BTN_PART2    = "🎯 Part 2"
BTN_PART3    = "💬 Part 3"
BTN_TASK1    = "📄 Task 1"
BTN_TASK2    = "✏️ Task 2"
BTN_BACK     = "🔙 Orqaga"
BTN_STATS    = "📊 Statistika"
BTN_HISTORY  = "📚 Tarix"
BTN_HELP     = "ℹ️ Yordam"

# ─── Keyboards ───────────────────────────────────────────────────

def main_keyboard():
    """Main menu: SPEAKING / WRITING + utilities."""
    return ReplyKeyboardMarkup(
        [
            [BTN_SPEAKING, BTN_WRITING],
            [BTN_STATS, BTN_HISTORY, BTN_HELP],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def speaking_keyboard():
    """Speaking sub-menu: Part 1 / Part 2 / Part 3."""
    return ReplyKeyboardMarkup(
        [
            [BTN_PART1, BTN_PART2, BTN_PART3],
            [BTN_BACK],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def writing_keyboard():
    """Writing sub-menu: Task 1 / Task 2."""
    return ReplyKeyboardMarkup(
        [
            [BTN_TASK1, BTN_TASK2],
            [BTN_BACK],
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


# ─── Texts ───────────────────────────────────────────────────────

CONTACT_TEXT = """👋 Assalomu aleykum, *{name}*!

🎯 Men *BZUF IELTS Bot* — IELTS imtihoniga tayyorlanishingizga yordam beruvchi AI yordamchi.

📱 Botdan foydalanish uchun telefon raqamingizni ulashing 👇"""

WELCOME_TEXT = """✅ *Telefon raqam saqlandi!*

👋 Xush kelibsiz, *{name}*!

*Quyidagi tugmalardan boshlang:*
🎤 *SPEAKING* — Part 1, 2 yoki 3 ni tanlang → ovoz yuboring
✍️ *WRITING* — Task 1 yoki Task 2 ni tanlang → esse yuboring"""

ALREADY_REG_TEXT = """👋 Xush kelibsiz, *{name}*!

🎤 *SPEAKING* tugmasini bosing → Part tanlang → ovoz yuboring
✍️ *WRITING* tugmasini bosing → Task tanlang → esse yuboring"""

SPEAKING_MENU_TEXT = """🎤 *SPEAKING — Qaysi qismni mashq qilasiz?*

📝 *Part 1* — Tanish mavzular, qisqa javoblar (20-45s)
🎯 *Part 2* — Cue Card, uzun nutq (60-120s)
💬 *Part 3* — Abstrakt savol, fikr bildirish (30-60s)"""

WRITING_MENU_TEXT = """✍️ *WRITING — Qaysi vazifani bajaryapsiz?*

📄 *Task 1* — Grafik, jadval, jarayon yoki xarita tavsifi (150-200 so'z)
✏️ *Task 2* — Esse, fikr-mulohaza, munozara (250-350 so'z)

Vazifani tanlaganingizdan so'ng ingliz tilida esseni yuboring."""

HELP_TEXT = """ℹ️ *BZUF IELTS Bot — Yordam*

*🎤 SPEAKING → Part 1/2/3:*
• Part 1: Tanish mavzular (20-45s)
• Part 2: Cue Card, uzun nutq (60-120s)
• Part 3: Munozara, abstrakt fikr (30-60s)

*✍️ WRITING → Task 1/2:*
• Task 1: Grafik/Jadval/Jarayon tavsifi (150-200 so'z)
• Task 2: Esse, fikr-mulohaza (250-350 so'z)

*IELTS Ball Tizimi (0-9):*
• 9.0 — Mutaxassis | 8.0 — Juda yaxshi
• 7.0 — Yaxshi | 6.0 — Vakolatli
• 5.0 — Oddiy | 4.0 — Cheklangan

*Buyruqlar:* /start /help /history /stats"""


# ─── Handlers ────────────────────────────────────────────────────

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or user.username or "Foydalanuvchi"
    db = context.bot_data.get("db")
    if not db:
        await update.message.reply_text("❌ Tizimda xatolik.")
        return

    await db.get_or_create_user(user.id, user.username, user.first_name)
    has_phone = await db.has_phone_number(user.id)

    if not has_phone:
        await update.message.reply_text(
            CONTACT_TEXT.format(name=name),
            parse_mode="Markdown",
            reply_markup=_contact_keyboard(),
        )
    else:
        # Clear any leftover state
        context.user_data.clear()
        await update.message.reply_text(
            ALREADY_REG_TEXT.format(name=name),
            parse_mode="Markdown",
            reply_markup=main_keyboard(),
        )


async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    contact = update.message.contact
    if not contact:
        return
    if contact.user_id != user.id:
        await update.message.reply_text(
            "❌ Faqat o'z raqamingizni ulashing.",
            reply_markup=_contact_keyboard(),
        )
        return
    db = context.bot_data.get("db")
    if db:
        await db.save_phone_number(user.id, contact.phone_number)
    name = user.first_name or user.username or "Foydalanuvchi"
    context.user_data.clear()
    await update.message.reply_text(
        WELCOME_TEXT.format(name=name),
        parse_mode="Markdown",
        reply_markup=main_keyboard(),
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        HELP_TEXT, parse_mode="Markdown", reply_markup=main_keyboard()
    )


async def keyboard_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Routes all Reply Keyboard button presses."""
    text = update.message.text

    # ── Main menu ──────────────────────────────────────────────
    if text == BTN_SPEAKING:
        context.user_data.pop("writing_task_type", None)
        await update.message.reply_text(
            SPEAKING_MENU_TEXT,
            parse_mode="Markdown",
            reply_markup=speaking_keyboard(),
        )

    elif text == BTN_WRITING:
        context.user_data.pop("speaking_part", None)
        context.user_data.pop("speaking_question", None)
        await update.message.reply_text(
            WRITING_MENU_TEXT,
            parse_mode="Markdown",
            reply_markup=writing_keyboard(),
        )

    # ── Speaking sub-menu ──────────────────────────────────────
    elif text in (BTN_PART1, BTN_PART2, BTN_PART3):
        part_map = {BTN_PART1: 1, BTN_PART2: 2, BTN_PART3: 3}
        from .speaking_parts_handler import send_part_question
        await send_part_question(update, context, part_map[text])

    # ── Writing sub-menu ───────────────────────────────────────
    elif text == BTN_TASK1:
        context.user_data["writing_task_type"] = "task1"
        await update.message.reply_text(
            "📄 *IELTS Writing — Task 1*\n\n"
            "Grafik, jadval, jarayon yoki xarita tavsifini ingliz tilida yuboring.\n\n"
            "📏 Tavsiya: *150-200 so'z*\n"
            "📝 Matnni yuboring:",
            parse_mode="Markdown",
            reply_markup=writing_keyboard(),
        )

    elif text == BTN_TASK2:
        context.user_data["writing_task_type"] = "task2"
        await update.message.reply_text(
            "✏️ *IELTS Writing — Task 2*\n\n"
            "Esse, fikr-mulohaza yoki munozarani ingliz tilida yuboring.\n\n"
            "📏 Tavsiya: *250-350 so'z*\n"
            "📝 Matnni yuboring:",
            parse_mode="Markdown",
            reply_markup=writing_keyboard(),
        )

    # ── Back ───────────────────────────────────────────────────
    elif text == BTN_BACK:
        context.user_data.pop("writing_task_type", None)
        context.user_data.pop("speaking_part", None)
        context.user_data.pop("speaking_question", None)
        await update.message.reply_text(
            "🏠 Asosiy menyu",
            reply_markup=main_keyboard(),
        )

    # ── Utilities ──────────────────────────────────────────────
    elif text == BTN_STATS:
        from .history_handler import stats_handler
        await stats_handler(update, context)

    elif text == BTN_HISTORY:
        from .history_handler import history_handler
        await history_handler(update, context)

    elif text == BTN_HELP:
        await help_handler(update, context)


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "noop":
        return
    elif query.data == "speaking_menu":
        from .speaking_parts_handler import speaking_menu_handler
        await speaking_menu_handler(update, context)
