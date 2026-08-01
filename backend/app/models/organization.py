"""
Organization and OrganizationMember models for multi-tenant isolation.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Uuid
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.models.user import UserRole


class OrganizationType(str, enum.Enum):
    """Organization type enumeration."""

    SCHOOL = "SCHOOL"
    HOUSEHOLD = "HOUSEHOLD"


class Organization(Base):
    """Organization model serving as the tenant boundary."""

    __tablename__ = "organizations"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    type = Column(Enum(OrganizationType), nullable=False, index=True)
    is_system_org = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    members = relationship(
        "OrganizationMember",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name='{self.name}', type={self.type})>"


class OrganizationMember(Base):
    """Association model linking users to organizations with assigned roles."""

    __tablename__ = "organization_members"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(Enum(UserRole), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    organization = relationship("Organization", back_populates="members")
    user = relationship("User")

    def __repr__(self) -> str:
        return (
            f"<OrganizationMember(id={self.id}, user_id={self.user_id}, "
            f"organization_id={self.organization_id}, role={self.role})>"
        )
