"""
Integration tests for Story 1.9: Parent PIN Management Endpoint (POST /api/v1/auth/children/{id}/pin).
"""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_pin_hash, verify_pin
from app.models.user import User, UserRole


@pytest.fixture
async def parent_user(db: AsyncSession) -> User:
    user = User(
        email=f"parent_{uuid.uuid4().hex[:8]}@test.com",
        hashed_password="hashed_password",
        role=UserRole.PARENT,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def other_parent_user(db: AsyncSession) -> User:
    user = User(
        email=f"other_parent_{uuid.uuid4().hex[:8]}@test.com",
        hashed_password="hashed_password",
        role=UserRole.PARENT,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def child_user(db: AsyncSession, parent_user: User) -> User:
    user = User(
        email=None,
        pin_code_hash=get_pin_hash("1234"),
        role=UserRole.STUDENT,
        parent_id=parent_user.id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
def auth_headers(parent_user: User) -> dict:
    token = create_access_token(
        subject=str(parent_user.id),
        additional_claims={"role": UserRole.PARENT.value},
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_auth_headers(other_parent_user: User) -> dict:
    token = create_access_token(
        subject=str(other_parent_user.id),
        additional_claims={"role": UserRole.PARENT.value},
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_reset_child_pin_success(
    async_client: AsyncClient,
    db: AsyncSession,
    parent_user: User,
    child_user: User,
    auth_headers: dict,
):
    response = await async_client.post(
        f"/api/v1/auth/children/{child_user.id}/pin",
        json={"pin_code": "5678"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(child_user.id)

    await db.refresh(child_user)
    assert verify_pin("5678", child_user.pin_code_hash)


@pytest.mark.asyncio
async def test_reset_child_pin_forbidden_for_other_parent(
    async_client: AsyncClient,
    child_user: User,
    other_auth_headers: dict,
):
    response = await async_client.post(
        f"/api/v1/auth/children/{child_user.id}/pin",
        json={"pin_code": "9999"},
        headers=other_auth_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_reset_child_pin_invalid_pin_format(
    async_client: AsyncClient,
    child_user: User,
    auth_headers: dict,
):
    response = await async_client.post(
        f"/api/v1/auth/children/{child_user.id}/pin",
        json={"pin_code": "abc1"},
        headers=auth_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_reset_child_pin_not_found(
    async_client: AsyncClient,
    auth_headers: dict,
):
    non_existent_id = uuid.uuid4()
    response = await async_client.post(
        f"/api/v1/auth/children/{non_existent_id}/pin",
        json={"pin_code": "1234"},
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_reset_child_pin_forbidden_for_student_role(
    async_client: AsyncClient,
    child_user: User,
):
    token = create_access_token(
        subject=str(child_user.id),
        additional_claims={"role": UserRole.STUDENT.value},
    )
    student_headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.post(
        f"/api/v1/auth/children/{child_user.id}/pin",
        json={"pin_code": "4321"},
        headers=student_headers,
    )
    assert response.status_code == 403
