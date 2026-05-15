from pydantic import BaseModel, Field
from typing import Literal


class ErrorItem(BaseModel):
    original: str
    corrected: str
    error_type: Literal["grammar", "vocabulary", "cohesion", "task_achievement", "pronunciation", "fluency"]
    explanation_uz: str


class WritingFeedback(BaseModel):
    task_type: Literal["task1", "task2"]
    task_achievement: float = Field(ge=0, le=9)
    coherence_cohesion: float = Field(ge=0, le=9)
    lexical_resource: float = Field(ge=0, le=9)
    grammatical_accuracy: float = Field(ge=0, le=9)
    overall_band: float = Field(ge=0, le=9)
    errors: list[ErrorItem] = Field(default_factory=list)
    corrected_text: str = ""
    strength_uz: str = ""
    weakness_uz: str = ""
    suggestions_uz: list[str] = Field(default_factory=list)

    @staticmethod
    def calculate_overall(ta: float, cc: float, lr: float, gra: float) -> float:
        avg = (ta + cc + lr + gra) / 4
        return round(avg * 2) / 2


class SpeakingFeedback(BaseModel):
    transcript: str
    fluency_coherence: float = Field(ge=0, le=9)
    lexical_resource: float = Field(ge=0, le=9)
    grammatical_accuracy: float = Field(ge=0, le=9)
    pronunciation: float = Field(ge=0, le=9)
    overall_band: float = Field(ge=0, le=9)
    errors: list[ErrorItem] = Field(default_factory=list)
    corrected_transcript: str = ""
    strength_uz: str = ""
    weakness_uz: str = ""
    suggestions_uz: list[str] = Field(default_factory=list)

    @staticmethod
    def calculate_overall(fc: float, lr: float, gra: float, p: float) -> float:
        avg = (fc + lr + gra + p) / 4
        return round(avg * 2) / 2
