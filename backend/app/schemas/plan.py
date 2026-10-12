from datetime import date, datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class PlanGenerateRequest(BaseModel):
    daily_minutes: int = Field(default=60, ge=10, le=480, description="Available study minutes per day")
    start_date: Optional[date] = Field(default=None, description="Start date (default today)")
    days_horizon: int = Field(default=14, ge=1, le=90, description="Planning horizon if no upcoming exams")


class PlanSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    subject_id: Optional[int]
    topic_id: int
    scheduled_date: date
    scheduled_order: int
    duration_minutes: int
    session_type: str
    status: str
    reason: Optional[str]
    created_at: datetime
    subject_name: Optional[str] = None
    topic_name: Optional[str] = None


class PlanSessionUpdateRequest(BaseModel):
    status: Literal["pending", "completed", "skipped"] = Field(..., description="New session status")
    notes: Optional[str] = None


class PlanGenerateResponse(BaseModel):
    message: str
    total_sessions_created: int
    start_date: date
    end_date: date
