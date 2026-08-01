"""
Unit and integration tests for AlertManager production code path wiring (Story 4.2).
Tests alert generation, DB persistence, Redis Pub/Sub publishing, and since timestamp filter.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.core.tenant import reset_active_organization_id, set_active_organization_id
from app.models.alert import AlertSeverity, AlertStatus, AlertTriggerType, PedagogicalAlert
from app.models.content import Module, Question
from app.models.diagnostic import CompetencyProfile, DiagnosticSession, DiagnosticSessionStatus, MasteryLevel
from app.models.organization import Organization, OrganizationMember, OrganizationType
from app.models.user import User, UserRole
from app.services.alert_manager import AlertManager


@pytest.fixture
async def test_org(db: AsyncSession) -> Organization:
    """Create a test organization."""
    org = Organization(
        name="Alert Test School",
        type=OrganizationType.SCHOOL,
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org


@pytest.fixture
async def student_user(db: AsyncSession, test_org: Organization) -> User:
    """Create a student user for testing."""
    user = User(
        email=None,
        pin_code_hash="1234",
        role=UserRole.STUDENT,
        parent_id=None,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    member = OrganizationMember(
        user_id=user.id,
        organization_id=test_org.id,
        role=UserRole.STUDENT,
    )
    db.add(member)
    await db.commit()
    return user


@pytest.fixture
async def parent_user(db: AsyncSession, student_user: User, test_org: Organization) -> User:
    """Create a parent user linked to student."""
    parent = User(
        email="parent_alert@test.com",
        role=UserRole.PARENT,
    )
    db.add(parent)
    await db.commit()
    await db.refresh(parent)

    student_user.parent_id = parent.id
    await db.commit()
    return parent


@pytest.fixture
async def auth_headers_student(student_user: User, test_org: Organization) -> dict:
    """Generate auth headers for student."""
    token = create_access_token(
        subject=str(student_user.id),
        additional_claims={
            "organizations": [
                {
                    "id": str(test_org.id),
                    "role": "STUDENT",
                    "type": "SCHOOL",
                }
            ]
        },
    )
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Organization-Id": str(test_org.id),
    }


@pytest.fixture
async def auth_headers_parent(parent_user: User, test_org: Organization) -> dict:
    """Generate auth headers for parent."""
    token = create_access_token(
        subject=str(parent_user.id),
        additional_claims={
            "organizations": [
                {
                    "id": str(test_org.id),
                    "role": "PARENT",
                    "type": "SCHOOL",
                }
            ]
        },
    )
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Organization-Id": str(test_org.id),
    }


@pytest.fixture
async def test_module(db: AsyncSession, test_org: Organization) -> Module:
    """Create a test module."""
    token = set_active_organization_id(test_org.id)
    try:
        module = Module(
            organization_id=test_org.id,
            subject="Mathematics",
            grade_level="السنة 4",
            domain="Numbers & Operations",
            competency_id="MATH-ALERT-01",
        )
        db.add(module)
        await db.commit()
        await db.refresh(module)
        return module
    finally:
        reset_active_organization_id(token)


@pytest.mark.asyncio
async def test_alert_manager_check_passport_failure():
    """Unit test: AlertManager.check_passport_failure generates PASSPORT_FAILED alert at WARNING severity."""
    alert_mgr = AlertManager()
    student_id = uuid4()
    alert = alert_mgr.check_passport_failure(
        student_id=student_id,
        competency_id="MATH-ALERT-01",
    )

    assert alert is not None
    assert alert["student_id"] == student_id
    assert alert["severity"] == AlertSeverity.WARNING
    assert alert["trigger_type"] == AlertTriggerType.PASSPORT_FAILED


@pytest.mark.asyncio
async def test_process_and_persist_alerts_unit(db: AsyncSession, test_org: Organization, student_user: User):
    """Unit test: process_and_persist_alerts persists alert to DB and publishes SSE event."""
    alert_mgr = AlertManager()
    alert_data = alert_mgr.check_passport_failure(
        student_id=student_user.id,
        competency_id="MATH-ALERT-01",
    )
    assert alert_data is not None

    with patch("app.services.alert_manager.publish_tenant_event", new_callable=AsyncMock) as mock_publish:
        mock_publish.return_value = 1

        persisted = await alert_mgr.process_and_persist_alerts(
            alerts=[alert_data],
            organization_id=test_org.id,
            db=db,
        )

        assert len(persisted) == 1
        alert_obj = persisted[0]
        assert alert_obj.organization_id == test_org.id
        assert alert_obj.student_id == student_user.id
        assert alert_obj.trigger_type == AlertTriggerType.PASSPORT_FAILED
        assert alert_obj.severity == AlertSeverity.WARNING

        mock_publish.assert_called_once()
        call_args = mock_publish.call_args
        assert call_args[0][0] == test_org.id
        assert call_args[0][1] == "pedagogical_alert"


@pytest.mark.asyncio
async def test_process_and_persist_alerts_redis_failure_resilience(db: AsyncSession, test_org: Organization, student_user: User):
    """Unit test: Redis publish exception is caught gracefully and DB persistence still succeeds."""
    alert_mgr = AlertManager()
    alert_data = alert_mgr.check_passport_failure(
        student_id=student_user.id,
        competency_id="MATH-ALERT-01",
    )
    assert alert_data is not None

    with patch("app.services.alert_manager.publish_tenant_event", side_effect=RuntimeError("Redis connection lost")):
        persisted = await alert_mgr.process_and_persist_alerts(
            alerts=[alert_data],
            organization_id=test_org.id,
            db=db,
        )

        assert len(persisted) == 1
        assert persisted[0].trigger_type == AlertTriggerType.PASSPORT_FAILED


@pytest.mark.asyncio
async def test_get_alerts_since_filter(
    async_client: AsyncClient,
    auth_headers_parent: dict,
    student_user: User,
    test_org: Organization,
    db: AsyncSession,
):
    """Integration test: GET /api/v1/dashboard/alerts?since={timestamp} filters alerts by timestamp."""
    token = set_active_organization_id(test_org.id)
    try:
        past_time = datetime.now(timezone.utc) - timedelta(hours=2)
        old_alert = PedagogicalAlert(
            organization_id=test_org.id,
            student_id=student_user.id,
            trigger_type=AlertTriggerType.REPEATED_FAILURE,
            severity=AlertSeverity.WARNING,
            simplified_message="Old alert",
            expert_message="Old alert details",
            status=AlertStatus.UNREAD,
            created_at=past_time,
        )
        db.add(old_alert)

        recent_time = datetime.now(timezone.utc)
        new_alert = PedagogicalAlert(
            organization_id=test_org.id,
            student_id=student_user.id,
            trigger_type=AlertTriggerType.PASSPORT_FAILED,
            severity=AlertSeverity.WARNING,
            simplified_message="New alert",
            expert_message="New alert details",
            status=AlertStatus.UNREAD,
            created_at=recent_time,
        )
        db.add(new_alert)
        await db.commit()
    finally:
        reset_active_organization_id(token)

    # Filter since 1 hour ago
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    response = await async_client.get(
        f"/api/v1/dashboard/alerts?since={cutoff}",
        headers=auth_headers_parent,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["simplified_message"] == "New alert"
