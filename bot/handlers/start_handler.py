from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

START_TEXT = """👋 Assalomu aleykum, *{name}*\\!

🎯 Men *BZUF IELTS Bot* — IELTS imtihoniga tayyorlanishingizga yordam beruvchi AI yordamchi\\.

📚 *Nima qila olaman?*

✍️ *Writing tahlili:*
• Ingliz tilida esse yuboring \\(matn yoki \\.txt hujjat\\)
• Task 1 yoki Task 2 ekanligini avtomatik aniqlayman
• 4 mezon bo'yicha IELTS bali va batafsil tahlil

🎤 *Speaking tahlili:*
• Ovozli xabar yuboring
• Nutqingizni IELTS mezonlari bo'yicha baholayman
• Xatolar, to'g'rilangan variant va maslahatlar

📊 *Tarix va statistika:*
• /history — so'nggi 5 ta tahlil
• /stats — umumiy statistikangiz

⚡ Boshlash uchun esse matnini yoki ovozli xabarni yuboring\\!"""

HELP_TEXT = """ℹ️ *BZUF IELTS Bot — Yordam*

*Buyruqlar:*
• /start — Botni boshlash
• /help — Yordam
• /history — So'nggi tahlillar
• /stats — Statistika

*Writing uchun:*
• Ingliz tilida esse yuboring \\(matn yoki \\.txt hujjat\\)
• Kamida 50 so'z
• Task 1: 150\\-200 so'z \\(grafik, jadval, jarayon, xarita\\)
• Task 2: 250\\-350 so'z \\(esse, fikr\\-mulohaza\\)

*Speaking uchun:*
• Ingliz tilida ovozli xabar yuboring
• Kamida 3 soniya, ko'pi bilan 10 daqiqa

*IELTS Ball Tizimi \\(0\\-9\\):*
• 9\\.0 — Mutaxassis \\(Expert\\)
• 8\\.0 — Juda yaxshi \\(Very Good\\)
• 7\\.0 — Yaxshi \\(Good\\)
• 6\\.0 — Vakolatli \\(Competent\\)
• 5\\.0 — Oddiy \\(Modest\\)
• 4\\.0 — Cheklangan \\(Limited\\)

*4 mezon bo'yicha baholanadi:*
✍️ Writing: Vazifa, Izchillik, Lug'at, Grammatika
🎤 Speaking: Ravonlik, Lug'at, Grammatika, Talaffuz

⚠️ *Eslatma:* Faqat IELTS Writing va Speaking\\."""


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or user.username or "Foydalanuvchi"
    db = context.bot_data.get("db")
    if db:
        await db.get_or_create_user(user.id, user.username, user.first_name)
    keyboard = [
        [
            InlineKeyboardButton("✍️ Writing nima?", callback_data="info_writing"),
            InlineKeyboardButton("🎤 Speaking nima?", callback_data="info_speaking"),
        ],
        [InlineKeyboardButton("📊 Mening statistikam", callback_data="show_stats")],
    ]
    await update.message.reply_text(
        START_TEXT.format(name=name),
        parse_mode="MarkdownV2",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, parse_mode="MarkdownV2")


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "info_writing":
        await query.message.reply_text(
            "✍️ *Writing haqida:*\n\nIngliz tilida esse yuboring\\. Bot Task 1 yoki Task 2 ekanligini avtomatik aniqlab, quyidagi 4 mezon bo'yicha IELTS bali beradi:\n\n• Vazifani bajarish\n• Izchillik va bog'liqlik\n• Leksik boylik\n• Grammatik to'g'rilik\n\n*Task 1 \\(150\\-200 so'z\\):* Grafik, jadval, jarayon yoki xarita tavsifi\n*Task 2 \\(250\\-350 so'z\\):* Esse, fikr\\-mulohaza, munozara",
            parse_mode="MarkdownV2",
        )
    elif query.data == "info_speaking":
        await query.message.reply_text(
            "🎤 *Speaking haqida:*\n\nIngliz tilida ovozli xabar yuboring\\. Bot nutqingizni matnga aylantiradi va 4 mezon bo'yicha IELTS bali beradi:\n\n• Ravonlik va izchillik\n• Leksik boylik\n• Grammatik to'g'rilik\n• Talaffuz",
            parse_mode="MarkdownV2",
        )
    elif query.data == "show_stats":
        db = context.bot_data.get("db")
        if db:
            from ..utils.formatters import format_stats
            stats = await db.get_user_stats(query.from_user.id)
            await query.message.reply_text(format_stats(stats), parse_mode="Markdown")
