from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


from app.models.topic import Topic


class TutorConversation(Base):
    __tablename__ = "tutor_conversations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
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
    topic: Mapped[Optional["Topic"]] = relationship("Topic")
    messages: Mapped[List["TutorMessage"]] = relationship("TutorMessage", back_populates="conversation", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_tutor_conv_user_topic", "user_id", "topic_id"),
    )


class TutorMessage(Base):
    __tablename__ = "tutor_messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("tutor_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender: Mapped[str] = mapped_column(String(32), nullable=False)  # user, assistant
    content: Mapped[str] = mapped_column(Text, nullable=False)
    step_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    citations_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    conversation: Mapped["TutorConversation"] = relationship("TutorConversation", back_populates="messages")

    __table_args__ = (
        Index("ix_tutor_msg_conv_created", "conversation_id", "created_at"),
    )
