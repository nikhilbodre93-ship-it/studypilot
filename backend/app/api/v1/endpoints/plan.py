from typing import Optional, List
from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.plan_session import PlanSession
from app.schemas.plan import (
    PlanGenerateRequest,
    PlanGenerateResponse,
    PlanSessionResponse,
    PlanSessionUpdateRequest,
)
from app.schemas.common import SuccessMessageResponse
from app.core.exceptions import NotFoundException, BadRequestException
from app.core.scheduler import generate_plan_schedule
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/generate", response_model=PlanGenerateResponse)
def generate_revision_plan(
    payload: PlanGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    start = payload.start_date or date.today()
    created = generate_plan_schedule(
        db=db,
        user_id=current_user.id,
        start_date=start,
        daily_minutes=payload.daily_minutes,
        days_horizon=payload.days_horizon
    )

    end_date = max([s.scheduled_date for s in created]) if created else start

    return PlanGenerateResponse(
        message="Revision plan generated successfully.",
        total_sessions_created=len(created),
        start_date=start,
        end_date=end_date,
    )


@router.get("/schedule", response_model=List[PlanSessionResponse])
def get_revision_schedule(
    from_date: Optional[date] = Query(default=None, description="Start date filter"),
    to_date: Optional[date] = Query(default=None, description="End date filter"),
    status: Optional[str] = Query(default=None, description="pending, completed, skipped"),
    subject_id: Optional[int] = Query(default=None, description="Filter by subject"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(PlanSession).filter(PlanSession.user_id == current_user.id)

    if from_date:
        query = query.filter(PlanSession.scheduled_date >= from_date)
    if to_date:
        query = query.filter(PlanSession.scheduled_date <= to_date)
    if status:
        query = query.filter(PlanSession.status == status)
    if subject_id:
        query = query.filter(PlanSession.subject_id == subject_id)

    sessions = query.order_by(
        PlanSession.scheduled_date.asc(),
        PlanSession.scheduled_order.asc()
    ).all()

    # Pre-fetch lookup maps
    subj_ids = {s.subject_id for s in sessions if s.subject_id}
    topic_ids = {s.topic_id for s in sessions if s.topic_id}

    subj_map = {s.id: s.name for s in db.query(Subject).filter(Subject.id.in_(subj_ids)).all()} if subj_ids else {}
    topic_map = {t.id: t.name for t in db.query(Topic).filter(Topic.id.in_(topic_ids)).all()} if topic_ids else {}

    results = []
    for s in sessions:
        item = PlanSessionResponse.model_validate(s)
        item.subject_name = subj_map.get(s.subject_id)
        item.topic_name = topic_map.get(s.topic_id)
        results.append(item)

    return results


@router.patch("/sessions/{session_id}", response_model=PlanSessionResponse)
def update_plan_session_status(
    session_id: int,
    payload: PlanSessionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(PlanSession).filter(
        PlanSession.id == session_id,
        PlanSession.user_id == current_user.id
    ).first()
    if not session:
        raise NotFoundException("PlanSession", session_id)

    session.status = payload.status
    db.commit()
    db.refresh(session)

    topic = db.query(Topic).filter(Topic.id == session.topic_id).first()
    subject = db.query(Subject).filter(Subject.id == session.subject_id).first() if session.subject_id else None

    resp = PlanSessionResponse.model_validate(session)
    resp.topic_name = topic.name if topic else None
    resp.subject_name = subject.name if subject else None
    return resp
