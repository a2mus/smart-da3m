"""
Content service for managing modules, questions, and knowledge atoms delegating to ContentRepository.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import KnowledgeAtom, Module, ModuleStatus, Question
from app.repositories.content_repo import ContentRepository
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
    """Service for content CRUD operations delegating database operations to ContentRepository."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ContentRepository(db)

    # ==================== Module Operations ====================

    async def create_module(self, module_data: ModuleCreate, organization_id: Optional[UUID] = None) -> Module:
        """Create a new curriculum module."""
        module_kwargs = {
            "subject": module_data.subject,
            "grade_level": module_data.grade_level,
            "domain": module_data.domain,
            "competency_id": module_data.competency_id,
            "status": module_data.status or ModuleStatus.DRAFT,
        }
        if organization_id:
            module_kwargs["organization_id"] = organization_id
        return await self.repo.create(**module_kwargs)

    async def get_module(self, module_id: UUID) -> Optional[Module]:
        """Get a module by ID."""
        return await self.repo.get_module(module_id)

    async def list_modules(
        self,
        skip: int = 0,
        limit: int = 100,
        subject: Optional[str] = None,
        grade_level: Optional[str] = None,
        status: Optional[ModuleStatus] = None,
    ) -> tuple[List[Module], int]:
        """List modules with optional filtering."""
        return await self.repo.list_modules(
            skip=skip, limit=limit, subject=subject, grade_level=grade_level, status=status
        )

    async def update_module(
        self, module_id: UUID, update_data: ModuleUpdate
    ) -> Optional[Module]:
        """Update a module."""
        update_dict = update_data.model_dump(exclude_unset=True)
        return await self.repo.update(module_id, **update_dict)

    async def delete_module(self, module_id: UUID) -> bool:
        """Delete a module."""
        return await self.repo.delete(module_id)

    # ==================== Question Operations ====================

    async def create_question(self, question_data: QuestionCreate, organization_id: Optional[UUID] = None) -> Question:
        """Create a new question."""
        q_kwargs = {
            "module_id": question_data.module_id,
            "content": question_data.content.model_dump(),
            "difficulty_level": question_data.difficulty_level,
            "target_misconception_id": question_data.target_misconception_id,
            "estimated_time_sec": question_data.estimated_time_sec,
        }
        if organization_id:
            q_kwargs["organization_id"] = organization_id
        return await self.repo.create_question(**q_kwargs)

    async def get_question(self, question_id: UUID) -> Optional[Question]:
        """Get a question by ID."""
        return await self.repo.get_question(question_id)

    async def list_questions(
        self,
        skip: int = 0,
        limit: int = 100,
        module_id: Optional[UUID] = None,
        difficulty_level: Optional[int] = None,
    ) -> tuple[List[Question], int]:
        """List questions with optional filtering."""
        if module_id:
            questions = await self.repo.list_module_questions(module_id, skip=skip, limit=limit)
            return questions, len(questions)
        modules, total = await self.repo.list_modules(skip=skip, limit=limit)
        all_q: List[Question] = []
        for m in modules:
            q_list = await self.repo.list_module_questions(m.id)
            all_q.extend(q_list)
        return all_q[:limit], len(all_q)

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
        return await self.repo.delete(question_id)

    async def bulk_create_questions(
        self, bulk_data: BulkQuestionCreate, organization_id: Optional[UUID] = None
    ) -> tuple[List[Question], List[dict]]:
        """Bulk create questions."""
        q_dicts = []
        for qd in bulk_data.questions:
            qd_dict = {
                "module_id": bulk_data.module_id,
                "content": qd.content.model_dump(),
                "difficulty_level": qd.difficulty_level,
                "target_misconception_id": qd.target_misconception_id,
                "estimated_time_sec": qd.estimated_time_sec,
            }
            if organization_id:
                qd_dict["organization_id"] = organization_id
            q_dicts.append(qd_dict)

        try:
            questions = await self.repo.bulk_create_questions(q_dicts)
            return questions, []
        except Exception as e:
            return [], [{"index": 0, "error": str(e)}]

    # ==================== Knowledge Atom Operations ====================

    async def create_knowledge_atom(
        self, atom_data: KnowledgeAtomCreate, organization_id: Optional[UUID] = None
    ) -> KnowledgeAtom:
        """Create a new knowledge atom."""
        return await self.repo.create_knowledge_atom(
            organization_id=organization_id or UUID("00000000-0000-0000-0000-000000000000"),
            competency_id=atom_data.competency_id,
            remediation_type=atom_data.remediation_type,
            content=atom_data.content.model_dump(),
        )

    async def get_knowledge_atom(self, atom_id: UUID) -> Optional[KnowledgeAtom]:
        """Get a knowledge atom by ID."""
        return await self.repo.get_knowledge_atom(atom_id)

    async def list_knowledge_atoms(
        self,
        skip: int = 0,
        limit: int = 100,
        competency_id: Optional[str] = None,
    ) -> tuple[List[KnowledgeAtom], int]:
        """List knowledge atoms with optional filtering."""
        if competency_id:
            atoms = await self.repo.list_competency_atoms(competency_id, skip=skip, limit=limit)
            return atoms, len(atoms)
        atoms_res = await self.repo.db.execute(
            select(KnowledgeAtom).offset(skip).limit(limit)
        )
        atoms_list = list(atoms_res.scalars().all())
        return atoms_list, len(atoms_list)

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
