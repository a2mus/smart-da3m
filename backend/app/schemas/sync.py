"""
Pydantic schemas for offline batch synchronization endpoint POST /api/v1/sync/batch.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SyncAnswerItem(BaseModel):
    """Schema for a queued offline diagnostic answer."""

    id: str = Field(..., description="Client-generated unique ID for offline item tracking")
    session_id: UUID
    question_id: UUID
    answer: str
    time_ms: int = Field(..., ge=0, description="Response time in milliseconds")
    created_at: Optional[datetime] = None


class SyncCompletionItem(BaseModel):
    """Schema for a queued offline knowledge atom completion."""

    id: str = Field(..., description="Client-generated unique ID for offline item tracking")
    atom_id: UUID
    time_spent_ms: int = Field(..., ge=0, description="Time spent in milliseconds")
    interactions_count: int = Field(default=1, ge=1)
    is_correct: bool = True
    created_at: Optional[datetime] = None


class SyncBatchRequest(BaseModel):
    """Schema for batch offline sync request."""

    answers: List[SyncAnswerItem] = Field(default_factory=list)
    completions: List[SyncCompletionItem] = Field(default_factory=list)
    since: Optional[datetime] = Field(None, description="Client last sync timestamp filter")


class SyncErrorDetail(BaseModel):
    """Schema for individual item processing failure in batch sync."""

    id: str
    reason: str


class SyncBatchResponse(BaseModel):
    """Schema for batch offline sync response."""

    accepted: int = Field(..., ge=0, description="Number of successfully processed or idempotent items")
    rejected: int = Field(..., ge=0, description="Number of failed/rejected items")
    errors: List[SyncErrorDetail] = Field(default_factory=list, description="List of item rejection details")
