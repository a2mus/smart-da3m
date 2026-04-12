"""
Integration tests for Parent Dashboard aggregator endpoint (T037).
Tests dashboard data aggregation and qualitative message generation.
"""

import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Module, Question
from app.models.diagnostic import (
    CompetencyProfile,
    DiagnosticAnswer,
    DiagnosticSession,
    MasteryLevel,
    RemediationGroup,
)
from app.models.remediation import RemediationPath, RemediationPathStatus
from app.models.user import User, UserRole


@pytest.fixture
async def parent_user(db: AsyncSession) -> User:
    """Create a parent user for testing."""
    user = User(
        email="parent@test.com",
        hashed_password="hashed_password",
        role=UserRole.PARENT,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def student_user(db: AsyncSession, parent_user: User) -> User:
    """Create a student user (child of parent) for testing."""
    user = User(
        email=None,
        pin_code_hash="1234",
        role=UserRole.STUDENT,
        parent_id=parent_user.id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def auth_headers_parent(parent_user: User) -> dict:
    """Generate auth headers for the parent user."""
    return {
        "Authorization": f"Bearer test-token-{parent_user.id}",
        "Content-Type": "application/json",
    }


@pytest.fixture
async def diagnostic_data(
    db: AsyncSession, student_user: User
) -> tuple:
    """Create diagnostic data for the student."""
    # Create a module
    module = Module(
        subject="Mathematics",
        grade_level="السنة 4",
        domain="Numbers & Operations",
        competency_id="MATH-4-NUM-01",
    )
    db.add(module)
    await db.flush()

    # Create diagnostic session
    session = DiagnosticSession(
        student_id=student_user.id,
        module_id=module.id,
        status="COMPLETED",
        recommended_group=RemediationGroup.B,
        completed_at=datetime.now(timezone.utc),
    )
    db.add(session)
    await db.flush()

    # Create competency profile
    profile = CompetencyProfile(
        student_id=student_user.id,
        competency_id="MATH-4-NUM-01",
        mastery_level=MasteryLevel.FAMILIAR,
        p_learned=0.55,
    )
    db.add(profile)
    await db.commit()

    return session, profile


class TestParentDashboardOverview:
    """Test suite for parent dashboard overview endpoint."""

    async def test_get_dashboard_overview(
        self,
        async_client: AsyncClient,
        auth_headers_parent: dict,
        parent_user: User,
        student_user: User,
        diagnostic_data: tuple,
        db: AsyncSession,
    ) -> None:
        """Test getting dashboard overview with child data."""
        response = await async_client.get(
            "/api/v1/dashboard/parent/overview",
            headers=auth_headers_parent,
        )

        assert response.status_code == 200
        data = response.json()

        # Check structure
        assert "children" in data
        assert len(data["children"]) == 1

        child = data["children"][0]
        assert child["id"] == str(student_user.id)
        assert "name" in child
        assert "subjects" in child
        assert "recent_activities" in child

    async def test_dashboard_shows_qualitative_messages(
        self,
        async_client: AsyncClient,
        auth_headers_parent: dict,
        student_user: User,
        diagnostic_data: tuple,
        db: AsyncSession,
    ) -> None:
        """Test that dashboard shows qualitative messages, not raw scores."""
        response = await async_client.get(
            "/api/v1/dashboard/parent/overview",
            headers=auth_headers_parent,
        )

        assert response.status_code == 200
        data = response.json()

        child = data["children"][0]

        # Should have smart messages
        assert "summary" in child
        assert isinstance(child["summary"], str)
        # Should NOT have raw numerical scores prominently displayed
        assert "raw_score" not in child

    async def test_dashboard_radar_chart_data(
        self,
        async_client: AsyncClient,
        auth_headers_parent: dict,
        student_user: User,
        db: AsyncSession,
    ) -> None:
        """Test that dashboard provides data for radar chart."""
        # Create profiles for multiple subjects
        subjects = [
            ("MATH-4-NUM-01", MasteryLevel.PROFICIENT),
            ("ARAB-4-LANG-01", MasteryLevel.MASTERED),
            ("FREN-4-LANG-01", MasteryLevel.FAMILIAR),
        ]

        for competency_id, mastery in subjects:
            profile = CompetencyProfile(
                student_id=student_user.id,
                competency_id=competency_id,
                mastery_level=mastery,
                p_learned=0.7 if mastery == MasteryLevel.PROFICIENT else 0.9,
            )
            db.add(profile)
        await db.commit()

        response = await async_client.get(
            "/api/v1/dashboard/parent/overview",
            headers=auth_headers_parent,
        )

        assert response.status_code == 200
        data = response.json()

        child = data["children"][0]
        assert "subjects" in child

        # Should have radar chart data for each subject
        for subject in child["subjects"]:
            assert "name" in subject
            assert "score" in subject
            assert "mastery_level" in subject
            assert isinstance(subject["score"], (int, float))

    async def test_dashboard_recommendations(
        self,
        async_client: AsyncClient,
        auth_headers_parent: dict,
        student_user: User,
        diagnostic_data: tuple,
        db: AsyncSession,
    ) -> None:
        """Test that dashboard provides actionable recommendations."""
        response = await async_client.get(
            "/api/v1/dashboard/parent/overview",
            headers=auth_headers_parent,
        )

        assert response.status_code == 200
        data = response.json()

        child = data["children"][0]
        assert "recommendations" in child
        assert len(child["recommendations"]) > 0

        # Recommendations should be specific and actionable
        rec = child["recommendations"][0]
        assert "title" in rec
        assert "description" in rec
        assert "duration" in rec

    async def test_dashboard_recent_activities(
        self,
        async_client: AsyncClient,
        auth_headers_parent: dict,
        student_user: User,
        diagnostic_data: tuple,
        db: AsyncSession,
    ) -> None:
        """Test that dashboard shows recent activities in bento grid format."""
        response = await async_client.get(
            "/api/v1/dashboard/parent/overview",
            headers=auth_headers_parent,
        )

        assert response.status_code == 200
        data = response.json()

        child = data["children"][0]
        assert "recent_activities" in child

        # Activities should have required fields
        for activity in child["recent_activities"]:
            assert "type" in activity
            assert "title" in activity
            assert "timestamp" in activity
            assert activity["type"] in ["DIAGNOSTIC", "REMEDIATION", "PASSPORT", "ACHIEVEMENT"]

    async def test_dashboard_unauthorized(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test that dashboard requires authentication."""
        response = await async_client.get("/api/v1/dashboard/parent/overview")
        assert response.status_code == 401

    async def test_dashboard_requires_parent_role(
        self,
        async_client: AsyncClient,
        db: AsyncSession,
    ) -> None:
        """Test that only parents can access parent dashboard."""
        # Create a student user (not parent)
        student = User(
            email=None,
            pin_code_hash="1234",
            role=UserRole.STUDENT,
        )
        db.add(student)
        await db.commit()

        headers = {
            "Authorization": f"Bearer test-token-{student.id}",
            "Content-Type": "application/json",
        }

        response = await async_client.get(
            "/api/v1/dashboard/parent/overview",
            headers=headers,
        )

        assert response.status_code == 403


class TestParentDashboardChildSelection:
    """Test suite for parent with multiple children."""

    async def test_multiple_children_display(
        self,
        async_client: AsyncClient,
        auth_headers_parent: dict,
        parent_user: User,
        db: AsyncSession,
    ) -> None:
        """Test dashboard displays multiple children."""
        # Create multiple children
        for i in range(3):
            child = User(
                email=None,
                pin_code_hash=f"123{i}",
                role=UserRole.STUDENT,
                parent_id=parent_user.id,
            )
            db.add(child)

            # Add diagnostic data for each
            module = Module(
                subject=f"Subject {i}",
                grade_level="السنة 4",
                domain="Test",
                competency_id=f"TEST-{i}",
            )
            db.add(module)
            await db.flush()

            profile = CompetencyProfile(
                student_id=child.id,
                competency_id=f"TEST-{i}",
                mastery_level=MasteryLevel.FAMILIAR,
                p_learned=0.5,
            )
            db.add(profile)

        await db.commit()

        response = await async_client.get(
            "/api/v1/dashboard/parent/overview",
            headers=auth_headers_parent,
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["children"]) == 3

    async def test_filter_by_child_id(
        self,
        async_client: AsyncClient,
        auth_headers_parent: dict,
        student_user: User,
        db: AsyncSession,
    ) -> None:
        """Test filtering dashboard data by specific child."""
        response = await async_client.get(
            f"/api/v1/dashboard/parent/overview?child_id={student_user.id}",
            headers=auth_headers_parent,
        )

        assert response.status_code == 200
        data = response.json()

        # Should only show the requested child
        assert len(data["children"]) == 1
        assert data["children"][0]["id"] == str(student_user.id)
