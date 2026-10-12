from typing import Optional
from math import ceil
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.topic_mastery import TopicMastery
from app.schemas.topic import (
    TopicCreate,
    TopicUpdate,
    TopicResponse,
)
from app.schemas.common import PaginatedResponse, SuccessMessageResponse
from app.core.exceptions import NotFoundException
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/subjects/{subject_id}/topics", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
@router.post("/subjects/{subject_id}/topics/", response_model=TopicResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_topic_for_subject(
    subject_id: int,
    payload: TopicCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.user_id == current_user.id
    ).first()
    if not subject:
        raise NotFoundException("Subject", subject_id)

    topic = Topic(
        subject_id=subject.id,
        name=payload.name.strip(),
        description=payload.description.strip() if payload.description else None,
        difficulty=payload.difficulty,
        order_index=payload.order_index,
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)

    # Automatically create initial 0 mastery record
    mastery = TopicMastery(
        user_id=current_user.id,
        topic_id=topic.id,
        score=0.0,
        stability=1.0,
        retrievability=1.0,
    )
    db.add(mastery)
    db.commit()

    resp = TopicResponse.model_validate(topic)
    resp.mastery_score = 0.0
    return resp


@router.get("/subjects/{subject_id}/topics", response_model=PaginatedResponse[TopicResponse])
@router.get("/subjects/{subject_id}/topics/", response_model=PaginatedResponse[TopicResponse], include_in_schema=False)
def list_topics_for_subject(
    subject_id: int,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=50, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.user_id == current_user.id
    ).first()
    if not subject:
        raise NotFoundException("Subject", subject_id)

    query = db.query(Topic).filter(Topic.subject_id == subject.id)
    total = query.count()
    offset = (page - 1) * page_size
    topics = query.order_by(Topic.order_index.asc(), Topic.id.asc()).offset(offset).limit(page_size).all()

    topic_ids = [t.id for t in topics]
    mastery_map = dict(
        db.query(TopicMastery.topic_id, TopicMastery.score)
        .filter(TopicMastery.topic_id.in_(topic_ids), TopicMastery.user_id == current_user.id)
        .all()
    ) if topic_ids else {}

    items = []
    for t in topics:
        item = TopicResponse.model_validate(t)
        item.mastery_score = mastery_map.get(t.id, 0.0)
        items.append(item)

    pages = ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse[TopicResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/topics/{topic_id}", response_model=TopicResponse)
def get_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    topic = (
        db.query(Topic)
        .join(Subject, Topic.subject_id == Subject.id)
        .filter(Topic.id == topic_id, Subject.user_id == current_user.id)
        .first()
    )
    if not topic:
        raise NotFoundException("Topic", topic_id)

    mastery = db.query(TopicMastery).filter(
        TopicMastery.topic_id == topic.id,
        TopicMastery.user_id == current_user.id
    ).first()

    resp = TopicResponse.model_validate(topic)
    resp.mastery_score = mastery.score if mastery else 0.0
    return resp


@router.put("/topics/{topic_id}", response_model=TopicResponse)
def update_topic(
    topic_id: int,
    payload: TopicUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    topic = (
        db.query(Topic)
        .join(Subject, Topic.subject_id == Subject.id)
        .filter(Topic.id == topic_id, Subject.user_id == current_user.id)
        .first()
    )
    if not topic:
        raise NotFoundException("Topic", topic_id)

    if payload.name is not None:
        topic.name = payload.name.strip()
    if payload.description is not None:
        topic.description = payload.description.strip() if payload.description else None
    if payload.difficulty is not None:
        topic.difficulty = payload.difficulty
    if payload.order_index is not None:
        topic.order_index = payload.order_index

    db.commit()
    db.refresh(topic)

    mastery = db.query(TopicMastery).filter(
        TopicMastery.topic_id == topic.id,
        TopicMastery.user_id == current_user.id
    ).first()

    resp = TopicResponse.model_validate(topic)
    resp.mastery_score = mastery.score if mastery else 0.0
    return resp


@router.delete("/topics/{topic_id}", response_model=SuccessMessageResponse)
def delete_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    topic = (
        db.query(Topic)
        .join(Subject, Topic.subject_id == Subject.id)
        .filter(Topic.id == topic_id, Subject.user_id == current_user.id)
        .first()
    )
    if not topic:
        raise NotFoundException("Topic", topic_id)

    db.delete(topic)
    db.commit()
    return SuccessMessageResponse(message=f"Topic '{topic.name}' deleted successfully.")
