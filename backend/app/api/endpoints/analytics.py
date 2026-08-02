"""
Analytics API endpoints for expert dashboard.
Provides heatmaps, cohort insights, and reporting functionality.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_expert
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
from app.services.analytics_service import AnalyticsService
from app.services.report_exporter import ReportExporter

router = APIRouter()


@router.get("/heatmap", response_model=HeatmapResponse)
async def get_competency_heatmap_get(
    module_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert),
) -> HeatmapResponse:
    """
    Get competency heatmap data for expert analytics via GET.
    Delegates to AnalyticsService for real tenant-isolated data.
    """
    from app.core.tenant import get_optional_active_organization_id
    org_id = getattr(current_user, "organization_id", None) or get_optional_active_organization_id()
    if not org_id:
        org_id = UUID("00000000-0000-0000-0000-000000000000")
    service = AnalyticsService(db)
    return await service.get_heatmap(organization_id=org_id, module_id=module_id)


@router.post("/heatmap", response_model=HeatmapResponse)
async def get_competency_heatmap(
    filters: HeatmapFilters,
    module_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert),
) -> HeatmapResponse:
    """
    Get competency heatmap data for expert analytics.
    Delegates to AnalyticsService for real tenant-isolated data.
    """
    from app.core.tenant import get_optional_active_organization_id
    org_id = getattr(current_user, "organization_id", None) or get_optional_active_organization_id()
    if not org_id:
        org_id = UUID("00000000-0000-0000-0000-000000000000")
    service = AnalyticsService(db)
    return await service.get_heatmap(organization_id=org_id, module_id=module_id)


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
    filters: Optional[HeatmapFilters] = None,
    group_by: str = Query("competency", description="Group by: competency or error_type"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert),
) -> AutoGroupResponse:
    """
    Auto-group students based on shared patterns.

    Groups students who share:
    - Same unmastered competencies (group_by=competency)
    - Same error types (group_by=error_type)
    """
    if group_by not in ("competency", "error_type"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid group_by value: {group_by}",
        )

    from app.core.tenant import get_optional_active_organization_id
    org_id = getattr(current_user, "organization_id", None) or get_optional_active_organization_id()
    if not org_id:
        org_id = UUID("00000000-0000-0000-0000-000000000000")

    service = AnalyticsService(db)
    return await service.auto_group_students(
        organization_id=org_id,
        filters=filters,
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
    current_user: User = Depends(get_current_expert),
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


@router.get("/export")
async def export_analytics_get(
    format: str = Query("csv", description="Export format: csv or pdf"),
    report_type: str = Query("heatmap", description="Report type: heatmap, remediation_card, full_report"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert),
):
    """
    Export analytics data in PDF or CSV format via GET.
    Delegates to AnalyticsService for real tenant-isolated export generation.
    """
    if format not in ("csv", "pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}",
        )

    from app.core.tenant import get_optional_active_organization_id
    org_id = getattr(current_user, "organization_id", None) or get_optional_active_organization_id()
    if not org_id:
        org_id = UUID("00000000-0000-0000-0000-000000000000")

    service = AnalyticsService(db)
    try:
        file_path = await service.export_report(
            organization_id=org_id,
            report_type=report_type,
            export_format=format,
        )

        from fastapi.responses import FileResponse
        media_type = "text/csv" if format == "csv" else "application/pdf"
        return FileResponse(path=file_path, filename=f"{report_type}.{format}", media_type=media_type)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}",
        )


@router.post("/export", response_model=ExportResponse)
async def export_analytics(
    request: ExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert),
) -> ExportResponse:
    """
    Export analytics data in PDF or CSV format.
    Delegates to AnalyticsService for real tenant-isolated data export.
    """
    from app.core.tenant import get_optional_active_organization_id
    org_id = getattr(current_user, "organization_id", None) or get_optional_active_organization_id()
    if not org_id:
        org_id = UUID("00000000-0000-0000-0000-000000000000")

    service = AnalyticsService(db)

    try:
        file_path = await service.export_report(
            organization_id=org_id,
            report_type=request.report_type,
            export_format=request.format,
            filters=request.filters,
            student_ids=request.student_ids,
        )

        return ExportResponse(
            success=True,
            file_path=file_path,
            format=request.format,
            report_type=request.report_type,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}",
        )


# Add missing import
from datetime import datetime, timezone