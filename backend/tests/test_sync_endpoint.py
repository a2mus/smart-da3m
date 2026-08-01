"""
Unit and integration tests for Backend Sync Endpoint POST /api/v1/sync/batch.
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from app.api.deps import get_current_student
from app.api.endpoints.sync import reset_rate_limit_store
from app.main import app
from app.models.diagnostic import DiagnosticSessionStatus
from app.models.user import User, UserRole


@pytest.fixture
def mock_student():
    student = User(
        id=uuid4(),
        email="student_sync@test.com",
        role=UserRole.STUDENT,
    )
    student.organization_id = uuid4()
    app.dependency_overrides[get_current_student] = lambda: student
    reset_rate_limit_store()
    yield student
    app.dependency_overrides.pop(get_current_student, None)
    reset_rate_limit_store()


@pytest.mark.asyncio
async def test_sync_batch_success(async_client: AsyncClient, db, mock_student):
    """Test POST /api/v1/sync/batch processes valid answer and atom completion items."""
    session_id = uuid4()
    question_id = uuid4()
    atom_id = uuid4()

    sync_payload = {
        "answers": [
            {
                "id": "item-ans-1",
                "session_id": str(session_id),
                "question_id": str(question_id),
                "answer": "4",
                "time_ms": 2500,
            }
        ],
        "completions": [
            {
                "id": "item-atom-1",
                "atom_id": str(atom_id),
                "time_spent_ms": 12000,
                "interactions_count": 2,
                "is_correct": True,
            }
        ],
    }

    with patch("app.api.endpoints.sync.SyncRepository") as MockSyncRepo:
        sync_repo_inst = MockSyncRepo.return_value
        sync_repo_inst.process_batch_sync = AsyncMock(return_value=(2, 0, []))

        response = await async_client.post(
            "/api/v1/sync/batch",
            json=sync_payload,
            headers={"Authorization": f"Bearer test-token-{mock_student.id}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["accepted"] == 2
        assert data["rejected"] == 0
        assert data["errors"] == []


@pytest.mark.asyncio
async def test_sync_batch_idempotency_and_partial_failure(async_client: AsyncClient, db, mock_student):
    """Test batch sync returns partial success with accepted and rejected counts."""
    sync_payload = {
        "answers": [
            {
                "id": "valid-ans",
                "session_id": str(uuid4()),
                "question_id": str(uuid4()),
                "answer": "42",
                "time_ms": 3000,
            },
            {
                "id": "invalid-ans",
                "session_id": str(uuid4()),
                "question_id": str(uuid4()),
                "answer": "0",
                "time_ms": 1000,
            },
        ],
        "completions": [],
    }

    errors = [{"id": "invalid-ans", "reason": "Session not found or invalid question"}]

    with patch("app.api.endpoints.sync.SyncRepository") as MockSyncRepo:
        sync_repo_inst = MockSyncRepo.return_value
        sync_repo_inst.process_batch_sync = AsyncMock(return_value=(1, 1, errors))

        response = await async_client.post(
            "/api/v1/sync/batch",
            json=sync_payload,
            headers={"Authorization": f"Bearer test-token-{mock_student.id}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["accepted"] == 1
        assert data["rejected"] == 1
        assert len(data["errors"]) == 1
        assert data["errors"][0]["id"] == "invalid-ans"


@pytest.mark.asyncio
async def test_sync_batch_rate_limiting(async_client: AsyncClient, db, mock_student):
    """Test rate limiting returns 429 Too Many Requests after exceeding max requests."""
    sync_payload = {"answers": [], "completions": []}

    with patch("app.api.endpoints.sync.SyncRepository") as MockSyncRepo:
        sync_repo_inst = MockSyncRepo.return_value
        sync_repo_inst.process_batch_sync = AsyncMock(return_value=(0, 0, []))

        # Send requests up to rate limit threshold (30 requests)
        for _ in range(30):
            res = await async_client.post(
                "/api/v1/sync/batch",
                json=sync_payload,
                headers={"Authorization": f"Bearer test-token-{mock_student.id}"},
            )
            assert res.status_code == status.HTTP_200_OK

        # 31st request triggers HTTP 429
        res_overflow = await async_client.post(
            "/api/v1/sync/batch",
            json=sync_payload,
            headers={"Authorization": f"Bearer test-token-{mock_student.id}"},
        )
        assert res_overflow.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Rate limit exceeded" in res_overflow.json()["detail"]
