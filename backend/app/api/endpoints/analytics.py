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
    RemediationCardsResponse,
    StudentCompetencyRow,
)
from app.services.analytics_service import AnalyticsService
from app.services.report_exporter import ReportExporter

router = APIRouter()


def _resolve_tenant_organization_id(current_user: User) -> Optional[UUID]:
    """
    Resolve active organization ID for tenant context from current_user or request context.
    Eliminates hardcoded zero-UUID sentinels by returning the explicit tenant ID or None.
    """
    from app.core.tenant import get_optional_active_organization_id

    return getattr(current_user, "organization_id", None) or get_optional_active_organization_id()


@router.get("/remediation-cards", response_model=RemediationCardsResponse)
async def get_remediation_cards(
    student_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert),
) -> RemediationCardsResponse:
    """
    Get printable remediation cards data for individual students or all students with gaps.
    Delegates to AnalyticsService for real tenant-isolated remediation card payload generation.
    """
    org_id = _resolve_tenant_organization_id(current_user)
    service = AnalyticsService(db)
    return await service.get_remediation_cards(organization_id=org_id, student_id=student_id)


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
    org_id = _resolve_tenant_organization_id(current_user)
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
    org_id = _resolve_tenant_organization_id(current_user)
    service = AnalyticsService(db)
    return await service.get_heatmap(
        organization_id=org_id,
        module_id=module_id,
        filters=filters,
    )


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

    org_id = _resolve_tenant_organization_id(current_user)

    service = AnalyticsService(db)
    return await service.auto_group_students(
        organization_id=org_id,
        filters=filters,
        group_by=group_by,
    )


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
            mastery_speed_days=0.0,
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
        mastery_speed_days=mastery_speed,
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

    org_id = _resolve_tenant_organization_id(current_user)

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
    Export analytics data in PDF or CSV format via POST request.
    Delegates to AnalyticsService for tenant isolation.
    """
    if request.format not in ("csv", "pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {request.format}",
        )

    org_id = _resolve_tenant_organization_id(current_user)

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


@router.get("/remediation-cards", response_model=RemediationCardsResponse)
async def get_remediation_cards(
    student_id: Optional[UUID] = Query(None),
    group_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert),
) -> RemediationCardsResponse:
    """
    Get print-formatted remediation card data for a single student or a remediation group.
    """
    if not student_id and not group_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either student_id or group_id must be provided",
        )

    from app.core.tenant import get_optional_active_organization_id
    org_id = getattr(current_user, "organization_id", None) or get_optional_active_organization_id()
    if not org_id:
        org_id = UUID("00000000-0000-0000-0000-000000000000")

    service = AnalyticsService(db)
    try:
        return await service.get_remediation_cards(
            organization_id=org_id,
            student_id=student_id,
            group_id=group_id,
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch remediation cards: {str(e)}",
        )


# Add missing import
from datetime import datetime, timezone