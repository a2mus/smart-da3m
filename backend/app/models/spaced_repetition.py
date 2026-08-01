"""
Spaced Repetition model for FR-16 (spaced re-surfacing of failed items).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Uuid
from sqlalchemy.orm import relationship

from app.db.session import Base


class SpacedRepetition(Base):
    """
    Tracks failed items for spaced re-surfacing to transfer learning to long-term memory.
    """

    __tablename__ = "spaced_repetitions"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    next_review_date = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        default=lambda: datetime.now(timezone.utc),
    )
    interval_days = Column(Integer, default=1, nullable=False)
    ease_factor = Column(Float, default=2.5, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    organization = relationship("Organization")
    student = relationship("User")
    question = relationship("Question")

    def __repr__(self) -> str:
        return (
            f"<SpacedRepetition(id={self.id}, student={self.student_id}, "
            f"question={self.question_id}, interval={self.interval_days}, "
            f"next_review={self.next_review_date})>"
        )
