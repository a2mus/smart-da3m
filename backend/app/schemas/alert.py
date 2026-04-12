"""
Pydantic schemas for pedagogical alerts.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.alert import AlertSeverity, AlertStatus, AlertTriggerType


class AlertResponse(BaseModel):
    """Schema for alert response."""

    id: UUID
    student_id: UUID
    trigger_type: AlertTriggerType
    severity: AlertSeverity
    status: AlertStatus
    simplified_message: str
    expert_message: str
    recommended_action: Optional[str] = None
    context_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    """Schema for paginated alert list."""

    items: List[AlertResponse]
    total: int
    unread_count: int


class AlertCreateRequest(BaseModel):
    """Schema for creating an alert (internal use)."""

    student_id: UUID
    trigger_type: AlertTriggerType
    severity: AlertSeverity
    simplified_message: str
    expert_message: str
    recommended_action: Optional[str] = None
    context_data: Dict[str, Any] = Field(default_factory=dict)


class AlertMarkReadRequest(BaseModel):
    """Schema for marking alert as read."""

    alert_ids: List[UUID]


class AlertMarkReadResponse(BaseModel):
    """Schema for mark as read response."""

    marked_count: int


class AlertDismissRequest(BaseModel):
    """Schema for dismissing an alert."""

    alert_id: UUID
    reason: Optional[str] = None


class AlertGroupingSuggestion(BaseModel):
    """Schema for auto-grouping suggestion."""

    should_group: bool
    group_size: Optional[int] = None
    shared_misconception: Optional[str] = None
    recommended_intervention: Optional[str] = None
    student_ids: List[UUID] = Field(default_factory=list)


class ParentAlertSummary(BaseModel):
    """Simplified alert for parent dashboard."""

    id: UUID
    severity: AlertSeverity
    message: str
    created_at: datetime
    is_read: bool
