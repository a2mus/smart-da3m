"""
Integration tests for content API endpoints (T014).
Tests for Module and Question CRUD operations.
"""

from uuid import uuid4
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_expert_user
from app.core.tenant import reset_active_organization_id, set_active_organization_id
from app.main import app
from app.models.content import KnowledgeAtom, Module, ModuleStatus, Question, RemediationType
from app.models.organization import Organization, OrganizationMember, OrganizationType
from app.models.user import User, UserRole


@pytest.fixture
async def test_org(db: AsyncSession) -> Organization:
    """Create a test organization."""
    org = Organization(
        name="Content Test School",
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
        email=f"expert-{uuid4()}@test.com",
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
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def auth_headers(expert_user: User, test_org: Organization) -> dict:
    """Generate auth headers and override dependency for the expert user."""
    def get_expert_override():
        set_active_organization_id(test_org.id)
        return expert_user

    app.dependency_overrides[get_current_expert_user] = get_expert_override
    return {
        "Authorization": f"Bearer test-token-{expert_user.id}",
        "X-Organization-Id": str(test_org.id),
        "Content-Type": "application/json",
    }


class TestModuleEndpoints:
    """Test suite for Module API endpoints."""

    async def test_create_module(
        self, async_client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test creating a new curriculum module."""
        module_data = {
            "title": "Module 1",
            "description": "Intro module",
            "subject": "Mathematics",
            "grade_level": "السنة 4",
            "domain": "Numbers & Operations",
            "competency_id": "MATH-4-NUM-01",
        }

        response = await async_client.post(
            "/api/v1/content/modules",
            json=module_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["subject"] == module_data["subject"]
        assert data["grade_level"] == module_data["grade_level"]
        assert data["domain"] == module_data["domain"]
        assert data["competency_id"] == module_data["competency_id"]
        assert data["status"] == "DRAFT"
        assert "id" in data
        assert "created_at" in data

    async def test_create_module_unauthorized(
        self, async_client: AsyncClient
    ) -> None:
        """Test that creating a module requires authentication."""
        app.dependency_overrides.clear()
        module_data = {
            "subject": "Mathematics",
            "grade_level": "السنة 4",
            "domain": "Numbers & Operations",
            "competency_id": "MATH-4-NUM-01",
        }

        response = await async_client.post(
            "/api/v1/content/modules",
            json=module_data,
        )

        assert response.status_code == 401

    async def test_list_modules(
        self, async_client: AsyncClient, auth_headers: dict, db: AsyncSession, test_org: Organization
    ) -> None:
        """Test listing all modules."""
        # Create test modules
        modules = [
            Module(
                organization_id=test_org.id,
                subject="Mathematics",
                grade_level="السنة 4",
                domain="Numbers & Operations",
                competency_id="MATH-4-NUM-01",
                status=ModuleStatus.PUBLISHED,
            ),
            Module(
                organization_id=test_org.id,
                subject="Mathematics",
                grade_level="السنة 4",
                domain="Geometry",
                competency_id="MATH-4-GEO-01",
                status=ModuleStatus.DRAFT,
            ),
        ]
        for module in modules:
            db.add(module)
        await db.commit()

        response = await async_client.get(
            "/api/v1/content/modules",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 2

    async def test_get_module_by_id(
        self, async_client: AsyncClient, auth_headers: dict, db: AsyncSession, test_org: Organization
    ) -> None:
        """Test getting a specific module by ID."""
        # Create a test module
        module = Module(
            organization_id=test_org.id,
            subject="Mathematics",
            grade_level="السنة 4",
            domain="Numbers & Operations",
            competency_id="MATH-4-NUM-01",
            status=ModuleStatus.PUBLISHED,
        )
        db.add(module)
        await db.commit()
        await db.refresh(module)

        response = await async_client.get(
            f"/api/v1/content/modules/{module.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(module.id)
        assert data["subject"] == module.subject
        assert data["competency_id"] == module.competency_id

    async def test_update_module(
        self, async_client: AsyncClient, auth_headers: dict, db: AsyncSession, test_org: Organization
    ) -> None:
        """Test updating a module."""
        # Create a test module
        module = Module(
            organization_id=test_org.id,
            subject="Mathematics",
            grade_level="السنة 4",
            domain="Numbers & Operations",
            competency_id="MATH-4-NUM-01",
            status=ModuleStatus.DRAFT,
        )
        db.add(module)
        await db.commit()
        await db.refresh(module)

        update_data = {
            "domain": "Advanced Numbers & Operations",
            "status": "PUBLISHED",
        }

        response = await async_client.patch(
            f"/api/v1/content/modules/{module.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["domain"] == update_data["domain"]
        assert data["status"] == update_data["status"]
        assert data["subject"] == module.subject  # Unchanged

    async def test_delete_module(
        self, async_client: AsyncClient, auth_headers: dict, db: AsyncSession, test_org: Organization
    ) -> None:
        """Test deleting a module."""
        # Create a test module
        module = Module(
            organization_id=test_org.id,
            subject="Mathematics",
            grade_level="السنة 4",
            domain="Numbers & Operations",
            competency_id="MATH-4-NUM-01",
            status=ModuleStatus.DRAFT,
        )
        db.add(module)
        await db.commit()
        await db.refresh(module)

        response = await async_client.delete(
            f"/api/v1/content/modules/{module.id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify module is deleted
        get_response = await async_client.get(
            f"/api/v1/content/modules/{module.id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404


class TestQuestionEndpoints:
    """Test suite for Question API endpoints."""

    async def test_create_question(
        self, async_client: AsyncClient, auth_headers: dict, db: AsyncSession, test_org: Organization
    ) -> None:
        """Test creating a new question."""
        # First create a module
        module = Module(
            organization_id=test_org.id,
            subject="Mathematics",
            grade_level="السنة 4",
            domain="Numbers & Operations",
            competency_id="MATH-4-NUM-01",
            status=ModuleStatus.PUBLISHED,
        )
        db.add(module)
        await db.commit()
        await db.refresh(module)

        question_data = {
            "module_id": str(module.id),
            "content": {
                "text": "What is 1/4 + 1/4?",
                "type": "multiple_choice",
                "options": ["1/8", "1/4", "1/2", "2/4"],
                "correct_answer": "1/2",
            },
            "difficulty_level": 3,
            "target_misconception_id": "MATH-FRAC-ADD-01",
            "estimated_time_sec": 60,
        }

        response = await async_client.post(
            "/api/v1/content/questions",
            json=question_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["module_id"] == question_data["module_id"]
        assert data["difficulty_level"] == question_data["difficulty_level"]
        assert data["target_misconception_id"] == question_data["target_misconception_id"]
        assert "id" in data

    async def test_list_questions_by_module(
        self, async_client: AsyncClient, auth_headers: dict, db: AsyncSession, test_org: Organization
    ) -> None:
        """Test listing questions filtered by module."""
        # Create module and questions
        module = Module(
            organization_id=test_org.id,
            subject="Mathematics",
            grade_level="السنة 4",
            domain="Numbers & Operations",
            competency_id="MATH-4-NUM-01",
            status=ModuleStatus.PUBLISHED,
        )
        db.add(module)
        await db.flush()

        questions = [
            Question(
                organization_id=test_org.id,
                module_id=module.id,
                content={"text": f"Question {i}", "correct_answer": "Option A"},
                difficulty_level=i,
                estimated_time_sec=60,
            )
            for i in range(1, 4)
        ]
        for q in questions:
            db.add(q)
        await db.commit()

        response = await async_client.get(
            f"/api/v1/content/questions?module_id={module.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 3

    async def test_bulk_import_questions(
        self, async_client: AsyncClient, auth_headers: dict, db: AsyncSession, test_org: Organization
    ) -> None:
        """Test bulk importing questions via JSON."""
        # Create a module first
        module = Module(
            organization_id=test_org.id,
            subject="Mathematics",
            grade_level="السنة 4",
            domain="Numbers & Operations",
            competency_id="MATH-4-NUM-01",
            status=ModuleStatus.PUBLISHED,
        )
        db.add(module)
        await db.commit()
        await db.refresh(module)

        questions_data = {
            "module_id": str(module.id),
            "questions": [
                {
                    "module_id": str(module.id),
                    "content": {"text": "Question 1", "correct_answer": "Option A"},
                    "difficulty_level": 2,
                    "estimated_time_sec": 45,
                },
                {
                    "module_id": str(module.id),
                    "content": {"text": "Question 2", "correct_answer": "Option B"},
                    "difficulty_level": 3,
                    "target_misconception_id": "MATH-TEST-01",
                    "estimated_time_sec": 60,
                },
            ],
        }

        response = await async_client.post(
            "/api/v1/content/questions/bulk",
            json=questions_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["imported_count"] == 2
        assert "imported_ids" in data
        assert len(data["imported_ids"]) == 2


    async def test_create_question_missing_correct_answer_fails(
        self, async_client: AsyncClient, auth_headers: dict, db: AsyncSession, test_org: Organization
    ) -> None:
        """Test creating a question without correct_answer fails validation."""
        module = Module(
            organization_id=test_org.id,
            subject="Mathematics",
            grade_level="السنة 4",
            domain="Numbers & Operations",
            competency_id="MATH-4-NUM-01",
            status=ModuleStatus.PUBLISHED,
        )
        db.add(module)
        await db.commit()

        question_data = {
            "module_id": str(module.id),
            "content": {
                "text": "Invalid Question with no answer",
                "type": "multiple_choice",
                "options": ["Option A", "Option B"],
            },
            "difficulty_level": 3,
            "estimated_time_sec": 60,
        }

        response = await async_client.post(
            "/api/v1/content/questions",
            json=question_data,
            headers=auth_headers,
        )

        assert response.status_code in (422, 400)


class TestKnowledgeAtomEndpoints:
    """Test suite for KnowledgeAtom API endpoints."""

    async def test_create_knowledge_atom(
        self, async_client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test creating a knowledge atom."""
        atom_data = {
            "competency_id": "MATH-4-NUM-01",
            "remediation_type": "AUDIO_VISUAL",
            "content": {
                "title": "Understanding Fraction Addition",
                "description": "Learn to add fractions with common denominators",
                "media_url": "/media/fractions_addition.mp4",
            },
        }

        response = await async_client.post(
            "/api/v1/content/knowledge-atoms",
            json=atom_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["competency_id"] == atom_data["competency_id"]
        assert data["remediation_type"] == atom_data["remediation_type"]
        assert "id" in data

    async def test_list_knowledge_atoms_by_competency(
        self, async_client: AsyncClient, auth_headers: dict, db: AsyncSession, test_org: Organization
    ) -> None:
        """Test listing knowledge atoms filtered by competency."""

        # Create knowledge atoms
        atoms = [
            KnowledgeAtom(
                organization_id=test_org.id,
                competency_id="MATH-4-NUM-01",
                remediation_type=RemediationType.AUDIO_VISUAL,
                content={"title": f"Atom {i}", "description": "desc"},
            )
            for i in range(3)
        ]
        for atom in atoms:
            db.add(atom)
        await db.commit()

        response = await async_client.get(
            "/api/v1/content/knowledge-atoms?competency_id=MATH-4-NUM-01",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 3

    async def test_get_knowledge_atom(
        self, async_client: AsyncClient, auth_headers: dict, db: AsyncSession, test_org: Organization
    ) -> None:
        """Test getting a knowledge atom by ID."""
        atom = KnowledgeAtom(
            organization_id=test_org.id,
            competency_id="MATH-4-NUM-01",
            remediation_type=RemediationType.SIMULATION,
            content={"title": "Interactive Fraction Bar", "description": "Drag to fill"},
        )
        db.add(atom)
        await db.commit()
        await db.refresh(atom)

        response = await async_client.get(
            f"/api/v1/content/knowledge-atoms/{atom.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(atom.id)

    async def test_update_knowledge_atom(
        self, async_client: AsyncClient, auth_headers: dict, db: AsyncSession, test_org: Organization
    ) -> None:
        """Test updating a knowledge atom."""
        atom = KnowledgeAtom(
            organization_id=test_org.id,
            competency_id="MATH-4-NUM-01",
            remediation_type=RemediationType.MIND_MAP,
            content={"title": "Initial Mindmap", "description": "initial"},
        )
        db.add(atom)
        await db.commit()
        await db.refresh(atom)

        update_data = {
            "content": {"title": "Updated Mindmap", "description": "updated"},
        }

        response = await async_client.patch(
            f"/api/v1/content/knowledge-atoms/{atom.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"]["title"] == "Updated Mindmap"

    async def test_delete_knowledge_atom(
        self, async_client: AsyncClient, auth_headers: dict, db: AsyncSession, test_org: Organization
    ) -> None:
        """Test deleting a knowledge atom."""
        atom = KnowledgeAtom(
            organization_id=test_org.id,
            competency_id="MATH-4-NUM-01",
            remediation_type=RemediationType.AUDIO_VISUAL,
            content={"title": "To delete", "description": "delete me"},
        )
        db.add(atom)
        await db.commit()
        await db.refresh(atom)

        response = await async_client.delete(
            f"/api/v1/content/knowledge-atoms/{atom.id}",
            headers=auth_headers,
        )

        assert response.status_code == 204
