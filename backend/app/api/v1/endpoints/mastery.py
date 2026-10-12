from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.topic import Topic
from app.models.subject import Subject
from app.models.flashcard import Flashcard, CardReview
from app.schemas.mastery import MasteryRecordRequest, MasteryRecordResponse
from app.core.bkt import record_topic_evidence
from app.core.sm2 import calculate_sm2
from app.core.exceptions import NotFoundException, BadRequestException
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/record", response_model=MasteryRecordResponse, status_code=status.HTTP_200_OK)
def record_learning_event(
    payload: MasteryRecordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify topic exists and belongs to current user
    topic = (
        db.query(Topic)
        .join(Subject, Topic.subject_id == Subject.id)
        .filter(Topic.id == payload.topic_id, Subject.user_id == current_user.id)
        .first()
    )
    if not topic:
        raise NotFoundException("Topic", payload.topic_id)

    # Determine correctness
    if payload.event_type == "quiz_answer":
        if payload.is_correct is None:
            raise BadRequestException("'is_correct' boolean is required for quiz_answer events.")
        is_correct = payload.is_correct
    elif payload.event_type == "card_rating":
        if payload.rating is None:
            raise BadRequestException("'rating' integer (1-5) is required for card_rating events.")
        # Rating 3, 4, 5 considered successful recall
        is_correct = payload.rating >= 3
    else:
        raise BadRequestException(f"Unsupported event_type '{payload.event_type}'.")

    # 1. Update BKT Topic Mastery
    mastery = record_topic_evidence(
        db=db,
        user_id=current_user.id,
        topic_id=payload.topic_id,
        is_correct=is_correct,
    )

    card_result = None
    # 2. Update Flashcard SM-2 if flashcard_id provided
    if payload.event_type == "card_rating" and payload.flashcard_id is not None:
        card = db.query(Flashcard).filter(
            Flashcard.id == payload.flashcard_id,
            Flashcard.user_id == current_user.id,
            Flashcard.topic_id == payload.topic_id
        ).first()

        if card:
            now = datetime.now(timezone.utc)
            sm2_calc = calculate_sm2(
                rating=payload.rating,
                current_ease_factor=card.ease_factor,
                current_repetitions=card.repetitions,
                current_interval=card.interval_days,
                review_date=now
            )
            card.ease_factor = sm2_calc.ease_factor
            card.repetitions = sm2_calc.repetitions
            card.interval_days = sm2_calc.interval_days
            card.due_date = sm2_calc.due_date
            card.last_reviewed_at = now

            # Record CardReview log
            review_entry = CardReview(
                flashcard_id=card.id,
                user_id=current_user.id,
                rating=payload.rating,
                review_duration_ms=payload.review_duration_ms or 0,
                reviewed_at=now,
            )
            db.add(review_entry)
            db.commit()
            db.refresh(card)
            card_result = card

    return MasteryRecordResponse(
        topic_id=mastery.topic_id,
        new_mastery_score=mastery.score,
        p_mastery=mastery.p_mastery,
        observed_accuracy=mastery.observed_accuracy,
        observed_correct=mastery.observed_correct,
        observed_total=mastery.observed_total,
        review_count=mastery.review_count,
        last_reviewed_at=mastery.last_reviewed_at or datetime.now(timezone.utc),
        card_id=card_result.id if card_result else None,
        card_ease_factor=card_result.ease_factor if card_result else None,
        card_interval_days=card_result.interval_days if card_result else None,
        card_repetitions=card_result.repetitions if card_result else None,
        card_due_date=card_result.due_date if card_result else None,
    )


@router.get("/topic/{topic_id}")
def get_topic_mastery(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.models.topic_mastery import TopicMastery
    topic = (
        db.query(Topic)
        .join(Subject, Topic.subject_id == Subject.id)
        .filter(Topic.id == topic_id, Subject.user_id == current_user.id)
        .first()
    )
    if not topic:
        raise NotFoundException("Topic", topic_id)

    mastery = db.query(TopicMastery).filter(
        TopicMastery.topic_id == topic_id,
        TopicMastery.user_id == current_user.id
    ).first()

    if not mastery:
        return {
            "topic_id": topic_id,
            "score": 0.0,
            "p_mastery": 0.2,
            "observed_accuracy": 0.0,
            "observed_correct": 0,
            "observed_total": 0,
            "review_count": 0,
            "last_reviewed_at": None
        }

    return {
        "topic_id": mastery.topic_id,
        "score": mastery.score,
        "p_mastery": mastery.p_mastery,
        "observed_accuracy": mastery.observed_accuracy,
        "observed_correct": mastery.observed_correct,
        "observed_total": mastery.observed_total,
        "review_count": mastery.review_count,
        "last_reviewed_at": mastery.last_reviewed_at.isoformat() if mastery.last_reviewed_at else None
    }

