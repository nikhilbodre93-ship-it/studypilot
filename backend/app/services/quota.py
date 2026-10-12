from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.config import settings
from app.models.llm_log import LLMUsageLog


def check_daily_quota(user_id: int, db: Session) -> None:
    """
    Enforce per-user daily quota for LLM generations.
    Raises HTTPException 429 if limit is exceeded.
    """
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    count = db.query(func.count(LLMUsageLog.id)).filter(
        LLMUsageLog.user_id == user_id,
        LLMUsageLog.created_at >= today_start
    ).scalar() or 0

    if count >= settings.DAILY_GENERATION_QUOTA:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily AI generation quota exceeded ({settings.DAILY_GENERATION_QUOTA} requests/day). Quota resets at midnight UTC."
        )
