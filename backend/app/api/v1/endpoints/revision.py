from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.subject import Subject
from app.models.topic import Topic
from app.core.priority import calculate_topic_priority, TopicPriorityBreakdown
from app.core.scheduler import build_daily_revision_queue, RevisionQueueResponse
from app.core.exceptions import NotFoundException
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/queue", response_model=RevisionQueueResponse)
def get_revision_queue(
    minutes: int = Query(default=60, ge=5, le=720, description="Available study time in minutes"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate an explainable revision queue tailored to available minutes today.
    Selects top-priority topics and fits them into optimal study blocks.
    """
    return build_daily_revision_queue(
        db=db,
        user_id=current_user.id,
        available_minutes=minutes
    )


@router.get("/explain/{topic_id}", response_model=TopicPriorityBreakdown)
def explain_topic_priority(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Detailed explanation of revision priority calculation for a single topic.
    Returns every weighted component and a human-readable summary.
    """
    topic = (
        db.query(Topic)
        .join(Subject, Topic.subject_id == Subject.id)
        .filter(Topic.id == topic_id, Subject.user_id == current_user.id)
        .first()
    )
    if not topic:
        raise NotFoundException("Topic", topic_id)

    return calculate_topic_priority(
        db=db,
        user_id=current_user.id,
        topic=topic
    )
