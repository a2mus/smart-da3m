"""
Unit and integration tests for Printable Remediation Cards (Story 9.4).
"""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.core.tenant import set_active_organization_id
from app.models.diagnostic import CompetencyProfile, MasteryLevel
from app.models.organization import Organization, OrganizationMember, OrganizationType
from app.models.user import User, UserRole
from app.services.analytics_service import AnalyticsService


@pytest.mark.asyncio
async def test_get_remediation_cards_service(db: AsyncSession):
    org_id = uuid.uuid4()
    set_active_organization_id(org_id)

    student = User(
        id=uuid.uuid4(),
        email=f"card_student_{uuid.uuid4().hex[:8]}@example.com",
        role=UserRole.STUDENT,
        hashed_password="hash",
    )
    db.add(student)
    await db.commit()

    member = OrganizationMember(
        user_id=student.id,
        organization_id=org_id,
        role=UserRole.STUDENT,
    )
    db.add(member)
    await db.commit()

    profile = CompetencyProfile(
        id=uuid.uuid4(),
        student_id=student.id,
        organization_id=org_id,
        competency_id="COMP_MATH_01",
        mastery_level=MasteryLevel.NOT_STARTED,
        p_learned=0.1,
    )
    db.add(profile)
    await db.commit()

    service = AnalyticsService(db)
    response = await service.get_remediation_cards(
        organization_id=org_id,
        student_id=student.id,
    )

    assert response.total_cards == 1
    assert response.cards[0].student_id == student.id
    assert len(response.cards[0].items) == 1
    assert response.cards[0].items[0].competency_id == "COMP_MATH_01"


@pytest.mark.asyncio
async def test_get_remediation_cards_endpoint_validation(async_client: AsyncClient, db: AsyncSession):
    expert = User(
        id=uuid.uuid4(),
        email=f"expert_{uuid.uuid4().hex[:8]}@example.com",
        role=UserRole.EXPERT,
        hashed_password="hash",
    )
    db.add(expert)
    await db.commit()

    token = create_access_token(subject=str(expert.id), additional_claims={"role": UserRole.EXPERT.value})
    headers = {"Authorization": f"Bearer {token}"}

    # Missing parameters should return 400 Bad Request
    response = await async_client.get("/api/v1/analytics/remediation-cards", headers=headers)
    assert response.status_code == 400
