"""
Pydantic schemas for content management (modules, questions, knowledge atoms).
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.content import ModuleStatus, RemediationType


# ==================== Module Schemas ====================

class ModuleBase(BaseModel):
    """Base schema for modules."""

    subject: str = Field(..., min_length=1, max_length=100)
    grade_level: str = Field(..., min_length=1, max_length=50)
    domain: str = Field(..., min_length=1, max_length=200)
    competency_id: str = Field(..., min_length=1, max_length=50)


class ModuleCreate(ModuleBase):
    """Schema for creating a new module."""

    status: Optional[ModuleStatus] = ModuleStatus.DRAFT


class ModuleUpdate(BaseModel):
    """Schema for updating a module."""

    subject: Optional[str] = Field(None, min_length=1, max_length=100)
    grade_level: Optional[str] = Field(None, min_length=1, max_length=50)
    domain: Optional[str] = Field(None, min_length=1, max_length=200)
    competency_id: Optional[str] = Field(None, min_length=1, max_length=50)
    status: Optional[ModuleStatus] = None


class ModuleResponse(ModuleBase):
    """Schema for module responses."""

    id: UUID
    status: ModuleStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModuleListResponse(BaseModel):
    """Schema for paginated module list."""

    items: List[ModuleResponse]
    total: int
    page: int
    page_size: int


# ==================== Question Schemas ====================

class QuestionContent(BaseModel):
    """Schema for question content structure."""

    text: str = Field(..., min_length=1)
    type: str = Field(default="multiple_choice")
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    media_urls: Optional[List[str]] = None


class QuestionBase(BaseModel):
    """Base schema for questions."""

    module_id: UUID
    content: QuestionContent
    difficulty_level: int = Field(..., ge=1, le=10)
    target_misconception_id: Optional[str] = Field(None, max_length=50)
    estimated_time_sec: int = Field(default=60, ge=5)


class QuestionCreate(QuestionBase):
    """Schema for creating a new question."""

    pass


class QuestionUpdate(BaseModel):
    """Schema for updating a question."""

    content: Optional[QuestionContent] = None
    difficulty_level: Optional[int] = Field(None, ge=1, le=10)
    target_misconception_id: Optional[str] = Field(None, max_length=50)
    estimated_time_sec: Optional[int] = Field(None, ge=5)


class QuestionResponse(QuestionBase):
    """Schema for question responses."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuestionListResponse(BaseModel):
    """Schema for paginated question list."""

    items: List[QuestionResponse]
    total: int
    page: int
    page_size: int


class BulkQuestionCreate(BaseModel):
    """Schema for bulk creating questions."""

    module_id: UUID
    questions: List[QuestionCreate]


class BulkQuestionResponse(BaseModel):
    """Schema for bulk question creation response."""

    imported_count: int
    imported_ids: List[UUID]
    errors: Optional[List[Dict[str, Any]]] = None


# ==================== Knowledge Atom Schemas ====================

class KnowledgeAtomContent(BaseModel):
    """Schema for knowledge atom content structure."""

    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    media_url: Optional[str] = None
    interactive_data: Optional[Dict[str, Any]] = None


class KnowledgeAtomBase(BaseModel):
    """Base schema for knowledge atoms."""

    competency_id: str = Field(..., min_length=1, max_length=50)
    remediation_type: RemediationType
    content: KnowledgeAtomContent


class KnowledgeAtomCreate(KnowledgeAtomBase):
    """Schema for creating a knowledge atom."""

    pass


class KnowledgeAtomUpdate(BaseModel):
    """Schema for updating a knowledge atom."""

    competency_id: Optional[str] = Field(None, min_length=1, max_length=50)
    remediation_type: Optional[RemediationType] = None
    content: Optional[KnowledgeAtomContent] = None


class KnowledgeAtomResponse(KnowledgeAtomBase):
    """Schema for knowledge atom responses."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KnowledgeAtomListResponse(BaseModel):
    """Schema for knowledge atom list response."""

    items: List[KnowledgeAtomResponse]
    total: int
    page: int
    page_size: int
