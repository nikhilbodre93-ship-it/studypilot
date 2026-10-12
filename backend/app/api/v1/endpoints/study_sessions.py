from typing import Optional, Dict
from math import ceil
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.study_session import StudySession
from app.schemas.study_session import (
    StudySessionCreate,
    StudySessionResponse,
    StudySessionSummaryResponse,
)
from app.schemas.common import PaginatedResponse, SuccessMessageResponse
from app.core.exceptions import NotFoundException, BadRequestException
from app.api.deps import get_current_user

router = APIRouter()


@router.post("", response_model=StudySessionResponse, status_code=status.HTTP_201_CREATED)
def create_study_session(
    payload: StudySessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subject_name: Optional[str] = None
    topic_name: Optional[str] = None

    if payload.subject_id:
        subject = db.query(Subject).filter(
            Subject.id == payload.subject_id,
            Subject.user_id == current_user.id
        ).first()
        if not subject:
            raise NotFoundException("Subject", payload.subject_id)
        subject_name = subject.name

    if payload.topic_id:
        topic = (
            db.query(Topic)
            .join(Subject, Topic.subject_id == Subject.id)
            .filter(Topic.id == payload.topic_id, Subject.user_id == current_user.id)
            .first()
        )
        if not topic:
            raise NotFoundException("Topic", payload.topic_id)
        topic_name = topic.name

    session = StudySession(
        user_id=current_user.id,
        subject_id=payload.subject_id,
        topic_id=payload.topic_id,
        duration_minutes=payload.duration_minutes,
        session_type=payload.session_type,
        notes=payload.notes,
        completed_at=payload.completed_at or datetime.now(timezone.utc),
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    resp = StudySessionResponse.model_validate(session)
    resp.subject_name = subject_name
    resp.topic_name = topic_name
    return resp


@router.get("", response_model=PaginatedResponse[StudySessionResponse])
def list_study_sessions(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    subject_id: Optional[int] = Query(default=None, description="Filter by subject"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(StudySession).filter(StudySession.user_id == current_user.id)
    if subject_id is not None:
        query = query.filter(StudySession.subject_id == subject_id)

    total = query.count()
    offset = (page - 1) * page_size
    sessions = query.order_by(StudySession.created_at.desc()).offset(offset).limit(page_size).all()

    # Pre-fetch subjects and topics map
    subj_ids = {s.subject_id for s in sessions if s.subject_id}
    topic_ids = {s.topic_id for s in sessions if s.topic_id}

    subj_map = {s.id: s.name for s in db.query(Subject).filter(Subject.id.in_(subj_ids)).all()} if subj_ids else {}
    topic_map = {t.id: t.name for t in db.query(Topic).filter(Topic.id.in_(topic_ids)).all()} if topic_ids else {}

    items = []
    for s in sessions:
        item = StudySessionResponse.model_validate(s)
        item.subject_name = subj_map.get(s.subject_id)
        item.topic_name = topic_map.get(s.topic_id)
        items.append(item)

    pages = ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse[StudySessionResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/summary", response_model=StudySessionSummaryResponse)
def get_study_session_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = db.query(StudySession).filter(StudySession.user_id == current_user.id).all()
    total_sessions = len(sessions)
    total_minutes = sum(s.duration_minutes for s in sessions)
    total_hours = round(total_minutes / 60.0, 1)

    by_type: Dict[str, int] = {}
    for s in sessions:
        by_type[s.session_type] = by_type.get(s.session_type, 0) + s.duration_minutes

    return StudySessionSummaryResponse(
        total_sessions=total_sessions,
        total_minutes=total_minutes,
        total_hours=total_hours,
        by_type=by_type,
    )


@router.delete("/{session_id}", response_model=SuccessMessageResponse)
def delete_study_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    if not session:
        raise NotFoundException("StudySession", session_id)

    db.delete(session)
    db.commit()
    return SuccessMessageResponse(message="Study session deleted successfully.")
