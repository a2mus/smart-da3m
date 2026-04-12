"""
User model with role-based access control.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""

    STUDENT = "STUDENT"
    PARENT = "PARENT"
    EXPERT = "EXPERT"


class Language(str, enum.Enum):
    """Supported languages."""

    AR = "AR"  # Arabic (RTL)
    FR = "FR"  # French (LTR)


class User(Base):
    """User model with support for students, parents, and experts."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=True, index=True)
    hashed_password = Column(String(255), nullable=True)
    pin_code_hash = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), nullable=False, index=True)
    language = Column(Enum(Language), default=Language.AR)
    parent_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
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
        return f"<User(id={self.id}, role={self.role}, email={self.email})>"
