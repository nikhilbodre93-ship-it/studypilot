from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models.topic_mastery import TopicMastery


class BKTConfig(BaseModel):
    """Bayesian Knowledge Tracing parameters."""
    p_init: float = 0.20   # Prior probability of mastery P(L0)
    p_learn: float = 0.15  # Probability of learning transition P(T)
    p_slip: float = 0.10   # Probability of slip P(S) (knowing but answering wrong)
    p_guess: float = 0.20  # Probability of guessing correctly P(G) without knowing


def update_bkt(current_p: float, is_correct: bool, config: Optional[BKTConfig] = None) -> float:
    """
    Compute posterior mastery probability following standard BKT Bayesian update:
    1. Update probability of knowing given observed evidence (correct or incorrect).
    2. Add transition probability of learning during this opportunity.
    """
    cfg = config or BKTConfig()

    # Numerical safety clamp
    p = max(0.001, min(0.999, current_p))

    # Evidence update P(L_t | Evidence)
    if is_correct:
        numerator = p * (1.0 - cfg.p_slip)
        denominator = numerator + (1.0 - p) * cfg.p_guess
    else:
        numerator = p * cfg.p_slip
        denominator = numerator + (1.0 - p) * (1.0 - cfg.p_guess)

    p_known = numerator / max(denominator, 1e-9)

    # Transition update: P(L_t+1) = P(L_t | Evidence) + (1 - P(L_t | Evidence)) * P(T)
    p_next = p_known + (1.0 - p_known) * cfg.p_learn

    return round(max(0.01, min(0.99, p_next)), 4)


def record_topic_evidence(
    db: Session,
    user_id: int,
    topic_id: int,
    is_correct: bool,
    config: Optional[BKTConfig] = None
) -> TopicMastery:
    """
    Update topic mastery and observed accuracy for a user given a quiz answer or flashcard response.
    """
    mastery = db.query(TopicMastery).filter(
        TopicMastery.user_id == user_id,
        TopicMastery.topic_id == topic_id
    ).first()

    now = datetime.now(timezone.utc)
    if not mastery:
        cfg = config or BKTConfig()
        initial_p = cfg.p_init
        new_p = update_bkt(initial_p, is_correct, cfg)
        mastery = TopicMastery(
            user_id=user_id,
            topic_id=topic_id,
            p_mastery=new_p,
            score=round(new_p * 100.0, 1),
            observed_correct=1 if is_correct else 0,
            observed_total=1,
            observed_accuracy=1.0 if is_correct else 0.0,
            review_count=1,
            last_reviewed_at=now,
        )
        db.add(mastery)
    else:
        new_p = update_bkt(mastery.p_mastery, is_correct, config)
        mastery.p_mastery = new_p
        mastery.score = round(new_p * 100.0, 1)
        mastery.observed_total += 1
        if is_correct:
            mastery.observed_correct += 1
        mastery.observed_accuracy = round(mastery.observed_correct / max(mastery.observed_total, 1), 4)
        mastery.review_count += 1
        mastery.last_reviewed_at = now

    db.commit()
    db.refresh(mastery)
    return mastery
