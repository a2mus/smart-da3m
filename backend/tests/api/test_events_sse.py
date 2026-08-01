"""Unit and integration tests for Server-Sent Events (SSE) streaming endpoint."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_authenticate_sse_user_missing_token(async_client: AsyncClient):
    """Test that requesting SSE stream without auth token returns 401."""
    response = await async_client.get("/api/v1/events/stream")
    assert response.status_code == 401
    assert "token" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_authenticate_sse_user_invalid_token(async_client: AsyncClient):
    """Test that invalid JWT token returns 401."""
    response = await async_client.get("/api/v1/events/stream?token=invalid_jwt_token")
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_event_publisher_unit():
    """Test publish_tenant_event helper using mocked Redis client."""
    org_id = uuid4()
    with patch("redis.asyncio.from_url") as mock_from_url:
        mock_redis = AsyncMock()
        mock_redis.publish.return_value = 2
        mock_from_url.return_value = mock_redis

        from app.services.event_publisher import publish_tenant_event

        subscribers = await publish_tenant_event(
            organization_id=org_id,
            event_type="test_alert",
            payload={"message": "hello"},
        )

        assert subscribers == 2
        mock_redis.publish.assert_called_once()
        call_args = mock_redis.publish.call_args
        assert call_args[0][0] == f"events:{org_id}"
        assert "test_alert" in call_args[0][1]
