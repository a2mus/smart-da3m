"""Server-Sent Events (SSE) Endpoint for Real-Time Tenant Notifications."""

import asyncio
import contextlib
import json
import logging
from collections.abc import AsyncGenerator
from uuid import UUID

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.core.config import settings
from app.core.security import verify_token
from app.db.session import get_db
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()
optional_security = HTTPBearer(auto_error=False)


async def authenticate_sse_user(
    token_param: str | None = Query(None, alias="token"),
    credentials: HTTPAuthorizationCredentials | None = Depends(  # noqa: B008
        optional_security
    ),
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> tuple[User, dict]:
    """Extracts token from Bearer header OR query param 'token'.

    Validates the JWT, and returns (user, token_payload).
    """
    token = None
    if credentials and credentials.credentials:
        token = credentials.credentials
    elif token_param:
        token = token_param

    if not token:
        detail_msg = (
            "Authentication token required "
            "(Bearer header or 'token' query param)"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail_msg,
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_uuid = UUID(user_id)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format in token",
        ) from err

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user, payload


def resolve_active_organization(
    request: Request,
    payload: dict,
    org_param: str | None = Query(None, alias="organization_id"),
) -> UUID:
    """Resolves target organization ID from headers, query param, or payload.

    Validates user membership.
    """
    org_header = request.headers.get(
        "x-organization-id"
    ) or request.headers.get("X-Organization-Id")
    target_str = org_header or org_param

    allowed_orgs: set[UUID] = set()
    orgs_claim = payload.get("organizations", [])
    for item in orgs_claim:
        if isinstance(item, dict) and "id" in item:
            with contextlib.suppress(ValueError):
                allowed_orgs.add(UUID(str(item["id"])))
        elif isinstance(item, (str, UUID)):
            with contextlib.suppress(ValueError):
                allowed_orgs.add(UUID(str(item)))

    single_org = payload.get("organization_id")
    if single_org:
        with contextlib.suppress(ValueError):
            allowed_orgs.add(UUID(str(single_org)))

    target_uuid: UUID | None = None
    if target_str:
        try:
            target_uuid = UUID(target_str)
        except ValueError as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid organization ID format",
            ) from err
        if allowed_orgs and target_uuid not in allowed_orgs:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of the specified organization",
            )
    else:
        if len(allowed_orgs) == 1:
            target_uuid = next(iter(allowed_orgs))
        elif payload.get("organization_id"):
            with contextlib.suppress(ValueError):
                target_uuid = UUID(str(payload["organization_id"]))

    if not target_uuid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active organization context is required",
        )

    return target_uuid


@router.get("/stream", response_class=EventSourceResponse)
async def event_stream(
    request: Request,
    user_and_payload: tuple[User, dict] = Depends(authenticate_sse_user),
    org_param: str | None = Query(None, alias="organization_id"),
):
    """Real-time Server-Sent Events (SSE) stream for tenant notifications.

    Subscribes to Redis Pub/Sub channel 'events:{organization_id}'.
    """
    user, payload = user_and_payload
    org_id = resolve_active_organization(request, payload, org_param)
    channel_name = f"events:{org_id}"

    async def event_generator() -> AsyncGenerator[dict, None]:
        redis_client = aioredis.from_url(
            settings.REDIS_URL, decode_responses=True
        )
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(channel_name)
        logger.info(
            "User %s connected to SSE stream for org %s (channel: %s)",
            user.id,
            org_id,
            channel_name,
        )

        try:
            yield {
                "event": "connected",
                "data": json.dumps(
                    {"status": "connected", "organization_id": str(org_id)}
                ),
            }

            while True:
                if await request.is_disconnected():
                    logger.info(
                        "Client disconnected from SSE stream for org %s",
                        org_id,
                    )
                    break

                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=1.0
                )
                if message and message.get("type") == "message":
                    raw_data = message.get("data")
                    try:
                        parsed = json.loads(raw_data)
                        event_type = parsed.get("event", "message")
                        payload_data = parsed.get("data", parsed)
                        formatted_data = (
                            json.dumps(payload_data)
                            if not isinstance(payload_data, str)
                            else payload_data
                        )
                        yield {
                            "event": event_type,
                            "data": formatted_data,
                        }
                    except json.JSONDecodeError:
                        yield {
                            "event": "message",
                            "data": raw_data,
                        }

                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            logger.info("SSE event stream task cancelled for user %s", user.id)
        except Exception as exc:
            logger.error("Error in SSE event stream: %s", exc, exc_info=True)
        finally:
            await pubsub.unsubscribe(channel_name)
            await pubsub.close()
            await redis_client.aclose()
            logger.info("Closed Redis Pub/Sub connection for org %s", org_id)

    return EventSourceResponse(event_generator())
