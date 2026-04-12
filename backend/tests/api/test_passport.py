"""
Integration tests for Passport evaluation endpoint (T031).
Tests the complete Passport assessment flow.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import KnowledgeAtom, Module, Question
from app.models.diagnostic import CompetencyProfile, DiagnosticSession, MasteryLevel
from app.models.user import User, UserRole


@pytest.fixture
async def student_user(db: AsyncSession) -> User:
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
    return user


@pytest.fixture
async def auth_headers_student(student_user: User) -> dict:
    """Generate auth headers for the student user."""
    return {
        "Authorization": f"Bearer test-token-{student_user.id}",
        "Content-Type": "application/json",
    }


@pytest.fixture
async def test_module(db: AsyncSession) -> Module:
    """Create a test module."""
    module = Module(
        subject="Mathematics",
        grade_level="السنة 4",
        domain="Numbers & Operations",
        competency_id="MATH-4-NUM-01",
    )
    db.add(module)
    await db.commit()
    await db.refresh(module)
    return module


@pytest.fixture
async def passport_questions(db: AsyncSession, test_module: Module) -> list:
    """Create Passport assessment questions."""
    questions = []
    for i in range(5):
        q = Question(
            module_id=test_module.id,
            content={
                "text": f"Passport question {i+1}?",
                "type": "multiple_choice",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
            },
            difficulty_level=5,
            estimated_time_sec=60,
        )
        db.add(q)
        questions.append(q)
    await db.commit()
    return questions


@pytest.fixture
async def knowledge_atoms(db: AsyncSession) -> list:
    """Create knowledge atoms for remediation."""
    from app.models.content import RemediationType

    atoms = []
    for i, atom_type in enumerate([RemediationType.AUDIO_VISUAL, RemediationType.SIMULATION]):
        atom = KnowledgeAtom(
            competency_id="MATH-4-NUM-01",
            remediation_type=atom_type,
            content={
                "title": f"Learning Atom {i+1}",
                "description": f"Description for atom {i+1}",
            },
        )
        db.add(atom)
        atoms.append(atom)
    await db.commit()
    return atoms


class TestRemediationPathway:
    """Test suite for remediation pathway endpoints."""

    async def test_get_pathway(
        self,
        async_client: AsyncClient,
        auth_headers_student: dict,
        student_user: User,
        knowledge_atoms: list,
        db: AsyncSession,
    ) -> None:
        """Test getting a remediation pathway for a competency."""
        # Create competency profile placing student in Group B
        profile = CompetencyProfile(
            student_id=student_user.id,
            competency_id="MATH-4-NUM-01",
            mastery_level=MasteryLevel.FAMILIAR,
            p_learned=0.45,
        )
        db.add(profile)
        await db.commit()

        response = await async_client.get(
            "/api/v1/remediation/pathway/MATH-4-NUM-01",
            headers=auth_headers_student,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["competency_id"] == "MATH-4-NUM-01"
        assert "atoms" in data
        assert len(data["atoms"]) > 0

    async def test_get_pathway_unauthorized(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test that getting pathway requires authentication."""
        response = await async_client.get("/api/v1/remediation/pathway/MATH-4-NUM-01")
        assert response.status_code == 401


