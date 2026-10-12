from datetime import datetime
from typing import Optional, Literal, Dict
from pydantic import BaseModel, Field, ConfigDict


class StudySessionBase(BaseModel):
    subject_id: Optional[int] = None
    topic_id: Optional[int] = None
    duration_minutes: int = Field(ge=1, le=720, description="Duration in minutes")
    session_type: Literal["pomodoro", "review", "quiz", "free"] = "pomodoro"
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None


class StudySessionCreate(StudySessionBase):
    pass


class StudySessionResponse(StudySessionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    subject_name: Optional[str] = None
    topic_name: Optional[str] = None


class StudySessionSummaryResponse(BaseModel):
    total_sessions: int
    total_minutes: int
    total_hours: float
    by_type: Dict[str, int]
