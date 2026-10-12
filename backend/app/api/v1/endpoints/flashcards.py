import json
import logging
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.user import User
from app.models.topic import Topic
from app.models.flashcard import Flashcard, CardReview
from app.api.v1.endpoints.auth import get_current_user
from app.llm.factory import get_llm_provider
from app.services.rag import retrieve_grounding_context
from app.services.quota import check_daily_quota
from app.core.sm2 import calculate_sm2
from app.core.bkt import record_topic_evidence
from prompts.v1.system import BASE_SYSTEM_INSTRUCTION
from prompts.v1.flashcards import GeneratedFlashcardDeck, FLASHCARD_PROMPT_TEMPLATE

logger = logging.getLogger("studypilot.flashcards")
router = APIRouter()


class FlashcardCreate(BaseModel):
    topic_id: int
    front: str
    back: str
    explanation: Optional[str] = None
    difficulty: str = "medium"


class FlashcardUpdate(BaseModel):
    front: Optional[str] = None
    back: Optional[str] = None
    explanation: Optional[str] = None
    difficulty: Optional[str] = None


class FlashcardGenerateRequest(BaseModel):
    topic_id: int
    count: int = Field(default=8, ge=1, le=30)


class FlashcardReviewRequest(BaseModel):
    flashcard_id: int
    rating: int = Field(..., ge=1, le=5)  # 1=Again, 2=Hard, 3=Good, 4=Easy, 5=Perfect
    review_duration_ms: Optional[int] = 0


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_flashcards(
    req: FlashcardGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_daily_quota(current_user.id, db)

    topic = db.query(Topic).filter(Topic.id == req.topic_id).first()
    if not topic or topic.subject.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Topic not found or unauthorized")

    context = retrieve_grounding_context(topic.id, query=f"{topic.name} key concepts definitions", db=db, top_k=4)

    prompt = FLASHCARD_PROMPT_TEMPLATE.format(
        topic_name=topic.name,
        count=req.count,
        context=context
    )

    provider = get_llm_provider()
    try:
        gen_deck: GeneratedFlashcardDeck = await provider.generate_structured(
            prompt=prompt,
            system_prompt=BASE_SYSTEM_INSTRUCTION,
            response_model=GeneratedFlashcardDeck,
            user_id=current_user.id,
            feature_name="flashcards"
        )
    except Exception as e:
        logger.error(f"Flashcard generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate flashcards: {str(e)}")

    now = datetime.now(timezone.utc)
    created_cards = []
    for item in gen_deck.cards:
        card = Flashcard(
            topic_id=topic.id,
            user_id=current_user.id,
            front=item.front,
            back=item.back,
            explanation=item.explanation or (f"Source: {item.citation}" if item.citation else None),
            difficulty=item.difficulty,
            ease_factor=2.5,
            interval_days=0,
            repetitions=0,
            due_date=now
        )
        db.add(card)
        created_cards.append(card)

    db.commit()

    return {
        "deck_title": gen_deck.deck_title,
        "topic_name": topic.name,
        "count": len(created_cards),
        "cards": [
            {
                "id": c.id,
                "front": c.front,
                "back": c.back,
                "explanation": c.explanation,
                "difficulty": c.difficulty,
                "due_date": c.due_date.isoformat() if c.due_date else None
            }
            for c in created_cards
        ]
    }


@router.get("/")
def list_flashcards(
    topic_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    due_only: bool = False,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Flashcard).filter(Flashcard.user_id == current_user.id)
    if topic_id:
        q = q.filter(Flashcard.topic_id == topic_id)
    if due_only:
        now = datetime.now(timezone.utc)
        q = q.filter(or_(Flashcard.due_date == None, Flashcard.due_date <= now))
    if search:
        q = q.filter(or_(Flashcard.front.ilike(f"%{search}%"), Flashcard.back.ilike(f"%{search}%")))

    cards = q.order_by(Flashcard.created_at.desc()).all()
    return [
        {
            "id": c.id,
            "topic_id": c.topic_id,
            "topic_name": c.topic.name if c.topic else "",
            "subject_name": c.topic.subject.name if c.topic and c.topic.subject else "",
            "front": c.front,
            "back": c.back,
            "explanation": c.explanation,
            "difficulty": c.difficulty,
            "ease_factor": c.ease_factor,
            "interval_days": c.interval_days,
            "repetitions": c.repetitions,
            "due_date": c.due_date.isoformat() if c.due_date else None,
            "last_reviewed_at": c.last_reviewed_at.isoformat() if c.last_reviewed_at else None
        }
        for c in cards
    ]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_flashcard(
    payload: FlashcardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    topic = db.query(Topic).filter(Topic.id == payload.topic_id).first()
    if not topic or topic.subject.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Topic not found or unauthorized")

    card = Flashcard(
        topic_id=payload.topic_id,
        user_id=current_user.id,
        front=payload.front,
        back=payload.back,
        explanation=payload.explanation,
        difficulty=payload.difficulty,
        ease_factor=2.5,
        interval_days=0,
        repetitions=0,
        due_date=datetime.now(timezone.utc)
    )
    db.add(card)
    db.commit()
    db.refresh(card)

    return {
        "id": card.id,
        "topic_id": card.topic_id,
        "front": card.front,
        "back": card.back,
        "explanation": card.explanation,
        "due_date": card.due_date.isoformat()
    }


@router.put("/{card_id}")
def update_flashcard(
    card_id: int,
    payload: FlashcardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    card = db.query(Flashcard).filter(Flashcard.id == card_id, Flashcard.user_id == current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    if payload.front is not None:
        card.front = payload.front
    if payload.back is not None:
        card.back = payload.back
    if payload.explanation is not None:
        card.explanation = payload.explanation
    if payload.difficulty is not None:
        card.difficulty = payload.difficulty

    db.commit()
    db.refresh(card)
    return {
        "id": card.id,
        "front": card.front,
        "back": card.back,
        "explanation": card.explanation
    }


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_flashcard(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    card = db.query(Flashcard).filter(Flashcard.id == card_id, Flashcard.user_id == current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    db.delete(card)
    db.commit()
    return None


@router.post("/review")
def review_flashcard(
    req: FlashcardReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    card = db.query(Flashcard).filter(
        Flashcard.id == req.flashcard_id,
        Flashcard.user_id == current_user.id
    ).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    now = datetime.now(timezone.utc)
    sm2_res = calculate_sm2(
        rating=req.rating,
        current_ease_factor=card.ease_factor,
        current_repetitions=card.repetitions,
        current_interval=card.interval_days,
        review_date=now
    )

    card.ease_factor = sm2_res.ease_factor
    card.repetitions = sm2_res.repetitions
    card.interval_days = sm2_res.interval_days
    card.due_date = sm2_res.due_date
    card.last_reviewed_at = now

    review_log = CardReview(
        flashcard_id=card.id,
        user_id=current_user.id,
        rating=req.rating,
        review_duration_ms=req.review_duration_ms or 0,
        reviewed_at=now
    )
    db.add(review_log)

    # Update BKT mastery (rating >= 3 indicates successful memory retrieval)
    is_correct = req.rating >= 3
    mastery = record_topic_evidence(
        db=db,
        user_id=current_user.id,
        topic_id=card.topic_id,
        is_correct=is_correct
    )

    db.commit()
    db.refresh(card)

    return {
        "flashcard_id": card.id,
        "ease_factor": card.ease_factor,
        "interval_days": card.interval_days,
        "repetitions": card.repetitions,
        "due_date": card.due_date.isoformat(),
        "topic_mastery_score": mastery.score,
        "is_correct": is_correct
    }


@router.get("/export/pdf")
def export_flashcards_printable(
    topic_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Flashcard).filter(Flashcard.user_id == current_user.id)
    if topic_id:
        q = q.filter(Flashcard.topic_id == topic_id)
    cards = q.all()

    cards_html = ""
    for c in cards:
        cards_html += f"""
        <div class="card">
            <div class="front"><strong>Q:</strong> {c.front}</div>
            <hr/>
            <div class="back"><strong>A:</strong> {c.back}</div>
            {f'<div class="expl"><em>Note:</em> {c.explanation}</div>' if c.explanation else ''}
        </div>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>StudyPilot Flashcards Export</title>
<style>
body {{ font-family: sans-serif; background: #fff; padding: 20px; }}
.card {{ border: 2px solid #2F5D46; border-radius: 12px; padding: 16px; margin-bottom: 20px; page-break-inside: avoid; }}
.front {{ font-size: 16px; font-weight: 600; color: #1f2937; margin-bottom: 8px; }}
.back {{ font-size: 15px; color: #2F5D46; margin-top: 8px; }}
.expl {{ font-size: 13px; color: #6b7280; margin-top: 6px; }}
</style>
</head>
<body>
<h1>StudyPilot Deck Export ({len(cards)} cards)</h1>
{cards_html}
</body>
</html>"""

    return Response(
        content=html,
        media_type="text/html",
        headers={"Content-Disposition": 'inline; filename="flashcards_deck.html"'}
    )
