"""
Unit tests for structured JSON LoggingMiddleware, request_id tracking, and error logging.
"""

import json
import logging
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.logging_middleware import LoggingMiddleware, logger
from app.core.security import create_access_token


@pytest.fixture
def app_with_logging():
    """Create a test FastAPI application with LoggingMiddleware."""
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)

    @app.get("/test-public")
    async def public_route():
        return {"message": "hello"}

    @app.get("/test-error")
    async def error_route():
        raise RuntimeError("Simulated crash")

    return app


def test_logging_middleware_adds_request_id_header(app_with_logging):
    """Test that X-Request-ID header is present in every response."""
    client = TestClient(app_with_logging)
    response = client.get("/test-public")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert UUID(response.headers["X-Request-ID"])  # Verify valid UUID string


def test_logging_middleware_preserves_incoming_request_id(app_with_logging):
    """Test that custom incoming X-Request-ID header is preserved."""
    client = TestClient(app_with_logging)
    custom_id = str(uuid4())
    response = client.get("/test-public", headers={"X-Request-ID": custom_id})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == custom_id


def test_logging_middleware_emits_json_logs(app_with_logging, caplog):
    """Test that log records emitted by middleware are parseable JSON."""
    client = TestClient(app_with_logging)
    with caplog.at_level(logging.INFO, logger="ihsane.access"):
        response = client.get("/test-public")
        assert response.status_code == 200

    log_messages = [record.message for record in caplog.records if "request_id" in record.message]
    assert len(log_messages) > 0

    log_json = json.loads(log_messages[-1])
    assert "request_id" in log_json
    assert log_json["method"] == "GET"
    assert log_json["path"] == "/test-public"
    assert log_json["status_code"] == 200
    assert "duration_ms" in log_json
    assert log_json["user_id"] is None
    assert log_json["organization_id"] is None


def test_logging_middleware_extracts_user_and_org_context(app_with_logging, caplog):
    """Test that user_id and organization_id are extracted from token and headers."""
    client = TestClient(app_with_logging)
    user_id = str(uuid4())
    org_id = str(uuid4())

    token = create_access_token(
        subject=user_id,
        additional_claims={"organizations": [{"id": org_id, "role": "EXPERT"}]},
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Organization-Id": org_id,
    }

    with caplog.at_level(logging.INFO, logger="ihsane.access"):
        response = client.get("/test-public", headers=headers)
        assert response.status_code == 200

    log_messages = [record.message for record in caplog.records if "request_id" in record.message]
    assert len(log_messages) > 0

    log_json = json.loads(log_messages[-1])
    assert log_json["user_id"] == user_id
    assert log_json["organization_id"] == org_id


def test_logging_middleware_handles_unhandled_exceptions(app_with_logging, caplog):
    """Test that unhandled exceptions log at ERROR level with stack trace and return 500."""
    client = TestClient(app_with_logging, raise_server_exceptions=False)

    with caplog.at_level(logging.ERROR, logger="ihsane.access"):
        response = client.get("/test-error")
        assert response.status_code == 500
        assert "X-Request-ID" in response.headers

    error_logs = [record for record in caplog.records if record.levelno == logging.ERROR]
    assert len(error_logs) > 0
    error_json = json.loads(error_logs[0].message)
    assert error_json["status_code"] == 500
    assert error_json["error"] == "Simulated crash"