class TestPassportEvaluation:
    """Test suite for Passport assessment endpoints."""

    async def test_evaluate_passport_pass(
        self,
        async_client: AsyncClient,
        auth_headers_student: dict,
        student_user: User,
        test_module: Module,
        passport_questions: list,
        db: AsyncSession,
    ) -> None:
        """Test passing Passport assessment."""
        # Create initial competency profile
        profile = CompetencyProfile(
            student_id=student_user.id,
            competency_id="MATH-4-NUM-01",
            mastery_level=MasteryLevel.FAMILIAR,
            p_learned=0.55,
        )
        db.add(profile)
        await db.commit()

        # Submit Passport answers (4/5 correct = 80%)
        answers = [
            {"question_id": str(q.id), "answer": "A", "time_ms": 5000}
            for q in passport_questions
        ]
        # Make one answer incorrect
        answers[2]["answer"] = "B"

        response = await async_client.post(
            "/api/v1/remediation/passport/evaluate",
            json={
                "competency_id": "MATH-4-NUM-01",
                "answers": answers,
            },
            headers=auth_headers_student,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["passed"] is True
        assert data["accuracy"] == 0.8
        assert data["new_mastery_level"] == "PROFICIENT"

    async def test_evaluate_passport_fail(
        self,
        async_client: AsyncClient,
        auth_headers_student: dict,
        student_user: User,
        test_module: Module,
        passport_questions: list,
        db: AsyncSession,
    ) -> None:
        """Test failing Passport assessment triggers alert."""
        # Create initial competency profile
        profile = CompetencyProfile(
            student_id=student_user.id,
            competency_id="MATH-4-NUM-01",
            mastery_level=MasteryLevel.FAMILIAR,
            p_learned=0.55,
        )
        db.add(profile)
        await db.commit()

        # Submit Passport answers (2/5 correct = 40% - failing)
        answers = [
            {"question_id": str(q.id), "answer": "B", "time_ms": 8000}
            for q in passport_questions
        ]
        # Make only 2 correct
        answers[0]["answer"] = "A"
        answers[1]["answer"] = "A"

        response = await async_client.post(
            "/api/v1/remediation/passport/evaluate",
            json={
                "competency_id": "MATH-4-NUM-01",
                "answers": answers,
            },
            headers=auth_headers_student,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["passed"] is False
        assert data["accuracy"] == 0.4
        assert data["new_mastery_level"] == "ATTEMPTED"  # Regression
        assert data["alert_triggered"] is True

    async def test_mastery_regression_on_fail(
        self,
        async_client: AsyncClient,
        auth_headers_student: dict,
        student_user: User,
        test_module: Module,
        passport_questions: list,
        db: AsyncSession,
    ) -> None:
        """Test mastery regression when failing Passport from high level."""
        # Create initial competency profile at high mastery
        profile = CompetencyProfile(
            student_id=student_user.id,
            competency_id="MATH-4-NUM-01",
            mastery_level=MasteryLevel.PROFICIENT,
            p_learned=0.85,
        )
        db.add(profile)
        await db.commit()

        # Submit failing answers
        answers = [
            {"question_id": str(q.id), "answer": "B", "time_ms": 10000}
            for q in passport_questions
        ]

        response = await async_client.post(
            "/api/v1/remediation/passport/evaluate",
            json={
                "competency_id": "MATH-4-NUM-01",
                "answers": answers,
            },
            headers=auth_headers_student,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["passed"] is False
        # Should regress from PROFICIENT
        assert data["new_mastery_level"] in ["FAMILIAR", "ATTEMPTED"]

    async def test_passport_evaluation_unauthorized(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test that Passport evaluation requires authentication."""
        response = await async_client.post(
            "/api/v1/remediation/passport/evaluate",
            json={
                "competency_id": "MATH-4-NUM-01",
                "answers": [],
            },
        )
        assert response.status_code == 401


class TestRemediationProgress:
    """Test suite for tracking remediation progress."""

    async def test_complete_knowledge_atom(
        self,
        async_client: AsyncClient,
        auth_headers_student: dict,
        student_user: User,
        knowledge_atoms: list,
        db: AsyncSession,
    ) -> None:
        """Test marking a knowledge atom as complete."""
        from app.models.remediation import RemediationPath

        # Create remediation path
        path = RemediationPath(
            student_id=student_user.id,
            competency_id="MATH-4-NUM-01",
            status="IN_PROGRESS",
            atoms_completed=[],
        )
        db.add(path)
        await db.commit()

        atom_id = str(knowledge_atoms[0].id)

        response = await async_client.post(
            f"/api/v1/remediation/atoms/{atom_id}/complete",
            headers=auth_headers_student,
        )

        assert response.status_code == 200
        data = response.json()
        assert atom_id in data["atoms_completed"]
        assert data["progress_percent"] > 0

    async def test_get_remediation_status(
        self,
        async_client: AsyncClient,
        auth_headers_student: dict,
        student_user: User,
        knowledge_atoms: list,
        db: AsyncSession,
    ) -> None:
        """Test getting current remediation status."""
        from app.models.remediation import RemediationPath

        # Create remediation path with some completed atoms
        path = RemediationPath(
            student_id=student_user.id,
            competency_id="MATH-4-NUM-01",
            status="IN_PROGRESS",
            atoms_completed=[knowledge_atoms[0].id],
        )
        db.add(path)
        await db.commit()

        response = await async_client.get(
            "/api/v1/remediation/status/MATH-4-NUM-01",
            headers=auth_headers_student,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["competency_id"] == "MATH-4-NUM-01"
        assert data["status"] == "IN_PROGRESS"
        assert len(data["atoms_completed"]) == 1
