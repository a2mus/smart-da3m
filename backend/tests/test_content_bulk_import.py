"""
Unit and integration tests for bulk import endpoint POST /api/v1/content/bulk-import.
"""

from uuid import uuid4
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_expert_user
from app.core.tenant import reset_active_organization_id, set_active_organization_id
from app.main import app
from app.models.content import Module, ModuleStatus
from app.models.organization import Organization, OrganizationMember, OrganizationType
from app.models.user import User, UserRole


@pytest.fixture
async def test_org(db: AsyncSession) -> Organization:
    """Create a test organization."""
    org = Organization(
        name="Bulk Import School",
        type=OrganizationType.SCHOOL,
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org


@pytest.fixture(autouse=True)
def set_org_context(test_org: Organization):
    """Set active tenant organization for queries."""
    token = set_active_organization_id(test_org.id)
    yield
    reset_active_organization_id(token)


@pytest.fixture
async def expert_user(db: AsyncSession, test_org: Organization) -> User:
    """Create an expert user for testing."""
    user = User(
        email=f"expert-bulk-{uuid4()}@test.com",
        hashed_password="hashed_password",
        role=UserRole.EXPERT,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    member = OrganizationMember(
        organization_id=test_org.id,
        user_id=user.id,
        role=UserRole.EXPERT,
    )
    db.add(member)
    await db.commit()
    user.organization_id = test_org.id
    return user


@pytest.fixture
async def auth_headers(expert_user: User, test_org: Organization) -> dict:
    """Generate auth headers and override dependency for the expert user."""
    def get_expert_override():
        set_active_organization_id(test_org.id)
        return expert_user

    app.dependency_overrides[get_current_expert_user] = get_expert_override
    yield {
        "Authorization": f"Bearer test-token-{expert_user.id}",
        "X-Organization-Id": str(test_org.id),
        "Content-Type": "application/json",
    }
    app.dependency_overrides.pop(get_current_expert_user, None)


@pytest.fixture
async def test_module(db: AsyncSession, test_org: Organization) -> Module:
    """Create a test module."""
    module = Module(
        organization_id=test_org.id,
        title="Test Module for Bulk Import",
        description="Description",
        subject="ARABIC",
        grade_level="Y1",
        domain="Reading",
        competency_id="ARABIC-1-READ-01",
        status=ModuleStatus.DRAFT,
    )
    db.add(module)
    await db.commit()
    await db.refresh(module)
    return module


@pytest.mark.asyncio
async def test_bulk_import_questions_success(
    async_client: AsyncClient, auth_headers: dict, test_module: Module
) -> None:
    """Test bulk importing valid questions successfully."""
    payload = {
        "items": [
            {
                "entity_type": "question",
                "module_id": str(test_module.id),
                "data": {
                    "content": {
                        "text": "What is 2 + 2?",
                        "type": "multiple_choice",
                        "options": ["3", "4", "5"],
                        "correct_answer": "4",
                    },
                    "difficulty_level": 2,
                    "estimated_time_sec": 30,
                },
            },
            {
                "entity_type": "question",
                "module_id": str(test_module.id),
                "data": {
                    "content": {
                        "text": "What is 3 + 3?",
                        "type": "multiple_choice",
                        "options": ["5", "6", "7"],
                        "correct_answer": "6",
                    },
                    "difficulty_level": 3,
                    "estimated_time_sec": 45,
                },
            },
        ]
    }

    response = await async_client.post(
        "/api/v1/content/bulk-import",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["created"] == 2
    assert data["failed"] == 0
    assert data["errors"] == []


@pytest.mark.asyncio
async def test_bulk_import_partial_success(
    async_client: AsyncClient, auth_headers: dict, test_module: Module
) -> None:
    """Test partial success when valid and invalid rows are in payload."""
    payload = {
        "items": [
            {
                "entity_type": "question",
                "module_id": str(test_module.id),
                "data": {
                    "content": {
                        "text": "Valid Question",
                        "type": "multiple_choice",
                        "options": ["A", "B"],
                        "correct_answer": "A",
                    },
                },
            },
            {
                "entity_type": "question",
                "data": {
                    "content": {"text": "Missing module_id question"},
                },
            },
        ]
    }

    response = await async_client.post(
        "/api/v1/content/bulk-import",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["created"] == 1
    assert data["failed"] == 1
    assert len(data["errors"]) == 1
    assert data["errors"][0]["row"] == 2
    assert "module_id" in data["errors"][0]["reason"]


@pytest.mark.asyncio
async def test_bulk_import_modules_and_atoms(
    async_client: AsyncClient, auth_headers: dict
) -> None:
    """Test bulk import of modules and knowledge atoms."""
    payload = {
        "items": [
            {
                "entity_type": "module",
                "data": {
                    "title": "Bulk Module",
                    "description": "Bulk description",
                    "subject": "MATH",
                    "grade_level": "Y2",
                    "domain": "Algebra",
                    "competency_id": "MATH-2-ALG-01",
                },
            },
            {
                "entity_type": "atom",
                "data": {
                    "competency_id": "MATH-2-ALG-01",
                    "remediation_type": "AUDIO_VISUAL",
                    "content": {
                        "title": "Addition Atom",
                        "description": "Learn basic addition",
                    },
                },
            },
        ]
    }

    response = await async_client.post(
        "/api/v1/content/bulk-import",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["created"] == 2
    assert data["failed"] == 0
    assert data["errors"] == []
