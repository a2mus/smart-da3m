"""
Integration tests for parent dashboard endpoints and DashboardRepo tenant isolation (Story 8.1).
"""

import uuid
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.diagnostic import CompetencyProfile, MasteryLevel
from app.models.organization import Organization, OrganizationMember, OrganizationType
from app.models.user import User, UserRole
from app.repositories.dashboard_repo import DashboardRepo
from app.services.dashboard_service import DashboardAggregator


@pytest.fixture
async def sample_organization(db: AsyncSession) -> Organization:
    org = Organization(name="Test Org", type=OrganizationType.SCHOOL)
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org


@pytest.fixture
async def parent_user(db: AsyncSession, sample_organization: Organization) -> User:
    user = User(
        email=f"parent_{uuid.uuid4().hex[:8]}@test.com",
        hashed_password="hashed_password",
        role=UserRole.PARENT,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    member = OrganizationMember(
        user_id=user.id,
        organization_id=sample_organization.id,
        role=UserRole.PARENT,
    )
    db.add(member)
    await db.commit()
    return user


@pytest.fixture
async def student_user(db: AsyncSession, parent_user: User, sample_organization: Organization) -> User:
    user = User(
        email=None,
        pin_code_hash="1234",
        role=UserRole.STUDENT,
        parent_id=parent_user.id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    member = OrganizationMember(
        user_id=user.id,
        organization_id=sample_organization.id,
        role=UserRole.STUDENT,
    )
    db.add(member)
    await db.commit()
    return user


@pytest.fixture
async def auth_headers_parent(parent_user: User, sample_organization: Organization) -> dict:
    token = create_access_token(subject=parent_user.id)
    return {
        "Authorization": f"Bearer {token}",
        "X-Organization-Id": str(sample_organization.id),
        "Content-Type": "application/json",
    }


class TestDashboardRepoAndEndpoints:
    """Test suite for DashboardRepo and /api/v1/dashboard endpoints."""

    async def test_dashboard_repo_tenant_filtering(
        self, db: AsyncSession, parent_user: User, student_user: User, sample_organization: Organization
    ) -> None:
        """Test DashboardRepo correctly fetches children within tenant scope."""
        repo = DashboardRepo(db, tenant_id=sample_organization.id)
        children = await repo.get_children_for_parent(parent_user.id)
        assert len(children) == 1
        assert children[0].id == student_user.id

    async def test_dashboard_repo_other_tenant_isolation(
        self, db: AsyncSession, parent_user: User, student_user: User
    ) -> None:
        """Test DashboardRepo ignores records outside active tenant scope."""
        other_org = Organization(name="Other Org", type=OrganizationType.SCHOOL)
        db.add(other_org)
        await db.commit()

        repo = DashboardRepo(db, tenant_id=other_org.id)
        children = await repo.get_children_for_parent(parent_user.id)
        assert len(children) == 0

    async def test_get_dashboard_overview_endpoint(
        self,
        async_client: AsyncClient,
        auth_headers_parent: dict,
        student_user: User,
        sample_organization: Organization,
        db: AsyncSession,
    ) -> None:
        """Test GET /api/v1/dashboard/overview returns real dashboard response."""
        profile = CompetencyProfile(
            organization_id=sample_organization.id,
            student_id=student_user.id,
            competency_id="MATH-4-NUM-01",
            mastery_level=MasteryLevel.PROFICIENT,
            p_learned=0.8,
        )
        db.add(profile)
        await db.commit()

        response = await async_client.get(
            "/api/v1/dashboard/overview",
            headers=auth_headers_parent,
        )

        assert response.status_code == 200
        data = response.json()
        assert "children" in data
        assert data["children_count"] == 1
        assert data["children"][0]["id"] == str(student_user.id)
        assert len(data["children"][0]["subjects"]) == 1
        assert data["children"][0]["subjects"][0]["score"] == 75
        assert "daily_recommendation" in data["children"][0]
        assert data["children"][0]["daily_recommendation"]["off_platform"] is True

    async def test_daily_reinforcement_recommendation_caching(
        self,
        async_client: AsyncClient,
        auth_headers_parent: dict,
        student_user: User,
        sample_organization: Organization,
        db: AsyncSession,
    ) -> None:
        """Test story 8.4 daily reinforcement recommendation generation and caching."""
        profile = CompetencyProfile(
            organization_id=sample_organization.id,
            student_id=student_user.id,
            competency_id="ARABIC-GRAMMAR-01",
            mastery_level=MasteryLevel.ATTEMPTED,
            p_learned=0.2,
        )
        db.add(profile)
        await db.commit()

        res1 = await async_client.get(
            "/api/v1/dashboard/overview",
            headers=auth_headers_parent,
        )
        assert res1.status_code == 200
        rec1 = res1.json()["children"][0]["daily_recommendation"]
        assert rec1["off_platform"] is True
        assert "competency_id" in rec1

        res2 = await async_client.get(
            "/api/v1/dashboard/overview",
            headers=auth_headers_parent,
        )
        assert res2.status_code == 200
        rec2 = res2.json()["children"][0]["daily_recommendation"]
        assert rec1["title"] == rec2["title"]

    async def test_get_children_list_endpoint(
        self,
        async_client: AsyncClient,
        auth_headers_parent: dict,
        student_user: User,
    ) -> None:
        """Test GET /api/v1/dashboard/children returns list of parent's children."""
        response = await async_client.get(
            "/api/v1/dashboard/children",
            headers=auth_headers_parent,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["child_id"] == str(student_user.id)
