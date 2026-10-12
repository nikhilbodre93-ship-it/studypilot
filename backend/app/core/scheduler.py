from typing import List, Optional, Dict
from datetime import datetime, date, timedelta, timezone
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models.subject import Subject
from app.models.topic import Topic
from app.models.plan_session import PlanSession
from app.core.priority import calculate_topic_priority, TopicPriorityBreakdown, PriorityWeights


class ScheduledSessionItem(BaseModel):
    topic_id: int
    topic_name: str
    subject_id: int
    subject_name: str
    duration_minutes: int
    session_type: str  # learn, review, quiz, rapid_review, exam_paper
    reason: str
    priority_score: float
    scheduled_order: int
    next_review_date: date


class RevisionQueueResponse(BaseModel):
    available_minutes: int
    total_scheduled_minutes: int
    sessions_count: int
    is_exam_mode_active: bool
    queue: List[ScheduledSessionItem]


def determine_session_type(breakdown: TopicPriorityBreakdown, duration_minutes: int) -> str:
    """Assign appropriate session type based on priority factors and exam mode."""
    days = breakdown.days_until_exam

    if breakdown.is_exam_mode and days is not None:
        if days == 0:
            return "rapid_review"
        elif days <= 3:
            return "exam_paper" if duration_minutes >= 30 else "quiz"
        else:
            return "quiz" if breakdown.components.get("quiz_error", 0) > 0.4 else "rapid_review"

    # Standard mode
    mastery = breakdown.raw_metrics.get("score", 0.0)
    overdue_cards = breakdown.raw_metrics.get("overdue_cards_count", 0)

    if mastery < 40.0:
        return "learn"
    elif mastery < 75.0 or overdue_cards > 0:
        return "review"
    else:
        return "quiz"


def compute_next_review_date(breakdown: TopicPriorityBreakdown, today: date) -> date:
    """Project next review date based on topic retention and exam proximity."""
    days_to_exam = breakdown.days_until_exam
    if days_to_exam is not None and 0 <= days_to_exam <= 3:
        return today + timedelta(days=1)  # Daily review in final countdown

    score = breakdown.raw_metrics.get("score", 0.0)
    if score < 40.0:
        return today + timedelta(days=1)
    elif score < 70.0:
        return today + timedelta(days=3)
    elif score < 85.0:
        return today + timedelta(days=6)
    else:
        return today + timedelta(days=12)


