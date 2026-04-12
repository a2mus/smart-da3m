"""
API endpoints for parent dashboard.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_expert, get_current_parent, get_db
from app.models.alert import AlertRecipient, AlertStatus, PedagogicalAlert
from app.models.user import User
from app.schemas.alert import (
    AlertListResponse,
    AlertMarkReadRequest,
    AlertMarkReadResponse,
    AlertResponse,
    ParentAlertSummary,
)
from app.schemas.dashboard import (
    ChildDashboardData,
    ChildProgressSummary,
    ParentDashboardResponse,
)
from app.services.alert_manager import AlertManager
from app.services.dashboard_service import DashboardAggregator

router = APIRouter()


@router.get(
    "/overview",
    response_model=ParentDashboardResponse,
    summary="Get parent dashboard overview",
)
async def get_dashboard_overview(
    child_id: Optional[UUID] = Query(None, description="Filter by specific child"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_parent),
) -> ParentDashboardResponse:
    """
    Get the parent dashboard with all children's progress data.

    Returns qualitative summaries, subject progress, recent activities,
    and actionable recommendations for each child.
    """
    aggregator = DashboardAggregator(db)

    # Get dashboard data
    dashboard_data = await aggregator.get_parent_dashboard(current_user.id)

    # Filter by specific child if requested
    if child_id:
        dashboard_data["children"] = [
            c for c in dashboard_data["children"] if c["id"] == str(child_id)
        ]
        dashboard_data["children_count"] = len(dashboard_data["children"])

    return ParentDashboardResponse(**dashboard_data)


@router.get(
    "/children/{child_id}",
    response_model=ChildDashboardData,
    summary="Get detailed data for a specific child",
)
async def get_child_details(
    child_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_parent),
) -> ChildDashboardData:
    """Get detailed dashboard data for a specific child."""
    aggregator = DashboardAggregator(db)

    # Verify the child belongs to this parent
    children = await aggregator.get_children_for_parent(current_user.id)
    child_ids = [str(c.id) for c in children]

    if str(child_id) not in child_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this child's data",
        )

    child_data = await aggregator.get_child_dashboard_data(child_id)
    return ChildDashboardData(**child_data)


@router.get(
    "/children",
    response_model=List[ChildProgressSummary],
    summary="Get list of parent's children with summaries",
)
async def get_children_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_parent),
) -> List[ChildProgressSummary]:
    """Get a simplified list of all children with basic progress info."""
    aggregator = DashboardAggregator(db)

    children = await aggregator.get_children_for_parent(current_user.id)

    summaries = []
    for child in children:
        # Get basic data for summary
        try:
            child_data = await aggregator.get_child_dashboard_data(child.id)
            summaries.append(
                ChildProgressSummary(
                    child_id=str(child.id),
                    name=child_data["name"],
                    overall_progress=child_data["overall_progress"],
                    last_active=child_data["last_active"],
                    needs_attention=any(
                        s["score"] < 50 for s in child_data["subjects"]
                    ),
                )
            )
        except Exception:
            # If data retrieval fails, still include child with defaults
            summaries.append(
                ChildProgressSummary(
                    child_id=str(child.id),
                    name=f"Student {str(child.id)[:8]}",
                    overall_progress=0,
                    needs_attention=False,
                )
            )

    return summaries


# ==================== Alert Endpoints ====================


@router.get(
    "/alerts",
    response_model=AlertListResponse,
    summary="Get alerts for the current user",
)
async def get_alerts(
    unread_only: bool = Query(False, description="Filter to unread alerts only"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_parent),
) -> AlertListResponse:
    """Get pedagogical alerts for the authenticated parent."""
    aggregator = DashboardAggregator(db)
    children = await aggregator.get_children_for_parent(current_user.id)
    child_ids = [c.id for c in children]

    if not child_ids:
        return AlertListResponse(items=[], total=0, unread_count=0)

    query = select(PedagogicalAlert).where(
        PedagogicalAlert.student_id.in_(child_ids)
    )

    if unread_only:
        query = query.where(PedagogicalAlert.status == AlertStatus.UNREAD)

    query = query.order_by(PedagogicalAlert.created_at.desc())
    result = await db.execute(query)
    alerts = result.scalars().all()
    unread_count = sum(1 for a in alerts if a.status == AlertStatus.UNREAD)

    return AlertListResponse(
        items=list(alerts),
        total=len(alerts),
        unread_count=unread_count,
    )


@router.post(
    "/alerts/mark-read",
    response_model=AlertMarkReadResponse,
    summary="Mark alerts as read",
)
async def mark_alerts_read(
    request: AlertMarkReadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_parent),
) -> AlertMarkReadResponse:
    """Mark specified alerts as read."""
    aggregator = DashboardAggregator(db)
    children = await aggregator.get_children_for_parent(current_user.id)
    child_ids = {c.id for c in children}

    marked_count = 0
    for alert_id in request.alert_ids:
        result = await db.execute(
            select(PedagogicalAlert).where(PedagogicalAlert.id == alert_id)
        )
        alert = result.scalar_one_or_none()

        if alert and alert.student_id in child_ids:
            alert.status = AlertStatus.READ
            alert.read_at = datetime.now(timezone.utc)
            marked_count += 1

    await db.commit()
    return AlertMarkReadResponse(marked_count=marked_count)


@router.get(
    "/alerts/expert",
    response_model=AlertListResponse,
    summary="Get all alerts for experts",
)
async def get_expert_alerts(
    severity: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert),
) -> AlertListResponse:
    """Get all pedagogical alerts for expert review."""
    query = select(PedagogicalAlert)
    if severity:
        query = query.where(PedagogicalAlert.severity == severity)
    query = query.order_by(PedagogicalAlert.severity.desc(), PedagogicalAlert.created_at.desc())
    result = await db.execute(query)
    alerts = result.scalars().all()
    unread_count = sum(1 for a in alerts if a.status == AlertStatus.UNREAD)

    return AlertListResponse(
        items=list(alerts),
        total=len(alerts),
        unread_count=unread_count,
    )


@router.get(
    "/children/{child_id}/alerts",
    response_model=List[ParentAlertSummary],
    summary="Get alerts for a specific child",
)
async def get_child_alerts(
    child_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_parent),
) -> List[ParentAlertSummary]:
    """Get simplified alerts for a specific child."""
    aggregator = DashboardAggregator(db)
    children = await aggregator.get_children_for_parent(current_user.id)
    child_ids = {str(c.id) for c in children}

    if str(child_id) not in child_ids:
        raise HTTPException(status_code=403, detail="Access denied")

    result = await db.execute(
        select(PedagogicalAlert)
        .where(PedagogicalAlert.student_id == child_id)
        .order_by(PedagogicalAlert.created_at.desc())
        .limit(10)
    )
    alerts = result.scalars().all()

    return [
        ParentAlertSummary(
            id=alert.id,
            severity=alert.severity,
            message=alert.simplified_message,
            created_at=alert.created_at,
            is_read=alert.status != AlertStatus.UNREAD,
        )
        for alert in alerts
    ]
