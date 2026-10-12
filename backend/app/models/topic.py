from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.subject import Subject
    from app.models.topic_mastery import TopicMastery
    from app.models.flashcard import Flashcard
    from app.models.quiz import Quiz
    from app.models.material import Material
    from app.models.note import Note


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)  # easy, medium, hard
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
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
    subject: Mapped["Subject"] = relationship("Subject", back_populates="topics")
    mastery: Mapped[Optional["TopicMastery"]] = relationship("TopicMastery", back_populates="topic", uselist=False, cascade="all, delete-orphan")
    flashcards: Mapped[List["Flashcard"]] = relationship("Flashcard", back_populates="topic", cascade="all, delete-orphan")
    quizzes: Mapped[List["Quiz"]] = relationship("Quiz", back_populates="topic", cascade="all, delete-orphan")
    materials: Mapped[List["Material"]] = relationship("Material", back_populates="topic", cascade="all, delete-orphan")
    notes: Mapped[List["Note"]] = relationship("Note", back_populates="topic", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_topics_subject_order", "subject_id", "order_index"),
        Index("ix_topics_subject_name", "subject_id", "name"),
    )
