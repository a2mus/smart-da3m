"""
Content Repository for managing modules, questions, and knowledge atoms.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import KnowledgeAtom, Module, ModuleStatus, Question, RemediationType
from app.repositories.base import BaseRepository


class ContentRepository(BaseRepository[Module]):
    """Repository handling database operations for content modules, questions, and knowledge atoms."""

    def __init__(self, db: AsyncSession):
        super().__init__(Module, db)

    # ==================== Module Operations ====================

    async def get_module(self, module_id: UUID) -> Optional[Module]:
        """Get module by ID."""
        return await self.get(module_id)

    async def list_modules(
        self,
        skip: int = 0,
        limit: int = 100,
        subject: Optional[str] = None,
        grade_level: Optional[str] = None,
        status: Optional[ModuleStatus] = None,
    ) -> tuple[List[Module], int]:
        """List modules with filtering and total count."""
        query = select(Module)
        if subject:
            query = query.where(Module.subject == subject)
        if grade_level:
            query = query.where(Module.grade_level == grade_level)
        if status:
            query = query.where(Module.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        result = await self.db.execute(query.offset(skip).limit(limit))
        modules = list(result.scalars().all())
        return modules, total

    # ==================== Question Operations ====================

    async def get_question(self, question_id: UUID) -> Optional[Question]:
        """Get question by ID."""
        result = await self.db.execute(
            select(Question).where(Question.id == question_id)
        )
        return result.scalar_one_or_none()

    async def list_module_questions(
        self, module_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Question]:
        """List all questions for a given module."""
        result = await self.db.execute(
            select(Question)
            .where(Question.module_id == module_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_question(
        self,
        module_id: UUID,
        organization_id: UUID,
        content: dict,
        difficulty_level: int,
        target_misconception_id: Optional[str] = None,
        estimated_time_sec: int = 60,
        is_shared: bool = False,
    ) -> Question:
        """Create a new question record."""
        question = Question(
            module_id=module_id,
            organization_id=organization_id,
            content=content,
            difficulty_level=difficulty_level,
            target_misconception_id=target_misconception_id,
            estimated_time_sec=estimated_time_sec,
            is_shared=is_shared,
        )
        self.db.add(question)
        await self.db.commit()
        await self.db.refresh(question)
        return question

    async def bulk_create_questions(
        self, questions_data: List[dict]
    ) -> List[Question]:
        """Bulk create question records."""
        questions = [Question(**q) for q in questions_data]
        self.db.add_all(questions)
        await self.db.commit()
        for q in questions:
            await self.db.refresh(q)
        return questions

    # ==================== Knowledge Atom Operations ====================

    async def get_knowledge_atom(self, atom_id: UUID) -> Optional[KnowledgeAtom]:
        """Get knowledge atom by ID."""
        result = await self.db.execute(
            select(KnowledgeAtom).where(KnowledgeAtom.id == atom_id)
        )
        return result.scalar_one_or_none()

    async def list_competency_atoms(
        self,
        competency_id: str,
        remediation_type: Optional[RemediationType] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[KnowledgeAtom]:
        """List knowledge atoms for a competency."""
        query = select(KnowledgeAtom).where(KnowledgeAtom.competency_id == competency_id)
        if remediation_type:
            query = query.where(KnowledgeAtom.remediation_type == remediation_type)
        result = await self.db.execute(query.offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create_knowledge_atom(
        self,
        organization_id: UUID,
        competency_id: str,
        remediation_type: RemediationType,
        content: dict,
        is_shared: bool = False,
    ) -> KnowledgeAtom:
        """Create a new knowledge atom."""
        atom = KnowledgeAtom(
            organization_id=organization_id,
            competency_id=competency_id,
            remediation_type=remediation_type,
            content=content,
            is_shared=is_shared,
        )
        self.db.add(atom)
        await self.db.commit()
        await self.db.refresh(atom)
        return atom
