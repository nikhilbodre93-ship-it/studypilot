from typing import Optional
from math import ceil
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.subject import Subject
from app.models.topic import Topic
from app.schemas.subject import (
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse,
)
from app.schemas.common import PaginatedResponse, SuccessMessageResponse
from app.core.exceptions import NotFoundException
from app.api.deps import get_current_user

router = APIRouter()


@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_subject(
    payload: SubjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subject = Subject(
        user_id=current_user.id,
        name=payload.name.strip(),
        description=payload.description.strip() if payload.description else None,
        exam_date=payload.exam_date,
        color=payload.color or "#2F5D46",
    )
    db.add(subject)
    db.commit()
    db.refresh(subject)

    resp = SubjectResponse.model_validate(subject)
    resp.topic_count = 0
    return resp


@router.get("", response_model=PaginatedResponse[SubjectResponse])
@router.get("/", response_model=PaginatedResponse[SubjectResponse], include_in_schema=False)
def list_subjects(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(default=None, description="Search by name"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Subject).filter(Subject.user_id == current_user.id)
    if search:
        query = query.filter(Subject.name.ilike(f"%{search.strip()}%"))

    total = query.count()
    offset = (page - 1) * page_size
    subjects = query.order_by(Subject.created_at.desc()).offset(offset).limit(page_size).all()

    # Get topic counts for each subject in batch
    subject_ids = [s.id for s in subjects]
    topic_counts = dict(
        db.query(Topic.subject_id, func.count(Topic.id))
        .filter(Topic.subject_id.in_(subject_ids))
        .group_by(Topic.subject_id)
        .all()
    ) if subject_ids else {}

    items = []
    for s in subjects:
        item = SubjectResponse.model_validate(s)
        item.topic_count = topic_counts.get(s.id, 0)
        items.append(item)

    pages = ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse[SubjectResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{subject_id}", response_model=SubjectResponse)
def get_subject(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.user_id == current_user.id
    ).first()
    if not subject:
        raise NotFoundException("Subject", subject_id)

    topic_count = db.query(func.count(Topic.id)).filter(Topic.subject_id == subject.id).scalar() or 0

    resp = SubjectResponse.model_validate(subject)
    resp.topic_count = topic_count
    return resp


@router.put("/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: int,
    payload: SubjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.user_id == current_user.id
    ).first()
    if not subject:
        raise NotFoundException("Subject", subject_id)

    if payload.name is not None:
        subject.name = payload.name.strip()
    if payload.description is not None:
        subject.description = payload.description.strip() if payload.description else None
    if payload.exam_date is not None:
        subject.exam_date = payload.exam_date
    if payload.color is not None:
        subject.color = payload.color

    db.commit()
    db.refresh(subject)

    topic_count = db.query(func.count(Topic.id)).filter(Topic.subject_id == subject.id).scalar() or 0
    resp = SubjectResponse.model_validate(subject)
    resp.topic_count = topic_count
    return resp


@router.delete("/{subject_id}", response_model=SuccessMessageResponse)
def delete_subject(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.user_id == current_user.id
    ).first()
    if not subject:
        raise NotFoundException("Subject", subject_id)

    db.delete(subject)
    db.commit()
    return SuccessMessageResponse(message=f"Subject '{subject.name}' deleted successfully.")
