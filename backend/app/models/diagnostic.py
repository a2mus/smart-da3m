"""
Diagnostic models for adaptive testing sessions, answers, and competency profiles.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID

from app.db.session import Base


class DiagnosticSessionStatus(str, enum.Enum):
    """Diagnostic session status."""

    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class RemediationGroup(str, enum.Enum):
    """Remediation group assignment based on diagnostic results."""

    A = "A"  # Mastery/Enrichment
    B = "B"  # Partial/Targeted remediation
    C = "C"  # No mastery/Intensive remediation


class ErrorClassification(str, enum.Enum):
    """Error classification for diagnostic answers."""

    RESOURCE = "RESOURCE"  # Missing prerequisites
    PROCESS = "PROCESS"  # Methodology misunderstanding
    INCIDENTAL = "INCIDENTAL"  # Carelessness
    NONE = "NONE"  # Correct answer


class MasteryLevel(str, enum.Enum):
    """Mastery level enumeration for competency profiles."""

    NOT_STARTED = "NOT_STARTED"
    ATTEMPTED = "ATTEMPTED"
    FAMILIAR = "FAMILIAR"
    PROFICIENT = "PROFICIENT"
    MASTERED = "MASTERED"


class DiagnosticSession(Base):
    """Adaptive diagnostic test session."""

    __tablename__ = "diagnostic_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    module_id = Column(
        UUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"), nullable=False
    )
    status = Column(
        Enum(DiagnosticSessionStatus),
        default=DiagnosticSessionStatus.IN_PROGRESS,
        nullable=False,
    )
    recommended_group = Column(Enum(RemediationGroup), nullable=True)
    started_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<DiagnosticSession(id={self.id}, student={self.student_id}, "
            f"status={self.status})>"
        )


class DiagnosticAnswer(Base):
    """Individual answer within a diagnostic session."""

    __tablename__ = "diagnostic_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("diagnostic_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_id = Column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    is_correct = Column(Integer, nullable=False)  # 0 or 1
    response_time_ms = Column(Integer, nullable=False)
    error_classification = Column(Enum(ErrorClassification), nullable=False)
    answered_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return (
            f"<DiagnosticAnswer(id={self.id}, session={self.session_id}, "
            f"correct={self.is_correct}, error={self.error_classification})>"
        )


class CompetencyProfile(Base):
    """Student competency mastery profile using BKT."""

    __tablename__ = "competency_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    competency_id = Column(String(50), nullable=False, index=True)
    mastery_level = Column(Enum(MasteryLevel), default=MasteryLevel.NOT_STARTED)
    p_learned = Column(Float, default=0.0)  # BKT probability (0.0 to 1.0)
    last_assessed = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return (
            f"<CompetencyProfile(id={self.id}, student={self.student_id}, "
            f"competency={self.competency_id}, mastery={self.mastery_level})>"
        )
