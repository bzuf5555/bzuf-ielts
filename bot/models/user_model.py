from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserModel(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    submission_count: int = 0
    writing_count: int = 0
    speaking_count: int = 0
    avg_writing_band: float = 0.0
    avg_speaking_band: float = 0.0
    last_active: datetime = Field(default_factory=datetime.utcnow)
