"""Redis Pub/Sub Event Publisher for Tenant Real-Time Notifications."""

import json
import logging
from typing import Any
from uuid import UUID

import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)


async def publish_tenant_event(
    organization_id: str | UUID,
    event_type: str,
    payload: dict[str, Any],
) -> int:
    """Publishes JSON event payload to tenant Redis channel.

    Channel: 'events:{organization_id}'.
    Returns the number of subscribers that received the message.
    """
    channel = f"events:{organization_id}"
    message = json.dumps(
        {
            "event": event_type,
            "data": payload,
        }
    )
    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        subscribers = await redis_client.publish(channel, message)
        logger.debug(
            "Published event '%s' to channel '%s' (subscribers: %d)",
            event_type,
            channel,
            subscribers,
        )
        return subscribers
    except Exception as exc:
        logger.error(
            "Failed to publish event '%s' to channel '%s': %s",
            event_type,
            channel,
            exc,
            exc_info=True,
        )
        raise
    finally:
        await redis_client.aclose()
