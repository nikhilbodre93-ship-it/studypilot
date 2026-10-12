from datetime import date
from typing import List, Dict, Optional
from pydantic import BaseModel


class UpcomingExamItem(BaseModel):
    subject_id: int
    subject_name: str
    exam_date: date
    days_remaining: int
    is_exam_mode: bool
    color: str


class AnalyticsSummaryResponse(BaseModel):
    overall_mastery_pct: float
    total_subjects: int
    total_topics: int
    mastered_topics_count: int  # score >= 80%
    in_progress_topics_count: int
    total_study_minutes: int
    total_study_sessions: int
    cards_overdue_count: int
    upcoming_exams: List[UpcomingExamItem]


class TopicMasteryItem(BaseModel):
    topic_id: int
    topic_name: str
    difficulty: str
    score: float
    p_mastery: float
    observed_accuracy: float
    observed_total: int
    last_reviewed_at: Optional[str] = None


class SubjectMasteryItem(BaseModel):
    subject_id: int
    subject_name: str
    color: str
    average_mastery: float
    exam_date: Optional[date] = None
    topics: List[TopicMasteryItem]


class AnalyticsMasteryResponse(BaseModel):
    subjects: List[SubjectMasteryItem]


class DayStudyTimeItem(BaseModel):
    date: str
    study_minutes: int
    session_count: int


class StudyTimeByDayResponse(BaseModel):
    days: List[DayStudyTimeItem]
    total_period_minutes: int
