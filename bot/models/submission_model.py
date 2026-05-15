from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional, Union
from .feedback_model import WritingFeedback, SpeakingFeedback


class SubmissionModel(BaseModel):
    user_id: int
    submission_type: Literal["writing", "speaking"]
    original_text: str
    feedback: Union[WritingFeedback, SpeakingFeedback]
    overall_band: float = Field(ge=0, le=9)
    word_count: int = 0
    duration_seconds: Optional[int] = None
    model_used: str = ""
    processing_time_ms: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SubmissionSummary(BaseModel):
    submission_type: Literal["writing", "speaking"]
    overall_band: float
    created_at: datetime
    word_count: int = 0
    task_type: Optional[str] = None
