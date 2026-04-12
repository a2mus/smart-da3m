"""
Content service for managing modules, questions, and knowledge atoms.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import KnowledgeAtom, Module, ModuleStatus, Question
from app.schemas.content import (
    BulkQuestionCreate,
    KnowledgeAtomCreate,
    KnowledgeAtomUpdate,
    ModuleCreate,
    ModuleUpdate,
    QuestionCreate,
    QuestionUpdate,
)


class ContentService:
    """Service for content CRUD operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== Module Operations ====================

    async def create_module(self, module_data: ModuleCreate) -> Module:
        """Create a new curriculum module."""
        module = Module(
            subject=module_data.subject,
            grade_level=module_data.grade_level,
            domain=module_data.domain,
            competency_id=module_data.competency_id,
            status=module_data.status or ModuleStatus.DRAFT,
        )
        self.db.add(module)
        await self.db.commit()
        await self.db.refresh(module)
        return module

    async def get_module(self, module_id: UUID) -> Optional[Module]:
        """Get a module by ID."""
        result = await self.db.execute(
            select(Module).where(Module.id == module_id)
        )
        return result.scalar_one_or_none()

    async def list_modules(
        self,
        skip: int = 0,
        limit: int = 100,
        subject: Optional[str] = None,
        grade_level: Optional[str] = None,
        status: Optional[ModuleStatus] = None,
    ) -> tuple[List[Module], int]:
        """List modules with optional filtering."""
        query = select(Module)

        if subject:
            query = query.where(Module.subject == subject)
        if grade_level:
            query = query.where(Module.grade_level == grade_level)
        if status:
            query = query.where(Module.status == status)

        # Get total count
        count_result = await self.db.execute(
            select(select(Module).subquery().c.id)
        )
        total = len(count_result.all())

        # Get paginated results
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        modules = result.scalars().all()

        return list(modules), total

    async def update_module(
        self, module_id: UUID, update_data: ModuleUpdate
    ) -> Optional[Module]:
        """Update a module."""
        module = await self.get_module(module_id)
        if not module:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(module, field, value)

        await self.db.commit()
        await self.db.refresh(module)
        return module

    async def delete_module(self, module_id: UUID) -> bool:
        """Delete a module."""
        module = await self.get_module(module_id)
        if not module:
            return False

        await self.db.delete(module)
        await self.db.commit()
        return True

    # ==================== Question Operations ====================

    async def create_question(self, question_data: QuestionCreate) -> Question:
        """Create a new question."""
        question = Question(
            module_id=question_data.module_id,
            content=question_data.content.model_dump(),
            difficulty_level=question_data.difficulty_level,
            target_misconception_id=question_data.target_misconception_id,
            estimated_time_sec=question_data.estimated_time_sec,
        )
        self.db.add(question)
        await self.db.commit()
        await self.db.refresh(question)
        return question

    async def get_question(self, question_id: UUID) -> Optional[Question]:
        """Get a question by ID."""
        result = await self.db.execute(
            select(Question).where(Question.id == question_id)
        )
        return result.scalar_one_or_none()

    async def list_questions(
        self,
        skip: int = 0,
        limit: int = 100,
        module_id: Optional[UUID] = None,
        difficulty_level: Optional[int] = None,
    ) -> tuple[List[Question], int]:
        """List questions with optional filtering."""
        query = select(Question)

        if module_id:
            query = query.where(Question.module_id == module_id)
        if difficulty_level:
            query = query.where(Question.difficulty_level == difficulty_level)

        # Get total count
        count_query = select(Question)
        if module_id:
            count_query = count_query.where(Question.module_id == module_id)
        count_result = await self.db.execute(count_query)
        total = len(count_result.all())

        # Get paginated results
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        questions = result.scalars().all()

        return list(questions), total

    async def update_question(
        self, question_id: UUID, update_data: QuestionUpdate
    ) -> Optional[Question]:
        """Update a question."""
        question = await self.get_question(question_id)
        if not question:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        if "content" in update_dict and update_dict["content"]:
            update_dict["content"] = update_dict["content"].model_dump()

        for field, value in update_dict.items():
            setattr(question, field, value)

        await self.db.commit()
        await self.db.refresh(question)
        return question

    async def delete_question(self, question_id: UUID) -> bool:
        """Delete a question."""
        question = await self.get_question(question_id)
        if not question:
            return False

        await self.db.delete(question)
        await self.db.commit()
        return True

    async def bulk_create_questions(
        self, bulk_data: BulkQuestionCreate
    ) -> tuple[List[Question], List[dict]]:
        """Bulk create questions."""
        questions = []
        errors = []

        for idx, question_data in enumerate(bulk_data.questions):
            try:
                question = Question(
                    module_id=bulk_data.module_id,
                    content=question_data.content.model_dump(),
                    difficulty_level=question_data.difficulty_level,
                    target_misconception_id=question_data.target_misconception_id,
                    estimated_time_sec=question_data.estimated_time_sec,
                )
                self.db.add(question)
                questions.append(question)
            except Exception as e:
                errors.append({"index": idx, "error": str(e)})

        await self.db.commit()
        for question in questions:
            await self.db.refresh(question)

        return questions, errors

    # ==================== Knowledge Atom Operations ====================

    async def create_knowledge_atom(
        self, atom_data: KnowledgeAtomCreate
    ) -> KnowledgeAtom:
        """Create a new knowledge atom."""
        atom = KnowledgeAtom(
            competency_id=atom_data.competency_id,
            remediation_type=atom_data.remediation_type,
            content=atom_data.content.model_dump(),
        )
        self.db.add(atom)
        await self.db.commit()
        await self.db.refresh(atom)
        return atom

    async def get_knowledge_atom(self, atom_id: UUID) -> Optional[KnowledgeAtom]:
        """Get a knowledge atom by ID."""
        result = await self.db.execute(
            select(KnowledgeAtom).where(KnowledgeAtom.id == atom_id)
        )
        return result.scalar_one_or_none()

    async def list_knowledge_atoms(
        self,
        skip: int = 0,
        limit: int = 100,
        competency_id: Optional[str] = None,
    ) -> tuple[List[KnowledgeAtom], int]:
        """List knowledge atoms with optional filtering."""
        query = select(KnowledgeAtom)

        if competency_id:
            query = query.where(KnowledgeAtom.competency_id == competency_id)

        # Get total count
        count_query = select(KnowledgeAtom)
        if competency_id:
            count_query = count_query.where(
                KnowledgeAtom.competency_id == competency_id
            )
        count_result = await self.db.execute(count_query)
        total = len(count_result.all())

        # Get paginated results
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        atoms = result.scalars().all()

        return list(atoms), total

    async def update_knowledge_atom(
        self, atom_id: UUID, update_data: KnowledgeAtomUpdate
    ) -> Optional[KnowledgeAtom]:
        """Update a knowledge atom."""
        atom = await self.get_knowledge_atom(atom_id)
        if not atom:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        if "content" in update_dict and update_dict["content"]:
            update_dict["content"] = update_dict["content"].model_dump()

        for field, value in update_dict.items():
            setattr(atom, field, value)

        await self.db.commit()
        await self.db.refresh(atom)
        return atom

    async def delete_knowledge_atom(self, atom_id: UUID) -> bool:
        """Delete a knowledge atom."""
        atom = await self.get_knowledge_atom(atom_id)
        if not atom:
            return False

        await self.db.delete(atom)
        await self.db.commit()
        return True
