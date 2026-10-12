from datetime import datetime, date, timezone
from typing import Optional
from sqlalchemy import String, Text, Integer, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class PlanSession(Base):
    __tablename__ = "plan_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id: Mapped[Optional[int]] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), nullable=True, index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    scheduled_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    session_type: Mapped[str] = mapped_column(String(32), default="review", nullable=False)  # learn, review, quiz, rapid_review, exam_paper
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)  # pending, completed, skipped
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Explainable scheduling rationale
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    __table_args__ = (
        Index("ix_plan_sessions_user_date_order", "user_id", "scheduled_date", "scheduled_order"),
    )
