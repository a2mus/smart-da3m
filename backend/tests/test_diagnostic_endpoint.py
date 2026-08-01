"""
Unit and integration tests for Diagnostic Endpoints wired to DiagnosticEngine and Repositories.
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from app.api.deps import get_current_student
from app.engines.bkt import MasteryLevel
from app.main import app
from app.models.diagnostic import DiagnosticSessionStatus, ErrorClassification
from app.models.user import User, UserRole


@pytest.fixture
def mock_student():
    student = User(
        id=uuid4(),
        email="student@test.com",
        role=UserRole.STUDENT,
    )
    student.organization_id = uuid4()
    app.dependency_overrides[get_current_student] = lambda: student
    yield student
    app.dependency_overrides.pop(get_current_student, None)


@pytest.mark.asyncio
async def test_diagnostic_start_endpoint(async_client: AsyncClient, db, mock_student):
    """Test starting a diagnostic session."""
    module_id = uuid4()
    session_id = uuid4()
    question_id = uuid4()

    mock_session = MagicMock()
    mock_session.id = session_id

    mock_question = MagicMock()
    mock_question.id = question_id
    mock_question.content = {"text": "What is 2+2?", "options": ["3", "4"]}
    mock_question.difficulty_level = 5
    mock_question.estimated_time_sec = 30

    with patch("app.api.endpoints.diagnostic.DiagnosticRepository") as MockDiagRepo, \
         patch("app.api.endpoints.diagnostic.ContentRepository") as MockContentRepo, \
         patch("app.api.endpoints.diagnostic.get_current_student", return_value=mock_student):

        diag_repo_inst = MockDiagRepo.return_value
        diag_repo_inst.create_session = AsyncMock(return_value=mock_session)

        content_repo_inst = MockContentRepo.return_value
        content_repo_inst.list_module_questions = AsyncMock(return_value=[mock_question])

        response = await async_client.post(
            "/api/v1/diagnostic/start",
            json={"module_id": str(module_id)},
            headers={"Authorization": f"Bearer test-token-{mock_student.id}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["session_id"] == str(session_id)
        assert data["question"]["id"] == str(question_id)


@pytest.mark.asyncio
async def test_diagnostic_answer_correct_bkt_update(async_client: AsyncClient, db, mock_student):
    """Test submitting a correct answer updates BKT mastery and saves profile to DB."""
    session_id = uuid4()
    module_id = uuid4()
    question_id = uuid4()

    mock_session = MagicMock()
    mock_session.id = session_id
    mock_session.student_id = mock_student.id
    mock_session.module_id = module_id
    mock_session.status = DiagnosticSessionStatus.IN_PROGRESS
    mock_session.organization_id = mock_student.organization_id

    mock_module = MagicMock()
    mock_module.competency_id = "MATH-C1"

    mock_question = MagicMock()
    mock_question.id = question_id
    mock_question.content = {"correct_answer": "4"}
    mock_question.difficulty_level = 5
    mock_question.target_misconception_id = None

    mock_answer_rec = MagicMock()
    mock_answer_rec.question_id = question_id
    mock_answer_rec.is_correct = 1

    with patch("app.api.endpoints.diagnostic.DiagnosticRepository") as MockDiagRepo, \
         patch("app.api.endpoints.diagnostic.ContentRepository") as MockContentRepo, \
         patch("app.api.endpoints.diagnostic.get_current_student", return_value=mock_student):

        diag_repo_inst = MockDiagRepo.return_value
        diag_repo_inst.get_session = AsyncMock(return_value=mock_session)
        diag_repo_inst.get_answer = AsyncMock(return_value=None)
        diag_repo_inst.get_competency_profile = AsyncMock(return_value=None)  # initial 0.5
        diag_repo_inst.update_or_create_competency_profile = AsyncMock()
        diag_repo_inst.record_answer = AsyncMock(return_value=mock_answer_rec)
        diag_repo_inst.get_session_answers = AsyncMock(return_value=[mock_answer_rec])
        diag_repo_inst.update_session_status = AsyncMock()

        content_repo_inst = MockContentRepo.return_value
        content_repo_inst.get_question = AsyncMock(return_value=mock_question)
        content_repo_inst.get_module = AsyncMock(return_value=mock_module)
        content_repo_inst.list_module_questions = AsyncMock(return_value=[mock_question])

        response = await async_client.post(
            "/api/v1/diagnostic/answer",
            json={
                "session_id": str(session_id),
                "question_id": str(question_id),
                "answer": "4",
                "time_ms": 10000,
            },
            headers={"Authorization": f"Bearer test-token-{mock_student.id}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_correct"] is True
        assert data["error_classification"] == "NONE"
        assert data["current_mastery"] > 0.5  # BKT increased mastery from 0.5
        diag_repo_inst.update_or_create_competency_profile.assert_called_once()


@pytest.mark.asyncio
async def test_diagnostic_results_endpoint(async_client: AsyncClient, db, mock_student):
    """Test getting diagnostic session results using engine evaluation."""
    session_id = uuid4()
    module_id = uuid4()

    mock_session = MagicMock()
    mock_session.id = session_id
    mock_session.student_id = mock_student.id
    mock_session.module_id = module_id
    mock_session.recommended_group = MagicMock(value="A")
    mock_session.completed_at = None

    mock_module = MagicMock()
    mock_module.competency_id = "MATH-C1"

    mock_profile = MagicMock()
    mock_profile.p_learned = 0.85

    mock_answer = MagicMock()
    mock_answer.is_correct = 1

    with patch("app.api.endpoints.diagnostic.DiagnosticRepository") as MockDiagRepo, \
         patch("app.api.endpoints.diagnostic.ContentRepository") as MockContentRepo, \
         patch("app.api.endpoints.diagnostic.get_current_student", return_value=mock_student):

        diag_repo_inst = MockDiagRepo.return_value
        diag_repo_inst.get_session = AsyncMock(return_value=mock_session)
        diag_repo_inst.get_session_answers = AsyncMock(return_value=[mock_answer] * 10)
        diag_repo_inst.get_competency_profile = AsyncMock(return_value=mock_profile)

        content_repo_inst = MockContentRepo.return_value
        content_repo_inst.get_module = AsyncMock(return_value=mock_module)

        response = await async_client.get(
            f"/api/v1/diagnostic/results/{session_id}",
            headers={"Authorization": f"Bearer test-token-{mock_student.id}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["mastery_probability"] == 0.85
        assert data["mastery_level"] == "PROFICIENT"
        assert data["total_questions"] == 10
        assert data["correct_answers"] == 10


@pytest.mark.asyncio
async def test_diagnostic_answer_idempotency_duplicate_submission(async_client: AsyncClient, db, mock_student):
    """Test duplicate answer submission returns 200 OK without double updating BKT or duplicate answer records."""
    session_id = uuid4()
    module_id = uuid4()
    question_id = uuid4()

    mock_session = MagicMock()
    mock_session.id = session_id
    mock_session.student_id = mock_student.id
    mock_session.module_id = module_id
    mock_session.status = DiagnosticSessionStatus.IN_PROGRESS
    mock_session.organization_id = mock_student.organization_id

    mock_module = MagicMock()
    mock_module.competency_id = "MATH-C1"

    mock_question = MagicMock()
    mock_question.id = question_id
    mock_question.content = {"correct_answer": "4"}
    mock_question.difficulty_level = 5
    mock_question.target_misconception_id = None

    mock_existing_answer = MagicMock()
    mock_existing_answer.question_id = question_id
    mock_existing_answer.is_correct = 1
    mock_existing_answer.error_classification = ErrorClassification.NONE

    mock_profile = MagicMock()
    mock_profile.p_learned = 0.75
    mock_profile.mastery_level = MasteryLevel.PROFICIENT

    with patch("app.api.endpoints.diagnostic.DiagnosticRepository") as MockDiagRepo, \
         patch("app.api.endpoints.diagnostic.ContentRepository") as MockContentRepo, \
         patch("app.api.endpoints.diagnostic.get_current_student", return_value=mock_student):

        diag_repo_inst = MockDiagRepo.return_value
        diag_repo_inst.get_session = AsyncMock(return_value=mock_session)
        diag_repo_inst.get_answer = AsyncMock(return_value=mock_existing_answer)
        diag_repo_inst.get_competency_profile = AsyncMock(return_value=mock_profile)
        diag_repo_inst.get_session_answers = AsyncMock(return_value=[mock_existing_answer])
        diag_repo_inst.update_or_create_competency_profile = AsyncMock()
        diag_repo_inst.record_answer = AsyncMock()

        content_repo_inst = MockContentRepo.return_value
        content_repo_inst.get_question = AsyncMock(return_value=mock_question)
        content_repo_inst.get_module = AsyncMock(return_value=mock_module)
        content_repo_inst.list_module_questions = AsyncMock(return_value=[mock_question])

        response = await async_client.post(
            "/api/v1/diagnostic/answer",
            json={
                "session_id": str(session_id),
                "question_id": str(question_id),
                "answer": "4",
                "time_ms": 10000,
            },
            headers={"Authorization": f"Bearer test-token-{mock_student.id}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_correct"] is True
        assert data["error_classification"] == "NONE"
        diag_repo_inst.update_or_create_competency_profile.assert_not_called()
        diag_repo_inst.record_answer.assert_not_called()
