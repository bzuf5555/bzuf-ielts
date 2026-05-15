from datetime import datetime
from ..utils.constants import get_band_emoji, get_band_bar, BAND_LABELS
from ..models.feedback_model import WritingFeedback, SpeakingFeedback


def _band_label(band: float) -> str:
    for b in sorted(BAND_LABELS.keys(), reverse=True):
        if band >= b:
            return BAND_LABELS[b]
    return BAND_LABELS[0.0]


def _escape_md(text: str) -> str:
    for ch in ["_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"]:
        text = text.replace(ch, f"\\{ch}")
    return text


def format_writing_feedback(feedback: WritingFeedback, word_count: int) -> str:
    task_label = "Task 1 (Akademik/Umumiy)" if feedback.task_type == "task1" else "Task 2 (Esse)"
    emoji = get_band_emoji(feedback.overall_band)
    label = _band_label(feedback.overall_band)

    lines = [
        f"📝 *IELTS Writing {task_label} Tahlili*",
        "",
        f"{emoji} *Umumiy Ball: {feedback.overall_band}/9* — {label}",
        f"`{get_band_bar(feedback.overall_band)}`",
        "",
        "📊 *Mezonlar bo'yicha:*",
        f"• Vazifani bajarish: *{feedback.task_achievement}* {get_band_emoji(feedback.task_achievement)}",
        f"• Izchillik va Bog'liqlik: *{feedback.coherence_cohesion}* {get_band_emoji(feedback.coherence_cohesion)}",
        f"• Leksik Boylik: *{feedback.lexical_resource}* {get_band_emoji(feedback.lexical_resource)}",
        f"• Grammatik To'g'rilik: *{feedback.grammatical_accuracy}* {get_band_emoji(feedback.grammatical_accuracy)}",
        "",
        f"📏 So'z soni: {word_count}",
    ]

    if feedback.strength_uz:
        lines += ["", "✅ *Kuchli tomonlar:*", feedback.strength_uz]

    if feedback.weakness_uz:
        lines += ["", "⚠️ *Zaif tomonlar:*", feedback.weakness_uz]

    if feedback.errors:
        lines += ["", f"❌ *Xatolar ({min(len(feedback.errors), 8)} ta):*"]
        type_labels = {
            "grammar": "Grammatika",
            "vocabulary": "Lug'at",
            "cohesion": "Bog'liqlik",
            "task_achievement": "Vazifa",
        }
        for i, err in enumerate(feedback.errors[:8], 1):
            type_label = type_labels.get(err.error_type, err.error_type.capitalize())
            lines.append("")
            lines.append(f"*{i}. [{type_label}]*")
            lines.append(f"❌ `{err.original[:120]}`")
            lines.append(f"✅ `{err.corrected[:120]}`")
            if err.explanation_uz:
                lines.append(f"💡 {err.explanation_uz}")

    if feedback.suggestions_uz:
        lines += ["", "💡 *Maslahatlar:*"]
        for tip in feedback.suggestions_uz[:5]:
            lines.append(f"• {tip}")

    return "\n".join(lines)


def format_corrected_writing(feedback: WritingFeedback) -> str:
    if not feedback.corrected_text:
        return ""
    text = feedback.corrected_text[:3500]
    return f"📄 *To'g'irlangan matn:*\n\n{text}"


