"""
Remediation models for personalized learning pathways.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Enum, ForeignKey, Integer, String, Uuid

from app.db.session import Base


class RemediationPathStatus(str, enum.Enum):
    """Remediation pathway status."""

    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABANDONED = "ABANDONED"


class RemediationPath(Base):
    """Student's personalized remediation pathway."""

    __tablename__ = "remediation_paths"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    competency_id = Column(String(50), nullable=False, index=True)
    status = Column(
        Enum(RemediationPathStatus),
        default=RemediationPathStatus.IN_PROGRESS,
        nullable=False,
    )
    atoms_completed = Column(JSON, default=list)  # stored as JSON array of UUID strings
    current_difficulty = Column(Integer, default=5)  # Dynamic difficulty tracking
    started_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<RemediationPath(id={self.id}, student={self.student_id}, "
            f"competency={self.competency_id}, status={self.status})>"
        )


class AtomCompletion(Base):
    """Record of a student completing a knowledge atom."""

    __tablename__ = "atom_completions"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    path_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("remediation_paths.id", ondelete="CASCADE"),
        nullable=False,
    )
    atom_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("knowledge_atoms.id", ondelete="CASCADE"),
        nullable=False,
    )
    time_spent_ms = Column(Integer, nullable=False)
    interactions_count = Column(Integer, default=1)
    completed_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return (
            f"<AtomCompletion(id={self.id}, path={self.path_id}, "
            f"atom={self.atom_id})>"
        )


class PassportAssessment(Base):
    """Passport assessment attempt for verifying mastery."""

    __tablename__ = "passport_assessments"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    competency_id = Column(String(50), nullable=False, index=True)
    passed = Column(Integer, nullable=True)  # 0 or 1, null if not completed
    accuracy = Column(Integer, nullable=True)  # Percentage (0-100)
    questions_answered = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    started_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<PassportAssessment(id={self.id}, student={self.student_id}, "
            f"passed={self.passed})>"
        )
