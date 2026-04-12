"""
Pydantic schemas for analytics endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ==================== Heatmap Schemas ====================

class HeatmapFilters(BaseModel):
    """Filters for heatmap data."""

    student_ids: Optional[List[UUID]] = None
    competency_ids: Optional[List[str]] = None
    class_id: Optional[str] = None
    grade_level: Optional[str] = None
    subject: Optional[str] = None


class StudentCompetencyRow(BaseModel):
    """Student row in heatmap."""

    id: UUID
    name: str
    grade_level: str


class HeatmapCell(BaseModel):
    """Individual cell in competency heatmap."""

    student_id: UUID
    competency_id: str
    mastery_level: str
    p_learned: float = Field(..., ge=0.0, le=1.0)
    color: str  # Hex color code
    score: int = Field(..., ge=0, le=100)


class HeatmapResponse(BaseModel):
    """Response schema for competency heatmap."""

    students: List[StudentCompetencyRow]
    competencies: List[str]
    cells: List[HeatmapCell]
    total_students: int
    total_competencies: int


# ==================== Auto-Grouping Schemas ====================

class GroupCriteria(BaseModel):
    """Criteria for grouping students."""

    competency_id: Optional[str] = None
    mastery_level: Optional[str] = None
    error_type: Optional[str] = None


class StudentGroup(BaseModel):
    """Group of students with shared characteristics."""

    group_id: str
    name: str
    student_count: int
    student_ids: List[str]
    criteria: Dict[str, Any]
    recommended_action: str


class AutoGroupResponse(BaseModel):
    """Response for auto-grouping endpoint."""

    groups: List[Dict[str, Any]]
    total_groups: int
    group_by: str


# ==================== Metrics Schemas ====================

class MetricResponse(BaseModel):
    """Platform-level analytics metrics."""

    gap_reduction_rate: float = Field(
        ..., description="Percentage improvement in competency scores"
    )
    mastery_speed: float = Field(
        ..., description="Average sessions to achieve mastery"
    )
    retention_rate: float = Field(
        ..., description="Percentage retaining mastery after 1 week"
    )
    effort_vs_results: float = Field(
        ..., description="Correlation between effort and results (0-1)"
    )
    resilience_score: float = Field(
        ..., description="Score for recovering from failures"
    )
    total_students: int
    total_assessments: int


# ==================== Export Schemas ====================

class ExportFormat(str):
    """Export format enumeration."""

    CSV = "csv"
    PDF = "pdf"


class ExportRequest(BaseModel):
    """Request to export analytics data."""

    format: str = Field(..., pattern="^(csv|pdf)$")
    report_type: str = Field(
        ..., pattern="^(heatmap|remediation_card|full_report)$"
    )
    filters: Optional[HeatmapFilters] = None
    student_ids: Optional[List[UUID]] = None


class ExportResponse(BaseModel):
    """Response for export request."""

    success: bool
    file_path: str
    format: str
    report_type: str
    generated_at: str