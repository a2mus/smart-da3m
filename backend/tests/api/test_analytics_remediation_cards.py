"""
Tests for Printable Remediation Cards API endpoint and tenant isolation (Story 9.4).
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
async def test_get_remediation_cards_unauthenticated(async_client: AsyncClient):
    """Test GET /api/v1/analytics/remediation-cards without auth token returns 401."""
    response = await async_client.get("/api/v1/analytics/remediation-cards")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_remediation_cards_success(
    async_client: AsyncClient, db: AsyncSession
):
    """Test fetching remediation cards for expert user returns 200 and cards list."""
    org = Organization(name="Remediation Card Test Org", type=OrganizationType.SCHOOL)
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

    token = create_access_token(subject=expert.id, additional_claims={"org_id": str(org.id)})
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Organization-ID": str(org.id),
    }

    response = await async_client.get(
        "/api/v1/analytics/remediation-cards",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "cards" in data
    assert "total_cards" in data
    assert isinstance(data["cards"], list)


@pytest.mark.asyncio
async def test_get_remediation_cards_tenant_isolation(
    db: AsyncSession
):
    """Test that remediation cards are strictly isolated by active organization_id."""
    org_a_id = uuid.uuid4()
    org_b_id = uuid.uuid4()
    student_a_id = uuid.uuid4()
    student_b_id = uuid.uuid4()

    student_a = User(
        id=student_a_id,
        email=f"st_a_{uuid.uuid4().hex[:8]}@test.com",
        hashed_password="hash",
        role=UserRole.STUDENT,
    )
    student_b = User(
        id=student_b_id,
        email=f"st_b_{uuid.uuid4().hex[:8]}@test.com",
        hashed_password="hash",
        role=UserRole.STUDENT,
    )
    db.add_all([student_a, student_b])
    await db.commit()

    mem_a = OrganizationMember(user_id=student_a.id, organization_id=org_a_id, role=UserRole.STUDENT)
    mem_b = OrganizationMember(user_id=student_b.id, organization_id=org_b_id, role=UserRole.STUDENT)
    db.add_all([mem_a, mem_b])
    await db.commit()

    profile_a = CompetencyProfile(
        id=uuid.uuid4(),
        organization_id=org_a_id,
        student_id=student_a_id,
        competency_id="MATH_ADD_01",
        mastery_level=MasteryLevel.NOT_STARTED,
        p_learned=0.1,
    )
    profile_b = CompetencyProfile(
        id=uuid.uuid4(),
        organization_id=org_b_id,
        student_id=student_b_id,
        competency_id="MATH_SUB_01",
        mastery_level=MasteryLevel.ATTEMPTED,
        p_learned=0.3,
    )
    db.add_all([profile_a, profile_b])
    await db.commit()

    service = AnalyticsService(db)
    cards_response_a = await service.get_remediation_cards(organization_id=org_a_id)

    student_ids_a = [card.student_id for card in cards_response_a.cards]
    assert student_a_id in student_ids_a
    assert student_b_id not in student_ids_a


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
