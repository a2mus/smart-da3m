"""
Integration tests for content API endpoints (T014).
Tests for Module and Question CRUD operations.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Module, ModuleStatus, Question
from app.models.user import User, UserRole


@pytest.fixture
async def expert_user(db: AsyncSession) -> User:
    """Create an expert user for testing."""
    user = User(
        email="expert@test.com",
        hashed_password="hashed_password",
        role=UserRole.EXPERT,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def auth_headers(expert_user: User) -> dict:
    """Generate auth headers for the expert user."""
    # Note: In real tests, this would use proper JWT generation
    # For now, we'll use a mock token structure
    return {
        "Authorization": f"Bearer test-token-{expert_user.id}",
        "Content-Type": "application/json",
    }


class TestModuleEndpoints:
    """Test suite for Module API endpoints."""

    async def test_create_module(
        self, async_client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test creating a new curriculum module."""
        module_data = {
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
        self, async_client: AsyncClient, auth_headers: dict, db: AsyncSession
    ) -> None:
        """Test listing all modules."""
        # Create test modules
        modules = [
            Module(
                subject="Mathematics",
                grade_level="السنة 4",
                domain="Numbers & Operations",
                competency_id="MATH-4-NUM-01",
                status=ModuleStatus.PUBLISHED,
            ),
            Module(
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
        assert isinstance(data, list)
        assert len(data) >= 2

    async def test_get_module_by_id(
        self, async_client: AsyncClient, auth_headers: dict, db: AsyncSession
    ) -> None:
        """Test getting a specific module by ID."""
        # Create a test module
        module = Module(
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
        self, async_client: AsyncClient, auth_headers: dict, db: AsyncSession
    ) -> None:
        """Test updating a module."""
        # Create a test module
        module = Module(
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
        self, async_client: AsyncClient, auth_headers: dict, db: AsyncSession
    ) -> None:
        """Test deleting a module."""
        # Create a test module
        module = Module(
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
        self, async_client: AsyncClient, auth_headers: dict, db: AsyncSession
    ) -> None:
        """Test creating a new question."""
        # First create a module
        module = Module(
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
        self, async_client: AsyncClient, auth_headers: dict, db: AsyncSession
    ) -> None:
        """Test listing questions filtered by module."""
        # Create module and questions
        module = Module(
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
                module_id=module.id,
                content={"text": f"Question {i}"},
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
        assert isinstance(data, list)
        assert len(data) == 3

    async def test_bulk_import_questions(
        self, async_client: AsyncClient, auth_headers: dict, db: AsyncSession
    ) -> None:
        """Test bulk importing questions via JSON."""
        # Create a module first
        module = Module(
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
                    "content": {"text": "Question 1"},
                    "difficulty_level": 2,
                    "estimated_time_sec": 45,
                },
                {
                    "content": {"text": "Question 2"},
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
        self, async_client: AsyncClient, auth_headers: dict, db: AsyncSession
    ) -> None:
        """Test listing knowledge atoms filtered by competency."""
        from app.models.content import KnowledgeAtom, RemediationType

        # Create knowledge atoms
        atoms = [
            KnowledgeAtom(
                competency_id="MATH-4-NUM-01",
                remediation_type=RemediationType.AUDIO_VISUAL,
                content={"title": f"Atom {i}"},
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
        assert isinstance(data, list)
        assert len(data) == 3
