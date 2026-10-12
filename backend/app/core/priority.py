from typing import Optional, Dict, Any, List
from datetime import datetime, date, timezone
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.subject import Subject
from app.models.topic import Topic
from app.models.topic_mastery import TopicMastery
from app.models.flashcard import Flashcard
from app.models.quiz import Quiz, QuizAttempt, AttemptAnswer, Question


class PriorityWeights(BaseModel):
    w_mastery: float = 0.35
    w_quiz_error: float = 0.20
    w_overdue_cards: float = 0.15
    w_difficulty: float = 0.10
    w_forgetting: float = 0.20


class TopicPriorityBreakdown(BaseModel):
    topic_id: int
    topic_name: str
    subject_id: int
    subject_name: str
    priority_score: float
    base_score: float
    exam_proximity_multiplier: float
    is_exam_mode: bool
    days_until_exam: Optional[int]
    components: Dict[str, float]
    raw_metrics: Dict[str, Any]
    reason: str


def compute_exam_multiplier(exam_date: Optional[date], current_date: Optional[date] = None) -> tuple[float, Optional[int], bool]:
    """Calculate the urgency multiplier and days remaining for an exam."""
    if not exam_date:
        return 1.0, None, False

    today = current_date or date.today()
    days = (exam_date - today).days

    if days < 0:
        # Exam passed: lower urgency compared to upcoming active exams
        return 0.4, days, False
    elif days == 0:
        # Exam is today: maximum urgency
        return 3.0, 0, True
    elif days <= 7:
        # Final week before exam: Exam Mode active (1.5x - 2.5x)
        multiplier = round(1.5 + ((7.0 - days) / 7.0) * 1.0, 3)
        return multiplier, days, True
    elif days <= 30:
        # Moderate proximity (1.0x - 1.5x)
        multiplier = round(1.0 + ((30.0 - days) / 30.0) * 0.5, 3)
        return multiplier, days, False
    else:
        return 1.0, days, False


def calculate_topic_priority(
    db: Session,
    user_id: int,
    topic: Topic,
    weights: Optional[PriorityWeights] = None,
    current_time: Optional[datetime] = None
) -> TopicPriorityBreakdown:
    w = weights or PriorityWeights()
    now = current_time or datetime.now(timezone.utc)
    today = now.date()

    subject = topic.subject
    subject_name = subject.name if subject else "General"
    exam_date = subject.exam_date if subject else None

    # 1. Fetch or initialize Mastery
    mastery = topic.mastery
    score = mastery.score if mastery else 0.0
    attempts = mastery.review_count if mastery else 0
    p_mastery = mastery.p_mastery if mastery else 0.2
    observed_acc = mastery.observed_accuracy if mastery else 0.0

    mastery_component = max(0.0, min(1.0, 1.0 - (score / 100.0)))

    # 2. Quiz error rate component
    # Query recent quiz attempts for this topic
    recent_attempts = (
        db.query(QuizAttempt)
        .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
        .filter(Quiz.topic_id == topic.id, QuizAttempt.user_id == user_id)
        .order_by(QuizAttempt.created_at.desc())
        .limit(3)
        .all()
    )

    if recent_attempts:
        total_score = sum(a.score for a in recent_attempts)
        total_max = sum(a.max_score for a in recent_attempts if a.max_score > 0)
        recent_acc = (total_score / total_max) if total_max > 0 else 0.5
        quiz_error_component = max(0.0, min(1.0, 1.0 - recent_acc))
    elif mastery and mastery.observed_total > 0:
        quiz_error_component = max(0.0, min(1.0, 1.0 - observed_acc))
    else:
        # No attempts yet
        quiz_error_component = mastery_component

    # 3. Overdue flashcards component
    overdue_count = (
        db.query(func.count(Flashcard.id))
        .filter(
            Flashcard.topic_id == topic.id,
            Flashcard.user_id == user_id,
            Flashcard.due_date.isnot(None),
            Flashcard.due_date <= now
        )
        .scalar() or 0
    )
    overdue_cards_component = min(1.0, overdue_count / 5.0)

    # 4. Difficulty component
    difficulty_map = {"easy": 0.33, "medium": 0.66, "hard": 1.00}
    difficulty_component = difficulty_map.get(topic.difficulty.lower(), 0.66)

    # 5. Days since last study (forgetting curve)
    last_studied = mastery.last_reviewed_at if mastery else None
    if last_studied:
        if last_studied.tzinfo is None and now.tzinfo is not None:
            last_studied = last_studied.replace(tzinfo=timezone.utc)
        elif last_studied.tzinfo is not None and now.tzinfo is None:
            last_studied = last_studied.replace(tzinfo=None)
        days_since = max(0, (now - last_studied).days)
        forgetting_component = min(1.0, days_since / 14.0)
    else:
        days_since = 999
        forgetting_component = 1.0

    # 6. Exam proximity multiplier
    exam_multiplier, days_until_exam, is_exam_mode = compute_exam_multiplier(exam_date, today)

    # Base weighted sum
    base_score = (
        w.w_mastery * mastery_component +
        w.w_quiz_error * quiz_error_component +
        w.w_overdue_cards * overdue_cards_component +
        w.w_difficulty * difficulty_component +
        w.w_forgetting * forgetting_component
    )

    final_priority = round(base_score * exam_multiplier, 4)

    # Build human-readable reason
    reason_parts = []
    reason_parts.append(f"Mastery {round(score, 1)}% after {attempts} attempts")

    if quiz_error_component > 0:
        reason_parts.append(f"recent error rate {round(quiz_error_component * 100)}%")

    if overdue_count > 0:
        reason_parts.append(f"{overdue_count} card{'s' if overdue_count != 1 else ''} overdue")

    if days_until_exam is not None:
        if days_until_exam == 0:
            reason_parts.append("exam TODAY")
        elif days_until_exam > 0:
            reason_parts.append(f"exam in {days_until_exam} day{'s' if days_until_exam != 1 else ''}")
        else:
            reason_parts.append("exam completed")
    else:
        reason_parts.append("no exam date")

    if is_exam_mode:
        reason_parts.append("Exam Mode active")

    reason_str = ", ".join(reason_parts)

    return TopicPriorityBreakdown(
        topic_id=topic.id,
        topic_name=topic.name,
        subject_id=topic.subject_id,
        subject_name=subject_name,
        priority_score=final_priority,
        base_score=round(base_score, 4),
        exam_proximity_multiplier=exam_multiplier,
        is_exam_mode=is_exam_mode,
        days_until_exam=days_until_exam,
        components={
            "mastery": round(mastery_component, 4),
            "quiz_error": round(quiz_error_component, 4),
            "overdue_cards": round(overdue_cards_component, 4),
            "difficulty": round(difficulty_component, 4),
            "forgetting": round(forgetting_component, 4),
        },
        raw_metrics={
            "score": score,
            "attempts": attempts,
            "observed_accuracy": observed_acc,
            "overdue_cards_count": overdue_count,
            "days_since_last_study": days_since if days_since != 999 else None,
            "difficulty": topic.difficulty,
            "days_until_exam": days_until_exam,
        },
        reason=reason_str,
    )
