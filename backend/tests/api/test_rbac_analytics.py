"""
Unit & API integration tests for RBAC role check enum case fix.
Verifies `require_expert` and RBAC authorization behavior.
"""

import uuid
import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, require_expert
from app.models.organization import Organization, OrganizationMember, OrganizationType
from app.models.user import User, UserRole


def test_require_expert_with_expert_user():
    """Verify require_expert permits users with UserRole.EXPERT."""
    expert_user = User(role=UserRole.EXPERT)
    result = require_expert(expert_user)
    assert result == expert_user


def test_require_expert_with_student_user():
    """Verify require_expert rejects users with UserRole.STUDENT with 403."""
    student_user = User(role=UserRole.STUDENT)
    with pytest.raises(HTTPException) as exc_info:
        require_expert(student_user)
    assert exc_info.value.status_code == 403
    assert "Expert access required" in exc_info.value.detail


def test_require_expert_with_parent_user():
    """Verify require_expert rejects users with UserRole.PARENT with 403."""
    parent_user = User(role=UserRole.PARENT)
    with pytest.raises(HTTPException) as exc_info:
        require_expert(parent_user)
    assert exc_info.value.status_code == 403
    assert "Expert access required" in exc_info.value.detail


def test_require_expert_with_none():
    """Verify require_expert rejects None user with 403."""
    with pytest.raises(HTTPException) as exc_info:
        require_expert(None)
    assert exc_info.value.status_code == 403
    assert "Expert access required" in exc_info.value.detail


def test_metric_response_schema_fields():
    """Verify MetricResponse schema contains both mastery_speed and mastery_speed_days."""
    from app.schemas.analytics import MetricResponse

    metric = MetricResponse(
        gap_reduction_rate=85.0,
        mastery_speed=2.5,
        mastery_speed_days=2.5,
        retention_rate=90.0,
        effort_vs_results=0.8,
        resilience_score=75.0,
        total_students=10,
        total_assessments=50,
    )
    dump = metric.model_dump()
    assert dump["mastery_speed"] == 2.5
    assert dump["mastery_speed_days"] == 2.5


@pytest.mark.asyncio
async def test_get_platform_metrics_http_response_mastery_speed_days(
    async_client: AsyncClient, db: AsyncSession
):
    """Verify GET /api/v1/analytics/metrics HTTP endpoint returns mastery_speed_days field in JSON payload."""
    org = Organization(name=f"Metrics Test Org {uuid.uuid4().hex[:6]}", type=OrganizationType.SCHOOL)
    db.add(org)
    await db.commit()

    expert = User(
        email=f"expert_metrics_{uuid.uuid4().hex[:8]}@test.com",
        hashed_password="hashed_password",
        role=UserRole.EXPERT,
    )
    db.add(expert)
    await db.commit()

    member = OrganizationMember(
        user_id=expert.id,
        organization_id=org.id,
        role=UserRole.EXPERT,
    )
    db.add(member)
    await db.commit()

    token = create_access_token(subject=expert.id, additional_claims={"org_id": str(org.id)})
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Organization-ID": str(org.id),
    }

    response = await async_client.get(
        "/api/v1/analytics/metrics",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "mastery_speed_days" in data
    assert isinstance(data["mastery_speed_days"], (float, int))


