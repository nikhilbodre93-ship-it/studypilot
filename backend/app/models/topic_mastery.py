from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Float, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.topic import Topic


class TopicMastery(Base):
    __tablename__ = "topic_mastery"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 0.0 to 100.0
    p_mastery: Mapped[float] = mapped_column(Float, default=0.2, nullable=False)  # BKT probability [0.0, 1.0]
    observed_correct: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    observed_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    observed_accuracy: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    stability: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    retrievability: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    last_reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_review_due: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    review_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    topic: Mapped["Topic"] = relationship("Topic", back_populates="mastery")

    __table_args__ = (
        Index("ix_topic_mastery_user_score", "user_id", "score"),
    )
