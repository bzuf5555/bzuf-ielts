import logging
from .base_agent import BaseAgent
from .router_agent import RouterAgent
from ..models.feedback_model import SpeakingFeedback, ErrorItem
from ..utils.prompts import SPEAKING_SYSTEM, build_speaking_prompt
from ..utils.validators import count_words

logger = logging.getLogger(__name__)


class SpeakingAgent(BaseAgent):
    def __init__(self, groq_service):
        super().__init__(groq_service)
        self.router = RouterAgent()

    async def analyze(self, transcript: str, duration_seconds: float) -> tuple[SpeakingFeedback, str, int]:
        """
        Analyze an IELTS speaking transcript.
        Returns (SpeakingFeedback, model_used, processing_time_ms).
        """
        word_count = count_words(transcript)
        model, max_tokens = self.router.route_speaking(word_count, duration_seconds)
        user_prompt = build_speaking_prompt(transcript, int(duration_seconds))

        data, elapsed_ms = await self.groq.complete_json(
            system_prompt=SPEAKING_SYSTEM,
            user_prompt=user_prompt,
            model=model,
            max_tokens=max_tokens,
        )
        feedback = self._parse_speaking_response(data, transcript)
        return feedback, model, elapsed_ms

    def _parse_speaking_response(self, data: dict, original_transcript: str) -> SpeakingFeedback:
        fc = self._validate_band_score(data.get("fluency_coherence"), "fluency_coherence")
        lr = self._validate_band_score(data.get("lexical_resource"), "lexical_resource")
        gra = self._validate_band_score(data.get("grammatical_accuracy"), "grammatical_accuracy")
        p = self._validate_band_score(data.get("pronunciation"), "pronunciation")

        raw_overall = data.get("overall_band")
        if raw_overall is not None:
            overall = self._validate_band_score(raw_overall, "overall_band")
        else:
            overall = SpeakingFeedback.calculate_overall(fc, lr, gra, p)

        errors_raw = data.get("errors", [])
        if not isinstance(errors_raw, list):
            errors_raw = []
        error_items = [ErrorItem(**e) for e in self._parse_errors(errors_raw)]

        return SpeakingFeedback(
            transcript=original_transcript[:2000],
            fluency_coherence=fc,
            lexical_resource=lr,
            grammatical_accuracy=gra,
            pronunciation=p,
            overall_band=overall,
            errors=error_items,
            corrected_transcript=self._safe_str(data.get("corrected_transcript"), 2500),
            strength_uz=self._safe_str(data.get("strength_uz"), 400),
            weakness_uz=self._safe_str(data.get("weakness_uz"), 400),
            suggestions_uz=self._safe_list(data.get("suggestions_uz"), 5),
        )
