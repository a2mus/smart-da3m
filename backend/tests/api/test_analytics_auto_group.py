"""
Unit and API integration tests for Auto-Grouping into Remediation Groups (Story 9.2).
"""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.core.tenant import set_active_organization_id
from app.engines.remediation_engine import RemediationEngine
from app.models.diagnostic import CompetencyProfile, MasteryLevel
from app.models.organization import Organization, OrganizationMember, OrganizationType
from app.models.user import User, UserRole
from app.services.analytics_service import AnalyticsService


def test_remediation_engine_auto_group_by_competency():
    """Verify stateless engine auto-grouping by competency."""
    engine = RemediationEngine()
    records = [
        {"student_id": "s1", "competency_id": "MATH-01", "mastery_level": "NOT_STARTED", "error_type": "PROCESS"},
        {"student_id": "s2", "competency_id": "MATH-01", "mastery_level": "NOT_STARTED", "error_type": "RESOURCE"},
        {"student_id": "s3", "competency_id": "MATH-02", "mastery_level": "ATTEMPTED", "error_type": "PROCESS"},
    ]
    groups = engine.auto_group_students(records, group_by="competency")
    assert len(groups) == 2
    g1 = next(g for g in groups if g["competency"] == "MATH-01")
    assert g1["student_count"] == 2
    assert "s1" in g1["student_ids"]
    assert "s2" in g1["student_ids"]


def test_remediation_engine_auto_group_by_error_type():
    """Verify stateless engine auto-grouping by error_type."""
    engine = RemediationEngine()
    records = [
        {"student_id": "s1", "competency_id": "MATH-01", "mastery_level": "NOT_STARTED", "error_type": "PROCESS"},
        {"student_id": "s2", "competency_id": "MATH-02", "mastery_level": "ATTEMPTED", "error_type": "PROCESS"},
        {"student_id": "s3", "competency_id": "MATH-01", "mastery_level": "NOT_STARTED", "error_type": "RESOURCE"},
    ]
    groups = engine.auto_group_students(records, group_by="error_type")
    assert len(groups) == 2
    process_group = next(g for g in groups if g["error_type"] == "PROCESS")
    assert process_group["student_count"] == 2
    assert "s1" in process_group["student_ids"]
    assert "s2" in process_group["student_ids"]


@pytest.mark.asyncio
async def test_analytics_service_auto_group(db: AsyncSession):
    """Verify AnalyticsService delegates auto grouping to repo and RemediationEngine."""
    org_id = uuid.uuid4()
    set_active_organization_id(org_id)
    s1_id = uuid.uuid4()
    s2_id = uuid.uuid4()

    cp1 = CompetencyProfile(
        id=uuid.uuid4(),
        student_id=s1_id,
        organization_id=org_id,
        competency_id="COMP-A",
        mastery_level=MasteryLevel.NOT_STARTED,
        p_learned=0.1,
    )
    cp2 = CompetencyProfile(
        id=uuid.uuid4(),
        student_id=s2_id,
        organization_id=org_id,
        competency_id="COMP-A",
        mastery_level=MasteryLevel.NOT_STARTED,
        p_learned=0.15,
    )
    db.add_all([cp1, cp2])
    await db.commit()

    service = AnalyticsService(db)
    res = await service.auto_group_students(organization_id=org_id, group_by="competency")
    assert res.total_groups == 1
    assert res.group_by == "competency"
    assert len(res.groups) == 1
    group = res.groups[0]
    assert group["competency"] == "COMP-A"
    assert group["student_count"] == 2
    assert str(s1_id) in group["student_ids"]
    assert str(s2_id) in group["student_ids"]


@pytest.mark.asyncio
async def test_auto_group_endpoint_integration(async_client: AsyncClient, db: AsyncSession):
    """Verify POST /api/v1/analytics/auto-group endpoint returns clustered groups."""
    org = Organization(name="AutoGroup Test Org", type=OrganizationType.SCHOOL)
    db.add(org)
    await db.commit()

    expert = User(
        email=f"expert_{uuid.uuid4().hex[:8]}@test.com",
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

    student_user = User(
        email=f"student_{uuid.uuid4().hex[:8]}@test.com",
        hashed_password="hashed_password",
        role=UserRole.STUDENT,
    )
    db.add(student_user)
    await db.commit()

    cp = CompetencyProfile(
        id=uuid.uuid4(),
        student_id=student_user.id,
        organization_id=org.id,
        competency_id="SCI-01",
        mastery_level=MasteryLevel.ATTEMPTED,
        p_learned=0.3,
    )
    db.add(cp)
    await db.commit()

    token = create_access_token(subject=expert.id, additional_claims={"org_id": str(org.id)})
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Organization-ID": str(org.id),
    }

    response = await async_client.post(
        "/api/v1/analytics/auto-group?group_by=competency",
        headers=headers,
        json={},
    )
    assert response.status_code == 200
    data = response.json()
    assert "groups" in data
    assert data["group_by"] == "competency"
    assert data["total_groups"] == len(data["groups"])
    if data["groups"]:
        g = data["groups"][0]
        assert "competency" in g
        assert "students" in g
