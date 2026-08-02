"""
Content service for managing modules, questions, and knowledge atoms delegating to ContentRepository.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import KnowledgeAtom, Module, ModuleStatus, Question
from app.repositories.content_repo import ContentRepository
from app.schemas.content import (
    BulkImportRequest,
    BulkImportResponse,
    BulkImportRowError,
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
            "title": module_data.title,
            "description": module_data.description,
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
        org_id = organization_id or UUID("00000000-0000-0000-0000-000000000000")
        q_kwargs = {
            "module_id": question_data.module_id,
            "organization_id": org_id,
            "content": question_data.content.model_dump(),
            "difficulty_level": question_data.difficulty_level,
            "target_misconception_id": question_data.target_misconception_id,
            "estimated_time_sec": question_data.estimated_time_sec,
        }
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
        update_dict = update_data.model_dump(exclude_unset=True)
        if "content" in update_dict and update_dict["content"] is not None:
            if hasattr(update_dict["content"], "model_dump"):
                update_dict["content"] = update_dict["content"].model_dump()

        return await self.repo.update_question(question_id, **update_dict)

    async def delete_question(self, question_id: UUID) -> bool:
        """Delete a question."""
        return await self.repo.delete_question(question_id)

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
        update_dict = update_data.model_dump(exclude_unset=True)
        if "content" in update_dict and update_dict["content"] is not None:
            if hasattr(update_dict["content"], "model_dump"):
                update_dict["content"] = update_dict["content"].model_dump()

        return await self.repo.update_knowledge_atom(atom_id, **update_dict)

    async def delete_knowledge_atom(self, atom_id: UUID) -> bool:
        """Delete a knowledge atom."""
        return await self.repo.delete_knowledge_atom(atom_id)

    async def bulk_import_content(
        self, payload: BulkImportRequest, organization_id: Optional[UUID] = None
    ) -> BulkImportResponse:
        """Bulk import questions, modules, or knowledge atoms with per-row validation and partial success."""
        created_count = 0
        failed_count = 0
        errors: List[BulkImportRowError] = []

        target_org_id = organization_id or UUID("00000000-0000-0000-0000-000000000000")

        for row_idx, item in enumerate(payload.items, start=1):
            try:
                entity_type = (item.entity_type or "question").lower()
                if entity_type == "question":
                    module_id = item.module_id or item.data.get("module_id")
                    if not module_id:
                        errors.append(BulkImportRowError(row=row_idx, reason="Missing required module_id for question"))
                        failed_count += 1
                        continue

                    question_data = QuestionCreate(
                        module_id=UUID(str(module_id)),
                        content=item.data.get("content", {}),
                        difficulty_level=item.data.get("difficulty_level", 3),
                        target_misconception_id=item.data.get("target_misconception_id"),
                        estimated_time_sec=item.data.get("estimated_time_sec", 60),
                    )

                    await self.repo.create_question(
                        module_id=question_data.module_id,
                        organization_id=target_org_id,
                        content=question_data.content.model_dump(),
                        difficulty_level=question_data.difficulty_level,
                        target_misconception_id=question_data.target_misconception_id,
                        estimated_time_sec=question_data.estimated_time_sec,
                    )
                    created_count += 1

                elif entity_type in ("atom", "knowledge_atom"):
                    atom_data = KnowledgeAtomCreate(
                        competency_id=item.data.get("competency_id", ""),
                        remediation_type=item.data.get("remediation_type", "MICRO_LESSON"),
                        content=item.data.get("content", {}),
                    )
                    await self.repo.create_knowledge_atom(
                        organization_id=target_org_id,
                        competency_id=atom_data.competency_id,
                        remediation_type=atom_data.remediation_type,
                        content=atom_data.content.model_dump(),
                    )
                    created_count += 1

                elif entity_type == "module":
                    mod_data = ModuleCreate(
                        title=item.data.get("title", ""),
                        description=item.data.get("description", ""),
                        subject=item.data.get("subject", "ARABIC"),
                        grade_level=item.data.get("grade_level", "Y1"),
                        domain=item.data.get("domain", ""),
                        competency_id=item.data.get("competency_id", "COMP-01"),
                        status=item.data.get("status", ModuleStatus.DRAFT),
                    )
                    await self.create_module(mod_data, organization_id=target_org_id)
                    created_count += 1
                else:
                    errors.append(BulkImportRowError(row=row_idx, reason=f"Unsupported entity type: {entity_type}"))
                    failed_count += 1
            except Exception as exc:
                failed_count += 1
                errors.append(BulkImportRowError(row=row_idx, reason=str(exc)))

        return BulkImportResponse(
            created=created_count,
            failed=failed_count,
            errors=errors,
        )

