from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class MasteryRecordRequest(BaseModel):
    topic_id: int
    event_type: Literal["quiz_answer", "card_rating"]
    is_correct: Optional[bool] = None
    rating: Optional[int] = Field(default=None, ge=1, le=5, description="1-5 rating for flashcards")
    flashcard_id: Optional[int] = None
    review_duration_ms: Optional[int] = 0


class MasteryRecordResponse(BaseModel):
    topic_id: int
    new_mastery_score: float
    p_mastery: float
    observed_accuracy: float
    observed_correct: int
    observed_total: int
    review_count: int
    last_reviewed_at: datetime
    # SM-2 card result if card rating was submitted
    card_id: Optional[int] = None
    card_ease_factor: Optional[float] = None
    card_interval_days: Optional[int] = None
    card_repetitions: Optional[int] = None
    card_due_date: Optional[datetime] = None
