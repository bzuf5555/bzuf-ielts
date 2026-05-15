from .constants import MIN_WRITING_WORDS, MAX_WRITING_WORDS, MAX_VOICE_DURATION


def count_words(text: str) -> int:
    return len(text.split())


def is_english_text(text: str) -> bool:
    english_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128)
    total_chars = sum(1 for c in text if c.isalpha())
    if total_chars == 0:
        return False
    return (english_chars / total_chars) > 0.7


def validate_writing_text(text: str) -> tuple[bool, str]:
    word_count = count_words(text)
    if word_count < MIN_WRITING_WORDS:
        return False, f"Matn juda qisqa ({word_count} so'z). Kamida {MIN_WRITING_WORDS} so'z yozing."
    if word_count > MAX_WRITING_WORDS:
        return False, f"Matn juda uzun ({word_count} so'z). Ko'pi bilan {MAX_WRITING_WORDS} so'z yozing."
    if not is_english_text(text):
        return False, "Iltimos, ingliz tilida yozing. Bot faqat ingliz tilini tahlil qiladi."
    return True, ""


def detect_writing_task_type(text: str) -> str:
    text_lower = text.lower()
    task1_keywords = [
        "the chart", "the graph", "the diagram", "the map", "the table",
        "the figure", "the process", "shows", "illustrates", "describes",
        "summarize", "summarise", "the bar", "the pie", "the line",
        "dear sir", "dear madam", "i am writing", "i would like to",
        "write a letter", "write to", "the data", "the information",
        "percentage", "proportion", "compared to", "increased", "decreased"
    ]
    task2_keywords = [
        "discuss", "opinion", "agree", "disagree", "to what extent",
        "advantages", "disadvantages", "causes", "effects", "solutions",
        "some people", "others believe", "it is argued", "it has been suggested",
        "do you think", "how far", "give your", "both views", "in my opinion",
        "nowadays", "in today's society", "many people argue", "it is widely believed"
    ]
    task1_score = sum(1 for kw in task1_keywords if kw in text_lower)
    task2_score = sum(1 for kw in task2_keywords if kw in text_lower)
    if task1_score > task2_score:
        return "task1"
    elif task2_score > task1_score:
        return "task2"
    word_count = count_words(text)
    return "task1" if word_count < 200 else "task2"


def validate_voice_duration(duration: int) -> tuple[bool, str]:
    if duration > MAX_VOICE_DURATION:
        return False, f"Audio juda uzun ({duration // 60} daqiqa). Ko'pi bilan 10 daqiqa."
    if duration < 3:
        return False, "Audio juda qisqa. Kamida 3 soniya gapiring."
    return True, ""
