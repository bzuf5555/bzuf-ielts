import logging
from .base_agent import BaseAgent
from .router_agent import RouterAgent
from ..models.feedback_model import WritingFeedback, ErrorItem
from ..utils.prompts import WRITING_TASK1_SYSTEM, WRITING_TASK2_SYSTEM, build_writing_prompt
from ..utils.validators import count_words

logger = logging.getLogger(__name__)


class WritingAgent(BaseAgent):
    def __init__(self, groq_service):
        super().__init__(groq_service)
        self.router = RouterAgent()

    async def analyze(self, text: str, task_type: str) -> tuple[WritingFeedback, str, int]:
        """
        Analyze an IELTS writing submission.
        Returns (WritingFeedback, model_used, processing_time_ms).
        """
        word_count = count_words(text)
        model, max_tokens = self.router.route_writing(word_count, task_type)
        system_prompt = WRITING_TASK1_SYSTEM if task_type == "task1" else WRITING_TASK2_SYSTEM
        user_prompt = build_writing_prompt(text, task_type, word_count)

        data, elapsed_ms = await self.groq.complete_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
            max_tokens=max_tokens,
        )
        feedback = self._parse_writing_response(data, task_type)
        return feedback, model, elapsed_ms

    def _parse_writing_response(self, data: dict, task_type: str) -> WritingFeedback:
        ta = self._validate_band_score(data.get("task_achievement"), "task_achievement")
        cc = self._validate_band_score(data.get("coherence_cohesion"), "coherence_cohesion")
        lr = self._validate_band_score(data.get("lexical_resource"), "lexical_resource")
        gra = self._validate_band_score(data.get("grammatical_accuracy"), "grammatical_accuracy")

        raw_overall = data.get("overall_band")
        if raw_overall is not None:
            overall = self._validate_band_score(raw_overall, "overall_band")
        else:
            overall = WritingFeedback.calculate_overall(ta, cc, lr, gra)

        errors_raw = data.get("errors", [])
        if not isinstance(errors_raw, list):
            errors_raw = []
        error_items = [ErrorItem(**e) for e in self._parse_errors(errors_raw)]

        return WritingFeedback(
            task_type=task_type,
            task_achievement=ta,
            coherence_cohesion=cc,
            lexical_resource=lr,
            grammatical_accuracy=gra,
            overall_band=overall,
            errors=error_items,
            corrected_text=self._safe_str(data.get("corrected_text"), 3000),
            strength_uz=self._safe_str(data.get("strength_uz"), 400),
            weakness_uz=self._safe_str(data.get("weakness_uz"), 400),
            suggestions_uz=self._safe_list(data.get("suggestions_uz"), 5),
        )
