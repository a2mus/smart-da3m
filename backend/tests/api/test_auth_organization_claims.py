"""
Integration tests for JWT organization claims and auth flow updates.
"""

import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_token
from app.models.organization import Organization, OrganizationMember, OrganizationType
from app.models.user import User, UserRole


@pytest.mark.asyncio
async def test_parent_registration_creates_household_org(async_client: AsyncClient, db: AsyncSession):
    register_payload = {
        "email": "test_parent_org@example.com",
        "password": "securepassword123",
        "language": "AR",
    }
    response = await async_client.post("/api/v1/auth/register/parent", json=register_payload)
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["email"] == "test_parent_org@example.com"
    parent_id = uuid.UUID(user_data["id"])

    # Verify household organization and member record were created
    login_response = await async_client.post(
        "/api/v1/auth/login/email",
        json={"email": "test_parent_org@example.com", "password": "securepassword123"},
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data

    # Verify JWT payload contains organizations claim
    payload = verify_token(token_data["access_token"])
    assert payload is not None
    assert "organizations" in payload
    orgs = payload["organizations"]
    assert len(orgs) == 1
    assert orgs[0]["role"] == "PARENT"
    assert orgs[0]["type"] == "HOUSEHOLD"


@pytest.mark.asyncio
async def test_student_registration_and_pin_login_org_claims(async_client: AsyncClient, db: AsyncSession):
    # 1. Register parent
    parent_resp = await async_client.post(
        "/api/v1/auth/register/parent",
        json={"email": "parent_for_student@example.com", "password": "securepassword123", "language": "FR"},
    )
    assert parent_resp.status_code == 201
    parent_id = parent_resp.json()["id"]

    # 2. Register student
    student_resp = await async_client.post(
        "/api/v1/auth/register/student",
        json={"parent_id": parent_id, "pin_code": "1234"},
    )
    assert student_resp.status_code == 201

    # 3. Login student via PIN
    pin_login_resp = await async_client.post(
        "/api/v1/auth/login/pin",
        json={"pin_code": "1234"},
    )
    assert pin_login_resp.status_code == 200
    token_data = pin_login_resp.json()

    # 4. Verify student JWT organizations claim
    payload = verify_token(token_data["access_token"])
    assert payload is not None
    assert payload["role"] == "STUDENT"
    assert "organizations" in payload
    orgs = payload["organizations"]
    assert len(orgs) == 1
    assert orgs[0]["role"] == "STUDENT"
    assert orgs[0]["type"] == "HOUSEHOLD"


@pytest.mark.asyncio
async def test_refresh_token_preserves_organization_claims(async_client: AsyncClient, db: AsyncSession):
    # Register and login
    await async_client.post(
        "/api/v1/auth/register/parent",
        json={"email": "refresh_parent@example.com", "password": "securepassword123", "language": "AR"},
    )
    login_resp = await async_client.post(
        "/api/v1/auth/login/email",
        json={"email": "refresh_parent@example.com", "password": "securepassword123"},
    )
    assert login_resp.status_code == 200
    refresh_token = login_resp.json()["refresh_token"]

    # Refresh
    refresh_resp = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_resp.status_code == 200
    new_access_token = refresh_resp.json()["access_token"]

    payload = verify_token(new_access_token)
    assert payload is not None
    assert "organizations" in payload
    assert len(payload["organizations"]) == 1


@pytest.mark.asyncio
async def test_legacy_user_without_org_gets_household_on_login(async_client: AsyncClient, db: AsyncSession):
    # Manually insert a user with no org membership
    from app.core.security import get_password_hash
    legacy_user = User(
        email="legacy_parent@example.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.PARENT,
    )
    db.add(legacy_user)
    await db.commit()

    # Login legacy user
    login_resp = await async_client.post(
        "/api/v1/auth/login/email",
        json={"email": "legacy_parent@example.com", "password": "password123"},
    )
    assert login_resp.status_code == 200
    payload = verify_token(login_resp.json()["access_token"])
    assert payload is not None
    assert "organizations" in payload
    assert len(payload["organizations"]) == 1
    assert payload["organizations"][0]["type"] == "HOUSEHOLD"
