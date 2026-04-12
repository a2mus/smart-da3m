"""
Pydantic schemas for diagnostic sessions and answers.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.diagnostic import (
    DiagnosticSessionStatus,
    ErrorClassification,
    MasteryLevel,
    RemediationGroup,
)


# ==================== Diagnostic Session Schemas ====================

class DiagnosticSessionCreate(BaseModel):
    """Schema for starting a diagnostic session."""

    module_id: UUID


class DiagnosticSessionResponse(BaseModel):
    """Schema for diagnostic session response."""

    id: UUID
    student_id: UUID
    module_id: UUID
    status: DiagnosticSessionStatus
    recommended_group: Optional[RemediationGroup] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StartDiagnosticResponse(BaseModel):
    """Schema for start diagnostic response with first question."""

    session_id: UUID
    question: Dict[str, Any]  # Question content
    question_number: int = 1


# ==================== Answer Submission Schemas ====================

class AnswerSubmitRequest(BaseModel):
    """Schema for submitting an answer."""

    session_id: UUID
    question_id: UUID
    answer: str
    time_ms: int = Field(..., ge=0, description="Response time in milliseconds")


class AnswerSubmitResponse(BaseModel):
    """Schema for answer submission response."""

    is_correct: bool
    error_classification: ErrorClassification
    current_mastery: float = Field(..., ge=0.0, le=1.0)
    mastery_level: MasteryLevel
    next_question: Optional[Dict[str, Any]] = None
    is_complete: bool = False


# ==================== Diagnostic Results Schemas ====================

class DiagnosticResultsResponse(BaseModel):
    """Schema for diagnostic results."""

    session_id: UUID
    mastery_probability: float = Field(..., ge=0.0, le=1.0)
    mastery_level: MasteryLevel
    recommended_group: RemediationGroup
    total_questions: int
    correct_answers: int
    accuracy: float = Field(..., ge=0.0, le=1.0)
    completed_at: datetime


# ==================== Competency Profile Schemas ====================

class CompetencyProfileResponse(BaseModel):
    """Schema for competency profile."""

    id: UUID
    student_id: UUID
    competency_id: str
    mastery_level: MasteryLevel
    p_learned: float = Field(..., ge=0.0, le=1.0)
    last_assessed: datetime

    class Config:
        from_attributes = True


class CompetencyProfileUpdate(BaseModel):
    """Schema for updating competency profile."""

    mastery_level: Optional[MasteryLevel] = None
    p_learned: Optional[float] = Field(None, ge=0.0, le=1.0)
