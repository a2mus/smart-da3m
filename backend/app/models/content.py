"""
Content models for curriculum modules, questions, and knowledge atoms.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db.session import Base


class ModuleStatus(str, enum.Enum):
    """Module publication status."""

    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"


class RemediationType(str, enum.Enum):
    """Type of remediation content."""

    AUDIO_VISUAL = "AUDIO_VISUAL"
    SIMULATION = "SIMULATION"
    MIND_MAP = "MIND_MAP"


class Module(Base):
    """Curriculum module for organizing content."""

    __tablename__ = "modules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject = Column(String(100), nullable=False, index=True)
    grade_level = Column(String(50), nullable=False, index=True)
    domain = Column(String(200), nullable=False)
    competency_id = Column(String(50), nullable=False, index=True)
    status = Column(
        Enum(ModuleStatus), default=ModuleStatus.DRAFT, nullable=False, index=True
    )
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return (
            f"<Module(id={self.id}, subject={self.subject}, "
            f"grade={self.grade_level}, competency={self.competency_id})>"
        )


class Question(Base):
    """Assessment question within a module."""

    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id = Column(
        UUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"), nullable=False
    )
    content = Column(JSONB, nullable=False)  # Question text, images, interactive layout
    difficulty_level = Column(Integer, nullable=False)  # 1-10 scale
    target_misconception_id = Column(String(50), nullable=True, index=True)
    estimated_time_sec = Column(Integer, nullable=False, default=60)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return (
            f"<Question(id={self.id}, module_id={self.module_id}, "
            f"difficulty={self.difficulty_level})>"
        )


class KnowledgeAtom(Base):
    """Micro-learning content for remediation pathways."""

    __tablename__ = "knowledge_atoms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competency_id = Column(String(50), nullable=False, index=True)
    remediation_type = Column(Enum(RemediationType), nullable=False)
    content = Column(JSONB, nullable=False)  # Title, description, media URLs, etc.
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return (
            f"<KnowledgeAtom(id={self.id}, competency={self.competency_id}, "
            f"type={self.remediation_type})>"
        )