def format_speaking_feedback(feedback: SpeakingFeedback, duration_seconds: float) -> str:
    emoji = get_band_emoji(feedback.overall_band)
    label = _band_label(feedback.overall_band)
    minutes = int(duration_seconds) // 60
    seconds = int(duration_seconds) % 60
    duration_str = f"{minutes}:{seconds:02d}" if minutes > 0 else f"{seconds} soniya"

    lines = [
        "🎤 *IELTS Speaking Tahlili*",
        "",
        f"{emoji} *Umumiy Ball: {feedback.overall_band}/9* — {label}",
        f"`{get_band_bar(feedback.overall_band)}`",
        "",
        "📊 *Mezonlar bo'yicha:*",
        f"• Ravonlik va Izchillik: *{feedback.fluency_coherence}* {get_band_emoji(feedback.fluency_coherence)}",
        f"• Leksik Boylik: *{feedback.lexical_resource}* {get_band_emoji(feedback.lexical_resource)}",
        f"• Grammatik To'g'rilik: *{feedback.grammatical_accuracy}* {get_band_emoji(feedback.grammatical_accuracy)}",
        f"• Talaffuz: *{feedback.pronunciation}* {get_band_emoji(feedback.pronunciation)}",
        "",
        f"⏱️ Davomiyligi: {duration_str}",
    ]

    if feedback.strength_uz:
        lines += ["", "✅ *Kuchli tomonlar:*", feedback.strength_uz]

    if feedback.weakness_uz:
        lines += ["", "⚠️ *Zaif tomonlar:*", feedback.weakness_uz]

    if feedback.errors:
        lines += ["", f"❌ *Xatolar ({min(len(feedback.errors), 8)} ta):*"]
        type_labels = {
            "grammar": "Grammatika",
            "vocabulary": "Lug'at",
            "fluency": "Ravonlik",
            "pronunciation": "Talaffuz",
        }
        for i, err in enumerate(feedback.errors[:8], 1):
            type_label = type_labels.get(err.error_type, err.error_type.capitalize())
            lines.append("")
            lines.append(f"*{i}. [{type_label}]*")
            lines.append(f"❌ `{err.original[:120]}`")
            lines.append(f"✅ `{err.corrected[:120]}`")
            if err.explanation_uz:
                lines.append(f"💡 {err.explanation_uz}")

    if feedback.suggestions_uz:
        lines += ["", "💡 *Maslahatlar:*"]
        for tip in feedback.suggestions_uz[:5]:
            lines.append(f"• {tip}")

    return "\n".join(lines)


def format_transcript(transcript: str) -> str:
    preview = transcript[:600] + ("..." if len(transcript) > 600 else "")
    return f"🎙️ *Sizning nutqingiz (matn):*\n\n_{preview}_"


def format_history(submissions: list[dict]) -> str:
    if not submissions:
        return (
            "📭 Hali hech qanday tahlil yo'q.\n\n"
            "Boshlash uchun ingliz tilida esse yuboring yoki ovozli xabar yuboring! ✍️"
        )
    lines = ["📚 *So'nggi tahlillar:*", ""]
    for i, sub in enumerate(submissions, 1):
        sub_type = "✍️ Writing" if sub.get("submission_type") == "writing" else "🎤 Speaking"
        band = sub.get("overall_band", 0)
        emoji = get_band_emoji(band)
        created = sub.get("created_at", datetime.utcnow())
        if isinstance(created, datetime):
            date_str = created.strftime("%d.%m.%Y %H:%M")
        else:
            date_str = str(created)[:16]
        word_count = sub.get("word_count", 0)
        count_str = f" • {word_count} so'z" if word_count else ""
        lines.append(f"{i}. {sub_type} {emoji} *{band}/9*{count_str} — {date_str}")
    return "\n".join(lines)


def format_stats(stats: dict) -> str:
    if not stats or stats.get("total_submissions", 0) == 0:
        return (
            "📊 *Statistika*\n\n"
            "Hali hech qanday tahlil yo'q.\n\n"
            "Boshlash uchun esse yuboring yoki ovozli xabar yuboring! ✍️"
        )
    total = stats.get("total_submissions", 0)
    writing_count = stats.get("writing_count", 0)
    speaking_count = stats.get("speaking_count", 0)
    avg_writing = stats.get("avg_writing_band", 0.0)
    avg_speaking = stats.get("avg_speaking_band", 0.0)
    recent = stats.get("recent_submissions", 0)
    member_since = stats.get("member_since", datetime.utcnow())
    since_str = member_since.strftime("%d.%m.%Y") if isinstance(member_since, datetime) else str(member_since)[:10]

    lines = [
        "📊 *Sizning Statistikangiz*",
        "",
        f"📅 A'zo bo'lgan sana: {since_str}",
        f"🔢 Jami tahlillar: *{total}*",
        f"✍️ Writing: {writing_count} ta",
        f"🎤 Speaking: {speaking_count} ta",
        f"📆 Oxirgi 30 kunda: {recent} ta",
        "",
    ]
    if writing_count > 0:
        lines += [
            "📈 *O'rtacha Writing balli:*",
            f"{get_band_emoji(avg_writing)} *{avg_writing:.1f}/9*",
            f"`{get_band_bar(avg_writing)}`",
            "",
        ]
    if speaking_count > 0:
        lines += [
            "📈 *O'rtacha Speaking balli:*",
            f"{get_band_emoji(avg_speaking)} *{avg_speaking:.1f}/9*",
            f"`{get_band_bar(avg_speaking)}`",
        ]
    return "\n".join(lines)
