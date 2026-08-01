"""
API endpoints for offline batch synchronization.
"""

from time import time
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_student, get_db
from app.models.user import User
from app.repositories.sync_repo import SyncRepository
from app.schemas.sync import SyncBatchRequest, SyncBatchResponse

router = APIRouter()

# In-memory rate limiter tracking request timestamps per student ID
_rate_limit_store: Dict[str, List[float]] = {}
RATE_LIMIT_WINDOW = 60.0  # seconds
RATE_LIMIT_MAX_REQUESTS = 30  # max batch sync requests per minute per student


def reset_rate_limit_store() -> None:
    """Reset rate limiter store (useful for unit testing)."""
    _rate_limit_store.clear()


def enforce_rate_limit(user_id: str) -> None:
    """Enforce rate limiting for batch sync requests per user."""
    now = time()
    history = _rate_limit_store.get(user_id, [])
    # Remove timestamps older than window
    recent_history = [t for t in history if now - t < RATE_LIMIT_WINDOW]

    if len(recent_history) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait before syncing again.",
        )

    recent_history.append(now)
    _rate_limit_store[user_id] = recent_history


@router.post(
    "/batch",
    response_model=SyncBatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Batch sync offline diagnostic answers and atom completions",
)
async def sync_batch(
    sync_request: SyncBatchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_student),
) -> SyncBatchResponse:
    """Process batched offline answers and atom completions idempotently."""
    enforce_rate_limit(str(current_user.id))

    sync_repo = SyncRepository(db)
    accepted, rejected, errors = await sync_repo.process_batch_sync(
        current_user=current_user,
        sync_request=sync_request,
    )

    return SyncBatchResponse(
        accepted=accepted,
        rejected=rejected,
        errors=errors,
    )