def build_daily_revision_queue(
    db: Session,
    user_id: int,
    available_minutes: int = 60,
    current_time: Optional[datetime] = None,
    weights: Optional[PriorityWeights] = None
) -> RevisionQueueResponse:
    now = current_time or datetime.now(timezone.utc)
    today = now.date()

    # Safety clamp on requested time
    avail_min = max(5, min(720, available_minutes))

    # Fetch all user topics
    topics = (
        db.query(Topic)
        .join(Subject, Topic.subject_id == Subject.id)
        .filter(Subject.user_id == user_id)
        .all()
    )

    if not topics:
        return RevisionQueueResponse(
            available_minutes=avail_min,
            total_scheduled_minutes=0,
            sessions_count=0,
            is_exam_mode_active=False,
            queue=[],
        )

    # Calculate priority for all topics
    breakdowns = [
        calculate_topic_priority(db, user_id, t, weights, now)
        for t in topics
    ]

    # Sort descending by priority score
    breakdowns.sort(key=lambda b: b.priority_score, reverse=True)

    is_exam_mode_active = any(b.is_exam_mode for b in breakdowns)

    # Fit sessions into available_minutes
    scheduled: List[ScheduledSessionItem] = []
    remaining_minutes = avail_min
    order = 1

    # Edge case: very small time window (< 15 mins)
    if avail_min < 15:
        top_topic = breakdowns[0]
        stype = "rapid_review" if top_topic.is_exam_mode else "review"
        scheduled.append(
            ScheduledSessionItem(
                topic_id=top_topic.topic_id,
                topic_name=top_topic.topic_name,
                subject_id=top_topic.subject_id,
                subject_name=top_topic.subject_name,
                duration_minutes=avail_min,
                session_type=stype,
                reason=f"Quick burst session: {top_topic.reason}",
                priority_score=top_topic.priority_score,
                scheduled_order=1,
                next_review_date=compute_next_review_date(top_topic, today),
            )
        )
        return RevisionQueueResponse(
            available_minutes=avail_min,
            total_scheduled_minutes=avail_min,
            sessions_count=1,
            is_exam_mode_active=is_exam_mode_active,
            queue=scheduled,
        )

    # Standard packing
    for b in breakdowns:
        if remaining_minutes < 10:
            break

        # Standard session length: 25 mins (or remaining if less)
        slot_duration = 25
        if remaining_minutes < 25:
            slot_duration = remaining_minutes
        elif remaining_minutes - 25 < 10:
            # Avoid leaving an awkward 5-minute remainder: expand this session
            slot_duration = remaining_minutes

        stype = determine_session_type(b, slot_duration)
        next_review = compute_next_review_date(b, today)

        scheduled.append(
            ScheduledSessionItem(
                topic_id=b.topic_id,
                topic_name=b.topic_name,
                subject_id=b.subject_id,
                subject_name=b.subject_name,
                duration_minutes=slot_duration,
                session_type=stype,
                reason=b.reason,
                priority_score=b.priority_score,
                scheduled_order=order,
                next_review_date=next_review,
            )
        )
        order += 1
        remaining_minutes -= slot_duration

    total_scheduled = sum(s.duration_minutes for s in scheduled)

    return RevisionQueueResponse(
        available_minutes=avail_min,
        total_scheduled_minutes=total_scheduled,
        sessions_count=len(scheduled),
        is_exam_mode_active=is_exam_mode_active,
        queue=scheduled,
    )


def generate_plan_schedule(
    db: Session,
    user_id: int,
    start_date: Optional[date] = None,
    daily_minutes: int = 60,
    days_horizon: int = 14
) -> List[PlanSession]:
    """
    Generate day-by-day revision schedule up to exam dates.
    Inserts newly planned sessions into plan_sessions table.
    """
    today = start_date or date.today()

    # Find maximum upcoming exam date or fallback horizon
    user_subjects = db.query(Subject).filter(Subject.user_id == user_id).all()
    upcoming_exam_dates = [s.exam_date for s in user_subjects if s.exam_date and s.exam_date >= today]

    if upcoming_exam_dates:
        max_date = max(upcoming_exam_dates)
        horizon = min(90, (max_date - today).days + 1)
    else:
        horizon = days_horizon

    horizon = max(1, horizon)

    # Clear pending future plan sessions to allow fresh generation
    db.query(PlanSession).filter(
        PlanSession.user_id == user_id,
        PlanSession.scheduled_date >= today,
        PlanSession.status == "pending"
    ).delete()
    db.commit()

    created_sessions: List[PlanSession] = []

    for d in range(horizon):
        target_day = today + timedelta(days=d)
        sim_time = datetime.combine(target_day, datetime.min.time(), tzinfo=timezone.utc)

        day_queue = build_daily_revision_queue(
            db=db,
            user_id=user_id,
            available_minutes=daily_minutes,
            current_time=sim_time
        )

        for item in day_queue.queue:
            ps = PlanSession(
                user_id=user_id,
                subject_id=item.subject_id,
                topic_id=item.topic_id,
                scheduled_date=target_day,
                scheduled_order=item.scheduled_order,
                duration_minutes=item.duration_minutes,
                session_type=item.session_type,
                status="pending",
                reason=item.reason,
            )
            db.add(ps)
            created_sessions.append(ps)

    db.commit()
    for s in created_sessions:
        db.refresh(s)

    return created_sessions
