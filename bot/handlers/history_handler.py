from telegram import Update
from telegram.ext import ContextTypes
from ..utils.formatters import format_history, format_stats


async def history_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = context.bot_data.get("db")
    if not db:
        await update.message.reply_text("❌ Ma'lumotlar bazasiga ulanishda xatolik.")
        return
    await db.get_or_create_user(user.id, user.username, user.first_name)
    submissions = await db.get_user_history(user.id, limit=5)
    await update.message.reply_text(format_history(submissions), parse_mode="Markdown")


async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = context.bot_data.get("db")
    if not db:
        await update.message.reply_text("❌ Ma'lumotlar bazasiga ulanishda xatolik.")
        return
    await db.get_or_create_user(user.id, user.username, user.first_name)
    stats = await db.get_user_stats(user.id)
    await update.message.reply_text(format_stats(stats), parse_mode="Markdown")
