from typing import List, Dict
from datetime import datetime, date, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.topic_mastery import TopicMastery
from app.models.flashcard import Flashcard
from app.models.study_session import StudySession
from app.schemas.analytics import (
    AnalyticsSummaryResponse,
    UpcomingExamItem,
    AnalyticsMasteryResponse,
    SubjectMasteryItem,
    TopicMasteryItem,
    StudyTimeByDayResponse,
    DayStudyTimeItem,
)
from app.core.priority import compute_exam_multiplier
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    now = datetime.now(timezone.utc)
    today = now.date()

    # Subjects and Topics
    subjects = db.query(Subject).filter(Subject.user_id == current_user.id).all()
    topics = (
        db.query(Topic)
        .join(Subject, Topic.subject_id == Subject.id)
        .filter(Subject.user_id == current_user.id)
        .all()
    )

    topic_ids = [t.id for t in topics]
    masteries = (
        db.query(TopicMastery)
        .filter(TopicMastery.topic_id.in_(topic_ids), TopicMastery.user_id == current_user.id)
        .all()
    ) if topic_ids else []

    mastery_scores = [m.score for m in masteries]
    overall_mastery = round(sum(mastery_scores) / len(mastery_scores), 1) if mastery_scores else 0.0

    mastered_count = sum(1 for s in mastery_scores if s >= 80.0)
    in_progress_count = len(topics) - mastered_count

    # Study Sessions stats
    study_sessions = db.query(StudySession).filter(StudySession.user_id == current_user.id).all()
    total_minutes = sum(s.duration_minutes for s in study_sessions)
    total_sessions_count = len(study_sessions)

    # Overdue flashcards
    overdue_cards = (
        db.query(func.count(Flashcard.id))
        .filter(
            Flashcard.user_id == current_user.id,
            Flashcard.due_date.isnot(None),
            Flashcard.due_date <= now
        )
        .scalar() or 0
    )

    # Upcoming exams
    upcoming_exams: List[UpcomingExamItem] = []
    for s in subjects:
        if s.exam_date:
            _, days, is_exam_mode = compute_exam_multiplier(s.exam_date, today)
            if days is not None and days >= 0:
                upcoming_exams.append(
                    UpcomingExamItem(
                        subject_id=s.id,
                        subject_name=s.name,
                        exam_date=s.exam_date,
                        days_remaining=days,
                        is_exam_mode=is_exam_mode,
                        color=s.color,
                    )
                )

    upcoming_exams.sort(key=lambda x: x.days_remaining)

    return AnalyticsSummaryResponse(
        overall_mastery_pct=overall_mastery,
        total_subjects=len(subjects),
        total_topics=len(topics),
        mastered_topics_count=mastered_count,
        in_progress_topics_count=in_progress_count,
        total_study_minutes=total_minutes,
        total_study_sessions=total_sessions_count,
        cards_overdue_count=overdue_cards,
        upcoming_exams=upcoming_exams,
    )


@router.get("/mastery", response_model=AnalyticsMasteryResponse)
def get_analytics_mastery(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subjects = db.query(Subject).filter(Subject.user_id == current_user.id).order_by(Subject.name.asc()).all()
    subject_items: List[SubjectMasteryItem] = []

    for s in subjects:
        topics = db.query(Topic).filter(Topic.subject_id == s.id).order_by(Topic.order_index.asc()).all()
        topic_items: List[TopicMasteryItem] = []
        topic_scores: List[float] = []

        for t in topics:
            m = db.query(TopicMastery).filter(TopicMastery.topic_id == t.id, TopicMastery.user_id == current_user.id).first()
            score = m.score if m else 0.0
            p_mastery = m.p_mastery if m else 0.2
            obs_acc = m.observed_accuracy if m else 0.0
            obs_tot = m.observed_total if m else 0
            last_rev = m.last_reviewed_at.isoformat() if (m and m.last_reviewed_at) else None

            topic_scores.append(score)
            topic_items.append(
                TopicMasteryItem(
                    topic_id=t.id,
                    topic_name=t.name,
                    difficulty=t.difficulty,
                    score=score,
                    p_mastery=p_mastery,
                    observed_accuracy=obs_acc,
                    observed_total=obs_tot,
                    last_reviewed_at=last_rev,
                )
            )

        avg_mastery = round(sum(topic_scores) / len(topic_scores), 1) if topic_scores else 0.0
        subject_items.append(
            SubjectMasteryItem(
                subject_id=s.id,
                subject_name=s.name,
                color=s.color,
                average_mastery=avg_mastery,
                exam_date=s.exam_date,
                topics=topic_items,
            )
        )

    return AnalyticsMasteryResponse(subjects=subject_items)


@router.get("/study-time-by-day", response_model=StudyTimeByDayResponse)
def get_study_time_by_day(
    days: int = Query(default=14, ge=1, le=90, description="Number of past days to query"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    today = date.today()
    start_date = today - timedelta(days=days - 1)

    # Fetch sessions completed or created within the range
    sessions = (
        db.query(StudySession)
        .filter(
            StudySession.user_id == current_user.id,
            StudySession.created_at >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc)
        )
        .all()
    )

    day_map: Dict[str, Dict[str, int]] = {
        (start_date + timedelta(days=i)).isoformat(): {"minutes": 0, "count": 0}
        for i in range(days)
    }

    for s in sessions:
        s_date = s.created_at.date().isoformat()
        if s_date in day_map:
            day_map[s_date]["minutes"] += s.duration_minutes
            day_map[s_date]["count"] += 1

    items: List[DayStudyTimeItem] = [
        DayStudyTimeItem(
            date=d,
            study_minutes=data["minutes"],
            session_count=data["count"]
        )
        for d, data in sorted(day_map.items())
    ]

    total_period = sum(item.study_minutes for item in items)

    return StudyTimeByDayResponse(
        days=items,
        total_period_minutes=total_period,
    )
