import logging
from ..utils.constants import (
    MODEL_FAST, MODEL_MEDIUM, MODEL_BEST,
    WORD_COUNT_FAST, WORD_COUNT_MEDIUM,
    MAX_TOKENS_ANALYSIS, MAX_TOKENS_FAST,
)

logger = logging.getLogger(__name__)


class RouterAgent:
    """Token-saving agent: selects the most cost-effective Groq model
    based on task complexity, saving tokens on simple requests."""

    def route_writing(self, word_count: int, task_type: str) -> tuple[str, int]:
        """Returns (model_name, max_tokens) for a writing analysis task."""
        if task_type == "task2" or word_count > WORD_COUNT_MEDIUM:
            model = MODEL_BEST
            max_tokens = MAX_TOKENS_ANALYSIS
            reason = "Task2/long → best model"
        elif word_count > WORD_COUNT_FAST:
            model = MODEL_MEDIUM
            max_tokens = MAX_TOKENS_ANALYSIS
            reason = "Medium length → medium model"
        else:
            # Task 1 short texts still need good model for quality analysis
            model = MODEL_MEDIUM
            max_tokens = MAX_TOKENS_FAST
            reason = "Short Task1 → medium model (quality required)"
        logger.info(f"Writing route: {word_count}w, {task_type} → {model} ({reason})")
        return model, max_tokens

    def route_speaking(self, word_count: int, duration_seconds: float) -> tuple[str, int]:
        """Returns (model_name, max_tokens) for a speaking analysis task."""
        if duration_seconds > 120 or word_count > WORD_COUNT_MEDIUM:
            model = MODEL_BEST
            max_tokens = MAX_TOKENS_ANALYSIS
            reason = "Long speaking → best model"
        elif duration_seconds > 45 or word_count > WORD_COUNT_FAST:
            model = MODEL_MEDIUM
            max_tokens = MAX_TOKENS_ANALYSIS
            reason = "Medium speaking → medium model"
        else:
            model = MODEL_FAST
            max_tokens = MAX_TOKENS_FAST
            reason = "Short speaking → fast model (saves tokens)"
        logger.info(f"Speaking route: {word_count}w, {duration_seconds:.0f}s → {model} ({reason})")
        return model, max_tokens
