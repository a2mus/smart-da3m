"""
Alert models for pedagogical alerts and notifications.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Enum, ForeignKey, Integer, String, Text, Uuid

from app.db.session import Base


class AlertSeverity(str, enum.Enum):
    """Alert severity levels."""

    INFO = "INFO"  # Minor issue, informational
    WARNING = "WARNING"  # Moderate concern, requires attention
    CRITICAL = "CRITICAL"  # Serious issue, immediate intervention needed


class AlertTriggerType(str, enum.Enum):
    """Types of events that trigger alerts."""

    REPEATED_FAILURE = "REPEATED_FAILURE"  # 3+ consecutive failures
    FRUSTRATION = "FRUSTRATION"  # Declining speed + low accuracy
    PASSPORT_FAILED = "PASSPORT_FAILED"  # Post-remediation assessment failure
    INACTIVITY = "INACTIVITY"  # Extended period without login
    ABANDONMENT = "ABANDONMENT"  # Session abandoned mid-way


class AlertStatus(str, enum.Enum):
    """Alert lifecycle status."""

    UNREAD = "UNREAD"
    READ = "READ"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class PedagogicalAlert(Base):
    """Pedagogical alert for parents and experts."""

    __tablename__ = "pedagogical_alerts"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    trigger_type = Column(Enum(AlertTriggerType), nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False, index=True)
    status = Column(Enum(AlertStatus), default=AlertStatus.UNREAD, nullable=False)

    # Messages for different audiences
    simplified_message = Column(Text, nullable=False)  # For parents
    expert_message = Column(Text, nullable=False)  # For experts with details

    # Additional context
    context_data = Column(JSON, default=dict)  # Store trigger-specific data
    recommended_action = Column(Text, nullable=True)

    # Tracking
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    read_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<PedagogicalAlert(id={self.id}, student={self.student_id}, "
            f"severity={self.severity}, type={self.trigger_type})>"
        )


class AlertRecipient(Base):
    """Tracks alert delivery to recipients (parents/experts)."""

    __tablename__ = "alert_recipients"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(
        Uuid(as_uuid=True), ForeignKey("pedagogical_alerts.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Delivery tracking
    delivered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    read_at = Column(DateTime(timezone=True), nullable=True)
    dismissed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<AlertRecipient(alert={self.alert_id}, user={self.user_id})>"
