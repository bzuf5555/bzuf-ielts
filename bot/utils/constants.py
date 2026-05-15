BAND_LABELS = {
    9.0: "Mutaxassis foydalanuvchi (Expert)",
    8.5: "Juda yaxshi foydalanuvchi",
    8.0: "Juda yaxshi foydalanuvchi (Very Good)",
    7.5: "Yaxshi foydalanuvchi",
    7.0: "Yaxshi foydalanuvchi (Good)",
    6.5: "Vakolatli foydalanuvchi",
    6.0: "Vakolatli foydalanuvchi (Competent)",
    5.5: "Qisman vakolatli",
    5.0: "Oddiy foydalanuvchi (Modest)",
    4.5: "Cheklangan foydalanuvchi",
    4.0: "Cheklangan foydalanuvchi (Limited)",
    3.5: "Juda cheklangan",
    3.0: "Juda cheklangan (Extremely Limited)",
    2.5: "Aralovchi foydalanuvchi",
    2.0: "Aralovchi foydalanuvchi (Intermittent)",
    1.5: "Foydalanmaydi",
    1.0: "Foydalanmaydi (Non-User)",
    0.5: "Urinib ko'rdi",
    0.0: "Bajarilmadi (Did not attempt)",
}

# Model routing thresholds
WORD_COUNT_FAST = 200
WORD_COUNT_MEDIUM = 400

# Groq model names
MODEL_FAST = "llama3-8b-8192"
MODEL_MEDIUM = "llama-3.1-70b-versatile"
MODEL_BEST = "llama-3.3-70b-versatile"
MODEL_WHISPER = "whisper-large-v3"

# Max tokens per model call
MAX_TOKENS_ANALYSIS = 3000
MAX_TOKENS_FAST = 2000

# Writing word count limits
MIN_WRITING_WORDS = 50
TASK1_MIN_WORDS = 150
TASK2_MIN_WORDS = 250
MAX_WRITING_WORDS = 800

# Voice limits
MAX_VOICE_DURATION = 600  # 10 minutes
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

# Rate limiting
MAX_SUBMISSIONS_PER_HOUR = 10

# History display count
HISTORY_DISPLAY_COUNT = 5


def get_band_emoji(band: float) -> str:
    if band >= 8.0:
        return "🌟"
    elif band >= 7.0:
        return "⭐"
    elif band >= 6.0:
        return "✅"
    elif band >= 5.0:
        return "📈"
    elif band >= 4.0:
        return "⚠️"
    else:
        return "❌"


def get_band_bar(band: float) -> str:
    filled = int(band)
    half = 1 if (band - filled) >= 0.5 else 0
    empty = 9 - filled - half
    return "█" * filled + ("▌" if half else "") + "░" * empty
