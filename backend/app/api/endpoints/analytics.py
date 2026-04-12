"""
Analytics API endpoints for expert dashboard.
Provides heatmaps, cohort insights, and reporting functionality.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_user, require_expert
from app.db.session import get_db
from app.models.diagnostic import (
    CompetencyProfile,
    DiagnosticAnswer,
    DiagnosticSession,
    ErrorClassification,
    MasteryLevel,
)
from app.models.remediation import RemediationPath
from app.models.user import User, UserRole
from app.schemas.analytics import (
    AutoGroupResponse,
    ExportRequest,
    ExportResponse,
    HeatmapCell,
    HeatmapFilters,
    HeatmapResponse,
    MetricResponse,
    StudentCompetencyRow,
)
from app.services.report_exporter import ReportExporter

router = APIRouter()


@router.post("/heatmap", response_model=HeatmapResponse)
async def get_competency_heatmap(
    filters: HeatmapFilters,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_expert),
) -> HeatmapResponse:
    """
    Get competency heatmap data for expert analytics.

    Returns a matrix of students × competencies with mastery levels
    color-coded for quick visual assessment.
    """
    # Build base query for students
    student_query = select(User).where(User.role == UserRole.STUDENT)

    # Apply filters
    if filters.student_ids:
        student_query = student_query.where(User.id.in_(filters.student_ids))

    result = await db.execute(student_query)
    students = list(result.scalars().all())

    if not students:
        return HeatmapResponse(
            students=[],
            competencies=[],
            cells=[],
            total_students=0,
            total_competencies=0,
        )

    student_ids = [s.id for s in students]

    # Get all competency profiles for these students
    profile_query = select(CompetencyProfile).where(
        CompetencyProfile.student_id.in_(student_ids)
    )

    if filters.competency_ids:
        profile_query = profile_query.where(
            CompetencyProfile.competency_id.in_(filters.competency_ids)
        )

    result = await db.execute(profile_query)
    profiles = list(result.scalars().all())

    # Extract unique competencies
    competency_ids = sorted(set(p.competency_id for p in profiles))

    # Build heatmap cells
    cells: List[HeatmapCell] = []
    for profile in profiles:
        # Determine color based on mastery level
        color = _mastery_to_color(profile.mastery_level)
        score = _mastery_to_score(profile.mastery_level)

        cells.append(
            HeatmapCell(
                student_id=profile.student_id,
                competency_id=profile.competency_id,
                mastery_level=profile.mastery_level.value,
                p_learned=round(profile.p_learned, 2),
                color=color,
                score=score,
            )
        )

    # Build student rows
    student_rows = [
        StudentCompetencyRow(
            id=s.id,
            name=f"Student {str(s.id)[:8]}",  # Placeholder
            grade_level="Grade 4",  # Would come from profile
        )
        for s in students
    ]

    return HeatmapResponse(
        students=student_rows,
        competencies=competency_ids,
        cells=cells,
        total_students=len(students),
        total_competencies=len(competency_ids),
    )


def _mastery_to_color(mastery: MasteryLevel) -> str:
    """Convert mastery level to heatmap color."""
    colors = {
        MasteryLevel.NOT_STARTED: "#fee2e2",  # Red-100
        MasteryLevel.ATTEMPTED: "#fef3c7",  # Amber-100
        MasteryLevel.FAMILIAR: "#fef9c3",  # Yellow-100
        MasteryLevel.PROFICIENT: "#d1fae5",  # Emerald-100
        MasteryLevel.MASTERED: "#86efac",  # Green-300
    }
    return colors.get(mastery, "#f3f4f6")


def _mastery_to_score(mastery: MasteryLevel) -> int:
    """Convert mastery level to numerical score."""
    scores = {
        MasteryLevel.NOT_STARTED: 0,
        MasteryLevel.ATTEMPTED: 25,
        MasteryLevel.FAMILIAR: 50,
        MasteryLevel.PROFICIENT: 75,
        MasteryLevel.MASTERED: 100,
    }
    return scores.get(mastery, 0)


@router.post("/auto-group", response_model=AutoGroupResponse)
async def auto_group_students(
    filters: HeatmapFilters,
    group_by: str = Query("competency", description="Group by: competency or error_type"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_expert),
) -> AutoGroupResponse:
    """
    Auto-group students based on shared patterns.

    Groups students who share:
    - Same unmastered competencies (group_by=competency)
    - Same error types (group_by=error_type)
    """
    if group_by == "competency":
        groups = await _group_by_competency(db, filters)
    elif group_by == "error_type":
        groups = await _group_by_error_type(db, filters)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid group_by value: {group_by}",
        )

    return AutoGroupResponse(
        groups=groups,
        total_groups=len(groups),
        group_by=group_by,
    )


async def _group_by_competency(
    db: AsyncSession, filters: HeatmapFilters
) -> List[Dict[str, Any]]:
    """Group students by shared unmastered competencies."""
    # Get students with NOT_STARTED or ATTEMPTED mastery
    query = (
        select(
            CompetencyProfile.competency_id,
            CompetencyProfile.mastery_level,
            func.array_agg(CompetencyProfile.student_id).label("student_ids"),
        )
        .where(
            CompetencyProfile.mastery_level.in_(
                [MasteryLevel.NOT_STARTED, MasteryLevel.ATTEMPTED]
            )
        )
        .group_by(CompetencyProfile.competency_id, CompetencyProfile.mastery_level)
    )

    if filters.competency_ids:
        query = query.where(
            CompetencyProfile.competency_id.in_(filters.competency_ids)
        )

    if filters.student_ids:
        query = query.where(
            CompetencyProfile.student_id.in_(filters.student_ids)
        )

    result = await db.execute(query)
    rows = result.all()

    groups = []
    for row in rows:
        student_count = len(row.student_ids) if row.student_ids else 0
        if student_count > 1:  # Only groups with 2+ students
            groups.append({
                "group_id": f"competency_{row.competency_id}_{row.mastery_level.value}",
                "name": f"{row.competency_id} - {row.mastery_level.value}",
                "student_count": student_count,
                "student_ids": [str(sid) for sid in row.student_ids],
                "criteria": {
                    "competency_id": row.competency_id,
                    "mastery_level": row.mastery_level.value,
                },
                "recommended_action": f"Collective remediation for {row.competency_id}",
            })

    # Sort by student count descending
    groups.sort(key=lambda x: x["student_count"], reverse=True)
    return groups


async def _group_by_error_type(
    db: AsyncSession, filters: HeatmapFilters
) -> List[Dict[str, Any]]:
    """Group students by shared error types."""
    # Get error patterns from diagnostic answers
    query = (
        select(
            DiagnosticAnswer.error_classification,
            func.array_agg(DiagnosticAnswer.session_id).label("session_ids"),
        )
        .where(DiagnosticAnswer.error_classification != ErrorClassification.NONE)
        .group_by(DiagnosticAnswer.error_classification)
    )

    result = await db.execute(query)
    rows = result.all()

    groups = []
    for row in rows:
        session_ids = row.session_ids if row.session_ids else []

        # Get unique students from sessions
        student_query = select(DiagnosticSession.student_id).where(
            DiagnosticSession.id.in_(session_ids)
        )
        student_result = await db.execute(student_query)
        student_ids = list(set(student_result.scalars().all()))

        if len(student_ids) > 1:
            groups.append({
                "group_id": f"error_{row.error_classification.value}",
                "name": f"{row.error_classification.value} Errors",
                "student_count": len(student_ids),
                "student_ids": [str(sid) for sid in student_ids],
                "criteria": {
                    "error_type": row.error_classification.value,
                },
                "recommended_action": f"Focus on {row.error_classification.value.lower()} error prevention",
            })

    groups.sort(key=lambda x: x["student_count"], reverse=True)
    return groups


@router.get("/metrics", response_model=MetricResponse)
async def get_platform_metrics(
    class_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_expert),
) -> MetricResponse:
    """
    Get platform-level analytics metrics.

    Returns key performance indicators:
    - Gap Reduction Rate
    - Mastery Speed
    - Retention Rate
    - Effort vs Results
    - Resilience Score
    """
    # Get all competency profiles for calculation
    query = select(CompetencyProfile)
    result = await db.execute(query)
    profiles = list(result.scalars().all())

    if not profiles:
        return MetricResponse(
            gap_reduction_rate=0.0,
            mastery_speed=0.0,
            retention_rate=0.0,
            effort_vs_results=0.0,
            resilience_score=0.0,
            total_students=0,
            total_assessments=0,
        )

    # Calculate metrics
    total_students = len(set(p.student_id for p in profiles))

    # Gap Reduction: % of students improving from low to high mastery
    low_mastery = [p for p in profiles if p.mastery_level in [
        MasteryLevel.NOT_STARTED, MasteryLevel.ATTEMPTED
    ]]
    high_mastery = [p for p in profiles if p.mastery_level in [
        MasteryLevel.PROFICIENT, MasteryLevel.MASTERED
    ]]

    gap_reduction = (
        (len(high_mastery) / len(profiles) * 100) if profiles else 0
    )

    # Mastery Speed: Average sessions to mastery (simulated)
    mastery_speed = 2.5  # Placeholder - would calculate from actual data

    # Retention Rate: Students maintaining mastery
    retention_rate = 75.0  # Placeholder

    # Effort vs Results: Correlation metric
    effort_vs_results = 0.82  # Placeholder correlation coefficient

    # Resilience Score: Students recovering from failures
    resilience_score = 68.0  # Placeholder

    # Get total assessments
    session_query = select(func.count(DiagnosticSession.id))
    result = await db.execute(session_query)
    total_assessments = result.scalar() or 0

    return MetricResponse(
        gap_reduction_rate=round(gap_reduction, 1),
        mastery_speed=mastery_speed,
        retention_rate=retention_rate,
        effort_vs_results=effort_vs_results,
        resilience_score=resilience_score,
        total_students=total_students,
        total_assessments=total_assessments,
    )


@router.post("/export", response_model=ExportResponse)
async def export_analytics(
    request: ExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_expert),
) -> ExportResponse:
    """
    Export analytics data in PDF or CSV format.

    Generates printable remediation cards or detailed reports.
    """
    exporter = ReportExporter(db)

    try:
        if request.format == "csv":
            file_path = await exporter.export_csv(
                request.report_type,
                request.filters,
                request.student_ids,
            )
        elif request.format == "pdf":
            file_path = await exporter.export_pdf(
                request.report_type,
                request.filters,
                request.student_ids,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported format: {request.format}",
            )

        return ExportResponse(
            success=True,
            file_path=file_path,
            format=request.format,
            report_type=request.report_type,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}",
        )


# Add missing import
from datetime import datetime, timezone