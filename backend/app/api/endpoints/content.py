"""
API endpoints for content management (modules, questions, knowledge atoms).
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_expert_user, get_db
from app.models.content import ModuleStatus
from app.models.user import User
from app.schemas.content import (
    BulkQuestionCreate,
    BulkQuestionResponse,
    KnowledgeAtomCreate,
    KnowledgeAtomListResponse,
    KnowledgeAtomResponse,
    KnowledgeAtomUpdate,
    ModuleCreate,
    ModuleListResponse,
    ModuleResponse,
    ModuleUpdate,
    QuestionCreate,
    QuestionListResponse,
    QuestionResponse,
    QuestionUpdate,
)
from app.services.content_service import ContentService

router = APIRouter()


# ==================== Module Endpoints ====================

@router.post(
    "/modules",
    response_model=ModuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new curriculum module",
)
async def create_module(
    module_data: ModuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert_user),
) -> ModuleResponse:
    """Create a new curriculum module.

    Only experts can create modules.
    """
    service = ContentService(db)
    module = await service.create_module(module_data)
    return module


@router.get(
    "/modules",
    response_model=ModuleListResponse,
    summary="List all curriculum modules",
)
async def list_modules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    subject: Optional[str] = None,
    grade_level: Optional[str] = None,
    status: Optional[ModuleStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert_user),
) -> ModuleListResponse:
    """List curriculum modules with optional filtering."""
    service = ContentService(db)
    modules, total = await service.list_modules(
        skip=skip,
        limit=limit,
        subject=subject,
        grade_level=grade_level,
        status=status,
    )
    return ModuleListResponse(
        items=modules,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
    )


@router.get(
    "/modules/{module_id}",
    response_model=ModuleResponse,
    summary="Get a specific module by ID",
)
async def get_module(
    module_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert_user),
) -> ModuleResponse:
    """Get a specific curriculum module by ID."""
    service = ContentService(db)
    module = await service.get_module(module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found",
        )
    return module


@router.patch(
    "/modules/{module_id}",
    response_model=ModuleResponse,
    summary="Update a curriculum module",
)
async def update_module(
    module_id: UUID,
    update_data: ModuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert_user),
) -> ModuleResponse:
    """Update a curriculum module."""
    service = ContentService(db)
    module = await service.update_module(module_id, update_data)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found",
        )
    return module


@router.delete(
    "/modules/{module_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a curriculum module",
)
async def delete_module(
    module_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert_user),
) -> None:
    """Delete a curriculum module."""
    service = ContentService(db)
    deleted = await service.delete_module(module_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found",
        )


# ==================== Question Endpoints ====================

@router.post(
    "/questions",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new question",
)
async def create_question(
    question_data: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert_user),
) -> QuestionResponse:
    """Create a new question in a module's question bank."""
    service = ContentService(db)
    question = await service.create_question(question_data)
    return question


@router.get(
    "/questions",
    response_model=QuestionListResponse,
    summary="List questions",
)
async def list_questions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    module_id: Optional[UUID] = None,
    difficulty_level: Optional[int] = Query(None, ge=1, le=10),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert_user),
) -> QuestionListResponse:
    """List questions with optional filtering by module."""
    service = ContentService(db)
    questions, total = await service.list_questions(
        skip=skip,
        limit=limit,
        module_id=module_id,
        difficulty_level=difficulty_level,
    )
    return QuestionListResponse(
        items=questions,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
    )


@router.get(
    "/questions/{question_id}",
    response_model=QuestionResponse,
    summary="Get a specific question by ID",
)
async def get_question(
    question_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert_user),
) -> QuestionResponse:
    """Get a specific question by ID."""
    service = ContentService(db)
    question = await service.get_question(question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )
    return question


@router.patch(
    "/questions/{question_id}",
    response_model=QuestionResponse,
    summary="Update a question",
)
async def update_question(
    question_id: UUID,
    update_data: QuestionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert_user),
) -> QuestionResponse:
    """Update a question."""
    service = ContentService(db)
    question = await service.update_question(question_id, update_data)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )
    return question


@router.delete(
    "/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a question",
)
async def delete_question(
    question_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert_user),
) -> None:
    """Delete a question."""
    service = ContentService(db)
    deleted = await service.delete_question(question_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )


@router.post(
    "/questions/bulk",
    response_model=BulkQuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bulk import questions",
)
async def bulk_import_questions(
    bulk_data: BulkQuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert_user),
) -> BulkQuestionResponse:
    """Bulk import questions into a module."""
    service = ContentService(db)
    questions, errors = await service.bulk_create_questions(bulk_data)

    return BulkQuestionResponse(
        imported_count=len(questions),
        imported_ids=[q.id for q in questions],
        errors=errors if errors else None,
    )


# ==================== Knowledge Atom Endpoints ====================

@router.post(
    "/knowledge-atoms",
    response_model=KnowledgeAtomResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a knowledge atom",
)
async def create_knowledge_atom(
    atom_data: KnowledgeAtomCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert_user),
) -> KnowledgeAtomResponse:
    """Create a new knowledge atom for remediation."""
    service = ContentService(db)
    atom = await service.create_knowledge_atom(atom_data)
    return atom


@router.get(
    "/knowledge-atoms",
    response_model=KnowledgeAtomListResponse,
    summary="List knowledge atoms",
)
async def list_knowledge_atoms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    competency_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert_user),
) -> KnowledgeAtomListResponse:
    """List knowledge atoms with optional filtering by competency."""
    service = ContentService(db)
    atoms, total = await service.list_knowledge_atoms(
        skip=skip,
        limit=limit,
        competency_id=competency_id,
    )
    return KnowledgeAtomListResponse(
        items=atoms,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
    )


@router.get(
    "/knowledge-atoms/{atom_id}",
    response_model=KnowledgeAtomResponse,
    summary="Get a specific knowledge atom by ID",
)
async def get_knowledge_atom(
    atom_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert_user),
) -> KnowledgeAtomResponse:
    """Get a specific knowledge atom by ID."""
    service = ContentService(db)
    atom = await service.get_knowledge_atom(atom_id)
    if not atom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge atom not found",
        )
    return atom


@router.patch(
    "/knowledge-atoms/{atom_id}",
    response_model=KnowledgeAtomResponse,
    summary="Update a knowledge atom",
)
async def update_knowledge_atom(
    atom_id: UUID,
    update_data: KnowledgeAtomUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert_user),
) -> KnowledgeAtomResponse:
    """Update a knowledge atom."""
    service = ContentService(db)
    atom = await service.update_knowledge_atom(atom_id, update_data)
    if not atom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge atom not found",
        )
    return atom


@router.delete(
    "/knowledge-atoms/{atom_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a knowledge atom",
)
async def delete_knowledge_atom(
    atom_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_expert_user),
) -> None:
    """Delete a knowledge atom."""
    service = ContentService(db)
    deleted = await service.delete_knowledge_atom(atom_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge atom not found",
        )
