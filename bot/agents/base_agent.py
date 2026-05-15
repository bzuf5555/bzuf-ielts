import logging
from typing import Any

logger = logging.getLogger(__name__)

VALID_ERROR_TYPES = {"grammar", "vocabulary", "cohesion", "task_achievement", "pronunciation", "fluency"}


class BaseAgent:
    def __init__(self, groq_service):
        self.groq = groq_service

    def _validate_band_score(self, score: Any, field_name: str = "score") -> float:
        try:
            score = float(score)
        except (TypeError, ValueError):
            logger.warning(f"Invalid band score for {field_name}: {score!r}, defaulting to 5.0")
            return 5.0
        score = max(0.0, min(9.0, score))
        return round(score * 2) / 2

    def _parse_errors(self, errors_raw: list) -> list[dict]:
        parsed = []
        for err in errors_raw[:10]:
            if not isinstance(err, dict):
                continue
            error_type = err.get("error_type", "grammar")
            if error_type not in VALID_ERROR_TYPES:
                error_type = "grammar"
            parsed.append({
                "original": str(err.get("original", ""))[:200].strip(),
                "corrected": str(err.get("corrected", ""))[:200].strip(),
                "error_type": error_type,
                "explanation_uz": str(err.get("explanation_uz", ""))[:300].strip(),
            })
        return [e for e in parsed if e["original"] and e["corrected"]]

    def _safe_str(self, value: Any, max_len: int = 500) -> str:
        if value is None:
            return ""
        return str(value)[:max_len].strip()

    def _safe_list(self, value: Any, max_items: int = 5) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item)[:200].strip() for item in value[:max_items] if item]
