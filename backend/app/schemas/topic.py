from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class TopicBase(BaseModel):
    name: str = Field(min_length=1, max_length=255, description="Topic name")
    description: Optional[str] = Field(default=None, description="Topic description or notes")
    difficulty: Literal["easy", "medium", "hard"] = Field(default="medium", description="Topic difficulty")
    order_index: int = Field(default=0, ge=0, description="Display order index")


class TopicCreate(TopicBase):
    pass


class TopicUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    difficulty: Optional[Literal["easy", "medium", "hard"]] = None
    order_index: Optional[int] = Field(default=None, ge=0)


class TopicResponse(TopicBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject_id: int
    created_at: datetime
    updated_at: datetime
    mastery_score: Optional[float] = None
