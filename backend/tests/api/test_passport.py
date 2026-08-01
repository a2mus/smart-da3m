"""
Integration tests for Passport evaluation endpoint (T031).
Tests the complete Passport assessment flow.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.core.tenant import reset_active_organization_id, set_active_organization_id
from app.models.content import KnowledgeAtom, Module, Question
from app.models.diagnostic import CompetencyProfile, DiagnosticSession, MasteryLevel
from app.models.organization import Organization, OrganizationMember, OrganizationType
from app.models.user import User, UserRole


@pytest.fixture
async def test_org(db: AsyncSession) -> Organization:
    """Create a test organization."""
    org = Organization(
        name="Test School",
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
async def auth_headers_student(student_user: User, test_org: Organization) -> dict:
    """Generate auth headers for the student user."""
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
async def test_module(db: AsyncSession, test_org: Organization) -> Module:
    """Create a test module."""
    token = set_active_organization_id(test_org.id)
    try:
        module = Module(
            organization_id=test_org.id,
            subject="Mathematics",
            grade_level="السنة 4",
            domain="Numbers & Operations",
            competency_id="MATH-4-NUM-01",
        )
        db.add(module)
        await db.commit()
        await db.refresh(module)
        return module
    finally:
        reset_active_organization_id(token)


@pytest.fixture
async def passport_questions(db: AsyncSession, test_module: Module, test_org: Organization) -> list:
    """Create Passport assessment questions."""
    token = set_active_organization_id(test_org.id)
    try:
        questions = []
        for i in range(5):
            q = Question(
                organization_id=test_org.id,
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
    finally:
        reset_active_organization_id(token)


@pytest.fixture
async def knowledge_atoms(db: AsyncSession, test_org: Organization) -> list:
    """Create knowledge atoms for remediation."""
    from app.models.content import RemediationType

    token = set_active_organization_id(test_org.id)
    try:
        atoms = []
        for i, atom_type in enumerate([RemediationType.AUDIO_VISUAL, RemediationType.SIMULATION]):
            atom = KnowledgeAtom(
                organization_id=test_org.id,
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
    finally:
        reset_active_organization_id(token)


class TestRemediationPathway:
    """Test suite for remediation pathway endpoints."""

    async def test_get_pathway(
        self,
        async_client: AsyncClient,
        auth_headers_student: dict,
        student_user: User,
        test_org: Organization,
        knowledge_atoms: list,
        db: AsyncSession,
    ) -> None:
        """Test getting a remediation pathway for a competency."""
        token = set_active_organization_id(test_org.id)
        try:
            profile = CompetencyProfile(
                student_id=student_user.id,
                competency_id="MATH-4-NUM-01",
                organization_id=test_org.id,
                mastery_level=MasteryLevel.FAMILIAR,
                p_learned=0.45,
            )
            db.add(profile)
            await db.commit()
        finally:
            reset_active_organization_id(token)

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
        test_org: Organization,
        test_module: Module,
        passport_questions: list,
        db: AsyncSession,
    ) -> None:
        """Test passing Passport assessment."""
        token = set_active_organization_id(test_org.id)
        try:
            profile = CompetencyProfile(
                student_id=student_user.id,
                competency_id="MATH-4-NUM-01",
                organization_id=test_org.id,
                mastery_level=MasteryLevel.FAMILIAR,
                p_learned=0.55,
            )
            db.add(profile)
            await db.commit()
        finally:
            reset_active_organization_id(token)

        answers = [
            {"question_id": str(q.id), "answer": "A", "time_ms": 5000}
            for q in passport_questions
        ]
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
        assert data["new_mastery_level"] == "MASTERED"

    async def test_evaluate_passport_fail(
        self,
        async_client: AsyncClient,
        auth_headers_student: dict,
        student_user: User,
        test_org: Organization,
        test_module: Module,
        passport_questions: list,
        db: AsyncSession,
    ) -> None:
        """Test failing Passport assessment triggers alert."""
        token = set_active_organization_id(test_org.id)
        try:
            profile = CompetencyProfile(
                student_id=student_user.id,
                competency_id="MATH-4-NUM-01",
                organization_id=test_org.id,
                mastery_level=MasteryLevel.FAMILIAR,
                p_learned=0.55,
            )
            db.add(profile)
            await db.commit()
        finally:
            reset_active_organization_id(token)

        answers = [
            {"question_id": str(q.id), "answer": "B", "time_ms": 8000}
            for q in passport_questions
        ]
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
        assert data["alert_triggered"] is True

    async def test_mastery_regression_on_fail(
        self,
        async_client: AsyncClient,
        auth_headers_student: dict,
        student_user: User,
        test_org: Organization,
        test_module: Module,
        passport_questions: list,
        db: AsyncSession,
    ) -> None:
        """Test mastery regression when failing Passport from high level."""
        token = set_active_organization_id(test_org.id)
        try:
            profile = CompetencyProfile(
                student_id=student_user.id,
                competency_id="MATH-4-NUM-01",
                organization_id=test_org.id,
                mastery_level=MasteryLevel.PROFICIENT,
                p_learned=0.85,
            )
            db.add(profile)
            await db.commit()
        finally:
            reset_active_organization_id(token)

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
        test_org: Organization,
        knowledge_atoms: list,
        db: AsyncSession,
    ) -> None:
        """Test marking a knowledge atom as complete."""
        from app.models.remediation import RemediationPath

        token = set_active_organization_id(test_org.id)
        try:
            path = RemediationPath(
                student_id=student_user.id,
                competency_id="MATH-4-NUM-01",
                organization_id=test_org.id,
                status="IN_PROGRESS",
                atoms_completed=[],
            )
            db.add(path)
            await db.commit()
        finally:
            reset_active_organization_id(token)

        atom_id = str(knowledge_atoms[0].id)

        response = await async_client.post(
            f"/api/v1/remediation/atoms/{atom_id}/complete",
            json={
                "time_spent_ms": 15000,
                "interactions_count": 1,
                "is_correct": True,
            },
            headers=auth_headers_student,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["progress_percent"] > 0

    async def test_get_remediation_status(
        self,
        async_client: AsyncClient,
        auth_headers_student: dict,
        student_user: User,
        test_org: Organization,
        knowledge_atoms: list,
        db: AsyncSession,
    ) -> None:
        """Test getting current remediation status."""
        from app.models.remediation import RemediationPath

        token = set_active_organization_id(test_org.id)
        try:
            path = RemediationPath(
                student_id=student_user.id,
                competency_id="MATH-4-NUM-01",
                organization_id=test_org.id,
                status="IN_PROGRESS",
                atoms_completed=[str(knowledge_atoms[0].id)],
            )
            db.add(path)
            await db.commit()
        finally:
            reset_active_organization_id(token)

        response = await async_client.get(
            "/api/v1/remediation/status/MATH-4-NUM-01",
            headers=auth_headers_student,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["competency_id"] == "MATH-4-NUM-01"
        assert data["status"] == "IN_PROGRESS"
        assert len(data["atoms_completed"]) == 1
