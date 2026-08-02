"""
Pydantic schemas for dashboard data.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SubjectProgress(BaseModel):
    """Schema for subject progress data."""

    name: str
    competency_id: str
    score: int = Field(..., ge=0, le=100)
    mastery_level: str
    last_assessed: Optional[str] = None


class RecentActivity(BaseModel):
    """Schema for recent activity item."""

    type: str  # DIAGNOSTIC, REMEDIATION, PASSPORT, ACHIEVEMENT
    title: str
    timestamp: str
    status: Optional[str] = None
    progress: Optional[int] = None


class Recommendation(BaseModel):
    """Schema for actionable recommendation."""

    title: str
    description: str
    duration: str
    priority: str  # high, medium, low
    activity_type: Optional[str] = "OFF_PLATFORM"
    off_platform: Optional[bool] = True
    competency_id: Optional[str] = None
    error_type: Optional[str] = None


class InsightMessage(BaseModel):
    """Schema for plain-language smart insight messages (zero raw scores)."""

    id: str
    type: str  # STRENGTH, GAP, PROGRESS, GENERAL
    text: str
    competency_id: Optional[str] = None
    competency_name: Optional[str] = None
    mastery_level: Optional[str] = None


class ChildDashboardData(BaseModel):
    """Schema for individual child dashboard data."""

    id: str
    name: str
    subjects: List[SubjectProgress]
    recent_activities: List[RecentActivity]
    summary: str
    insights: List[InsightMessage] = Field(default_factory=list)
    recommendations: List[Recommendation]
    daily_recommendation: Optional[Recommendation] = None
    overall_progress: float
    last_active: Optional[str] = None


class ParentDashboardResponse(BaseModel):
    """Schema for parent dashboard response."""

    parent_id: str
    children_count: int
    children: List[ChildDashboardData]
    generated_at: str


class ChildProgressSummary(BaseModel):
    """Schema for simplified child progress summary."""

    child_id: str
    name: str
    avatar_url: Optional[str] = None
    overall_progress: float
    last_active: Optional[str] = None
    needs_attention: bool = False
