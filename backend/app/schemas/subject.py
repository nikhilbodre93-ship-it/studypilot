from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class SubjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=255, description="Subject name")
    description: Optional[str] = Field(default=None, description="Detailed subject description")
    exam_date: Optional[date] = Field(default=None, description="Upcoming exam date")
    color: str = Field(default="#2F5D46", max_length=32, description="Hex or CSS color")


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    exam_date: Optional[date] = None
    color: Optional[str] = Field(default=None, max_length=32)


class SubjectResponse(SubjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    topic_count: int = 0
