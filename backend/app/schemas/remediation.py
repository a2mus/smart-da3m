"""
Pydantic schemas for remediation pathways and Passport assessments.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.remediation import RemediationPathStatus


# ==================== Remediation Path Schemas ====================

class RemediationAtom(BaseModel):
    """Schema for a remediation atom in a pathway."""

    id: UUID
    competency_id: str
    remediation_type: str
    content: Dict[str, Any]
    order: int = 0


class RemediationPathResponse(BaseModel):
    """Schema for remediation pathway response."""

    id: UUID
    student_id: UUID
    competency_id: str
    status: RemediationPathStatus
    atoms: List[RemediationAtom]
    atoms_completed: List[UUID]
    progress_percent: float = Field(0.0, ge=0.0, le=100.0)
    current_difficulty: int = Field(5, ge=1, le=10)
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RemediationPathRequest(BaseModel):
    """Schema for requesting a remediation pathway."""

    competency_id: str
    student_group: str = Field(default="B", pattern="^[ABC]$")


# ==================== Atom Completion Schemas ====================

class AtomCompleteRequest(BaseModel):
    """Schema for marking an atom as complete."""

    time_spent_ms: int = Field(..., ge=0)
    interactions_count: int = Field(default=1, ge=1)
    is_correct: bool = True


class AtomCompleteResponse(BaseModel):
    """Schema for atom completion response."""

    atom_id: UUID
    atoms_completed: int
    total_atoms: int
    progress_percent: float
    new_difficulty: int
    next_atom: Optional[RemediationAtom] = None
    recommendation: Optional[str] = None


# ==================== Passport Assessment Schemas ====================

class PassportAnswer(BaseModel):
    """Schema for a Passport answer."""

    question_id: str
    answer: str
    time_ms: int = Field(..., ge=0)


class PassportEvaluateRequest(BaseModel):
    """Schema for evaluating a Passport assessment."""

    competency_id: str
    answers: List[PassportAnswer]


class PassportEvaluateResponse(BaseModel):
    """Schema for Passport evaluation results."""

    passed: bool
    accuracy: float = Field(..., ge=0.0, le=1.0)
    correct_count: int
    total_questions: int
    previous_mastery_level: str
    new_mastery_level: str
    badge_earned: Optional[str] = None
    alert_triggered: bool = False
    message: str


class PassportQuestion(BaseModel):
    """Schema for a Passport question."""

    id: str
    content: Dict[str, Any]
    difficulty_level: int


class PassportQuestionsResponse(BaseModel):
    """Schema for Passport questions response."""

    competency_id: str
    questions: List[PassportQuestion]
    assessment_id: UUID


# ==================== Engagement Tracking Schemas ====================

class EngagementStatusResponse(BaseModel):
    """Schema for student engagement status."""

    is_frustrated: bool
    is_bored: bool
    recommendation: str
    message: str


class RemediationStatusResponse(BaseModel):
    """Schema for remediation status."""

    competency_id: str
    status: RemediationPathStatus
    atoms_completed: List[UUID]
    progress_percent: float
    can_take_passport: bool
