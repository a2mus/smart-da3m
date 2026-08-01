"""
Integration tests for Story 1.6: Self-Registration Flow for Independent Parents.
"""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_token


@pytest.mark.asyncio
async def test_parent_self_registration_with_name(async_client: AsyncClient, db: AsyncSession):
    register_payload = {
        "email": "independent_parent_named@example.com",
        "password": "securepassword123",
        "name": "Sarah Connor",
        "language": "AR",
    }
    response = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["email"] == "independent_parent_named@example.com"
    assert user_data["role"] == "PARENT"

    # Login to verify JWT access token and household organization name
    login_response = await async_client.post(
        "/api/v1/auth/login/email",
        json={"email": "independent_parent_named@example.com", "password": "securepassword123"},
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data

    payload = verify_token(token_data["access_token"])
    assert payload is not None
    assert "organizations" in payload
    orgs = payload["organizations"]
    assert len(orgs) == 1
    assert orgs[0]["role"] == "PARENT"
    assert orgs[0]["type"] == "HOUSEHOLD"


@pytest.mark.asyncio
async def test_parent_self_registration_without_name(async_client: AsyncClient, db: AsyncSession):
    register_payload = {
        "email": "independent_parent_unnamed@example.com",
        "password": "securepassword123",
        "language": "FR",
    }
    response = await async_client.post("/api/v1/auth/register/parent", json=register_payload)
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["email"] == "independent_parent_unnamed@example.com"
    assert user_data["role"] == "PARENT"

    login_response = await async_client.post(
        "/api/v1/auth/login/email",
        json={"email": "independent_parent_unnamed@example.com", "password": "securepassword123"},
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    payload = verify_token(token_data["access_token"])
    assert payload is not None
    assert len(payload["organizations"]) == 1
    assert payload["organizations"][0]["type"] == "HOUSEHOLD"


@pytest.mark.asyncio
async def test_parent_registration_duplicate_email(async_client: AsyncClient, db: AsyncSession):
    payload = {
        "email": "duplicate_parent@example.com",
        "password": "securepassword123",
    }
    resp1 = await async_client.post("/api/v1/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = await async_client.post("/api/v1/auth/register", json=payload)
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Email already registered"
