"""
Unit and integration tests for database repository layer.
"""

import pytest
import uuid
from uuid import UUID

from app.core.tenant import set_active_organization_id, reset_active_organization_id
from app.models.content import ModuleStatus, RemediationType
from app.models.diagnostic import DiagnosticSessionStatus, ErrorClassification, MasteryLevel, RemediationGroup
from app.models.organization import OrganizationType
from app.models.remediation import RemediationPathStatus
from app.models.user import UserRole
from app.repositories.content_repo import ContentRepository
from app.repositories.diagnostic_repo import DiagnosticRepository
from app.repositories.remediation_repo import RemediationRepository
from app.repositories.user_repo import UserRepository


@pytest.mark.asyncio
async def test_user_repository_crud(db):
    """Test UserRepository user and organization CRUD methods."""
    token = set_active_organization_id(UUID("00000000-0000-0000-0000-000000000001"))
    try:
        repo = UserRepository(db)
        org = await repo.create_organization(
            name="Test Org Repository", org_type=OrganizationType.SCHOOL
        )
        assert org.id is not None
        assert org.name == "Test Org Repository"

        set_active_organization_id(org.id)

        user = await repo.create_user(
            role=UserRole.STUDENT,
            email="repo_student@example.com",
            hashed_password="secret_hash",
        )
        assert user.id is not None
        assert user.email == "repo_student@example.com"

        fetched_user = await repo.get_user_by_email("repo_student@example.com")
        assert fetched_user is not None
        assert fetched_user.id == user.id

        member = await repo.add_organization_member(
            user_id=user.id, organization_id=org.id, role=UserRole.STUDENT
        )
        assert member.id is not None
        assert member.organization_id == org.id

        memberships = await repo.get_user_memberships(user.id)
        assert len(memberships) == 1
        assert memberships[0].organization_id == org.id
    finally:
        reset_active_organization_id(token)


@pytest.mark.asyncio
async def test_diagnostic_repository(db):
    """Test DiagnosticRepository session, answer, and profile methods."""
    token = set_active_organization_id(UUID("00000000-0000-0000-0000-000000000001"))
    try:
        user_repo = UserRepository(db)
        org = await user_repo.create_organization(name="Diag Org", org_type=OrganizationType.SCHOOL)
        set_active_organization_id(org.id)

        student = await user_repo.create_user(role=UserRole.STUDENT, email="diag_student@example.com")

        content_repo = ContentRepository(db)
        module, _ = await content_repo.list_modules()
        if not module:
            module_obj = await content_repo.create(
                subject="Mathematics",
                grade_level="G4",
                domain="NUMBERS",
                competency_id="COMP_NUM_01",
                organization_id=org.id,
                status=ModuleStatus.PUBLISHED,
            )
            module_id = module_obj.id
        else:
            module_id = module[0].id

        diag_repo = DiagnosticRepository(db)
        session = await diag_repo.create_session(
            student_id=student.id, module_id=module_id, organization_id=org.id
        )
        assert session.id is not None
        assert session.status == DiagnosticSessionStatus.IN_PROGRESS

        updated_session = await diag_repo.update_session_status(
            session.id, DiagnosticSessionStatus.COMPLETED, RemediationGroup.A
        )
        assert updated_session is not None
        assert updated_session.status == DiagnosticSessionStatus.COMPLETED
        assert updated_session.recommended_group == RemediationGroup.A

        # Test answer recording
        q = await content_repo.create_question(
            module_id=module_id,
            organization_id=org.id,
            content={"question_text": "What is 2+2?"},
            difficulty_level=3,
        )

        answer = await diag_repo.record_answer(
            session_id=session.id,
            question_id=q.id,
            organization_id=org.id,
            is_correct=1,
            response_time_ms=2500,
            error_classification=ErrorClassification.NONE,
        )
        assert answer.id is not None
        assert answer.is_correct == 1

        answers = await diag_repo.get_session_answers(session.id)
        assert len(answers) == 1

        # Test competency profile
        profile = await diag_repo.update_or_create_competency_profile(
            student_id=student.id,
            competency_id="COMP_NUM_01",
            organization_id=org.id,
            p_learned=0.85,
            mastery_level=MasteryLevel.PROFICIENT,
        )
        assert profile.p_learned == 0.85
        assert profile.mastery_level == MasteryLevel.PROFICIENT
    finally:
        reset_active_organization_id(token)


@pytest.mark.asyncio
async def test_remediation_repository(db):
    """Test RemediationRepository path, completion, and passport methods."""
    token = set_active_organization_id(UUID("00000000-0000-0000-0000-000000000001"))
    try:
        user_repo = UserRepository(db)
        org = await user_repo.create_organization(name="Remediation Org", org_type=OrganizationType.SCHOOL)
        set_active_organization_id(org.id)

        student = await user_repo.create_user(role=UserRole.STUDENT, email="rem_student@example.com")

        remed_repo = RemediationRepository(db)
        path = await remed_repo.create_path(
            student_id=student.id, competency_id="COMP_NUM_01", organization_id=org.id
        )
        assert path.id is not None
        assert path.status == RemediationPathStatus.IN_PROGRESS

        active_path = await remed_repo.get_active_student_path(student.id, "COMP_NUM_01")
        assert active_path is not None
        assert active_path.id == path.id

        # Test passport assessment
        assessment = await remed_repo.create_passport_assessment(
            student_id=student.id, competency_id="COMP_NUM_01", organization_id=org.id
        )
        assert assessment.id is not None

        updated_assess = await remed_repo.record_passport_result(
            assessment.id, passed=1, accuracy=90, questions_answered=10, correct_answers=9
        )
        assert updated_assess is not None
        assert updated_assess.passed == 1
        assert updated_assess.accuracy == 90
    finally:
        reset_active_organization_id(token)
