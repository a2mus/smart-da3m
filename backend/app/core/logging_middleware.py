"""
Structured JSON logging middleware and log formatting for FastAPI/Starlette.
Provides request_id tracking, tenant/user context extraction, and JSON log emission.
"""

import json
import logging
import sys
import time
import traceback
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from fastapi import status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.security import verify_token
from app.core.tenant import get_optional_active_organization_id

# Configure logger for HTTP requests
logger = logging.getLogger("ihsane.access")
logger.setLevel(logging.INFO)

# Ensure handler is attached if not already
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.propagate = False


class JSONLogFormatter(logging.Formatter):
    """Formats log records as JSON strings."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        if record.exc_info:
            log_data["exception"] = "".join(traceback.format_exception(*record.exc_info))

        return json.dumps(log_data)


def extract_user_id_from_request(request: Request) -> Optional[str]:
    """Safely extract user_id (sub) from Authorization Bearer token without raising exceptions."""
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1]
    payload = verify_token(token)
    if payload and "sub" in payload:
        return str(payload["sub"])
    if payload and "user_id" in payload:
        return str(payload["user_id"])
    return None


def extract_org_id_from_request(request: Request) -> Optional[str]:
    """Extract organization_id from contextvar, X-Organization-Id header, or JWT payload."""
    active_org = get_optional_active_organization_id()
    if active_org:
        return str(active_org)

    org_header = request.headers.get("x-organization-id") or request.headers.get("X-Organization-Id")
    if org_header:
        try:
            return str(UUID(org_header))
        except ValueError:
            pass

    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
        payload = verify_token(token)
        if payload and payload.get("organization_id"):
            return str(payload["organization_id"])

    return None


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that assigns a unique request_id to each HTTP request,
    measures request execution duration, logs structured JSON log records,
    and returns the X-Request-ID header in responses.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id") or request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid4())

        request.state.request_id = request_id
        start_time = time.perf_counter()

        user_id = extract_user_id_from_request(request)
        org_id_str = extract_org_id_from_request(request)

        response: Optional[Response] = None
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            log_payload = {
                "request_id": request_id,
                "user_id": user_id,
                "organization_id": extract_org_id_from_request(request) or org_id_str,
                "method": request.method,
                "path": request.url.path,
                "status_code": 500,
                "duration_ms": duration_ms,
                "error": str(exc),
            }
            logger.error(json.dumps(log_payload), exc_info=True)

            err_response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal Server Error"},
            )
            err_response.headers["X-Request-ID"] = request_id
            return err_response
        finally:
            if response is not None:
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                log_payload = {
                    "request_id": request_id,
                    "user_id": user_id,
                    "organization_id": extract_org_id_from_request(request) or org_id_str,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                }
                logger.info(json.dumps(log_payload))

        response.headers["X-Request-ID"] = request_id
        return response
