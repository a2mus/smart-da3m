"""
Sync Repository for handling idempotent batch offline synchronization of answers and atom completions.
"""

from typing import List, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.engines.diagnostic_engine import DiagnosticEngine
from app.engines.remediation_engine import RemediationEngine
from app.models.content import KnowledgeAtom, Question
from app.models.diagnostic import DiagnosticSessionStatus, ErrorClassification, MasteryLevel
from app.models.remediation import AtomCompletion, RemediationPath
from app.models.user import User
from app.repositories.content_repo import ContentRepository
from app.repositories.diagnostic_repo import DiagnosticRepository
from app.repositories.remediation_repo import RemediationRepository
from app.schemas.sync import SyncAnswerItem, SyncBatchRequest, SyncCompletionItem, SyncErrorDetail


class SyncRepository:
    """Repository handling offline batch sync processing."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.diag_repo = DiagnosticRepository(db)
        self.content_repo = ContentRepository(db)
        self.remed_repo = RemediationRepository(db)

    async def process_batch_sync(
        self,
        current_user: User,
        sync_request: SyncBatchRequest,
    ) -> Tuple[int, int, List[SyncErrorDetail]]:
        """Process batched offline answers and atom completions idempotently.

        Returns:
            Tuple of (accepted_count, rejected_count, error_details)
        """
        accepted = 0
        rejected = 0
        errors: List[SyncErrorDetail] = []

        # 1. Process diagnostic answers
        for item in sync_request.answers:
            try:
                processed = await self._process_answer_item(current_user, item)
                if processed:
                    accepted += 1
                else:
                    rejected += 1
                    errors.append(SyncErrorDetail(id=item.id, reason="Session not found or invalid question"))
            except Exception as e:
                rejected += 1
                errors.append(SyncErrorDetail(id=item.id, reason=str(e)))

        # 2. Process atom completions
        for item in sync_request.completions:
            try:
                processed = await self._process_completion_item(current_user, item)
                if processed:
                    accepted += 1
                else:
                    rejected += 1
                    errors.append(SyncErrorDetail(id=item.id, reason="Knowledge atom or remediation path not found"))
            except Exception as e:
                rejected += 1
                errors.append(SyncErrorDetail(id=item.id, reason=str(e)))

        return accepted, rejected, errors

    async def _process_answer_item(
        self,
        current_user: User,
        item: SyncAnswerItem,
    ) -> bool:
        session = await self.diag_repo.get_session(item.session_id)
        if not session or session.student_id != current_user.id:
            return False

        question = await self.content_repo.get_question(item.question_id)
        if not question:
            return False

        # Idempotency check: if answer already recorded for (session_id, question_id), accept without duplicating BKT update
        existing_answer = await self.diag_repo.get_answer(item.session_id, item.question_id)
        if existing_answer:
            return True

        # Process new answer
        correct_answer = question.content.get("correct_answer", "")
        is_correct = item.answer.strip().lower() == correct_answer.strip().lower()

        module = await self.content_repo.get_module(session.module_id)
        competency_id = module.competency_id if module else "C1"
        org_id = getattr(session, "organization_id", None) or UUID("00000000-0000-0000-0000-000000000000")

        profile = await self.diag_repo.get_competency_profile(current_user.id, competency_id)
        current_p_learned = profile.p_learned if profile else 0.5

        engine = DiagnosticEngine()
        processed = engine.process_answer(
            current_p_learned=current_p_learned,
            is_correct=is_correct,
            response_time_ms=item.time_ms,
            difficulty_level=question.difficulty_level,
            target_misconception_id=question.target_misconception_id,
        )

        new_p_learned = processed["current_mastery"]
        mastery_level_val = processed["mastery_level"]
        error_classification_val = processed["error_classification"]

        await self.diag_repo.update_or_create_competency_profile(
            student_id=current_user.id,
            competency_id=competency_id,
            organization_id=org_id,
            p_learned=new_p_learned,
            mastery_level=MasteryLevel(mastery_level_val),
        )

        await self.diag_repo.record_answer(
            session_id=item.session_id,
            question_id=item.question_id,
            organization_id=org_id,
            is_correct=1 if is_correct else 0,
            response_time_ms=item.time_ms,
            error_classification=ErrorClassification(error_classification_val),
        )

        # Check for completion
        answers = await self.diag_repo.get_session_answers(item.session_id)
        is_complete = engine.is_session_complete(
            answers_count=len(answers),
            current_p_learned=new_p_learned,
        )
        if is_complete and session.status != DiagnosticSessionStatus.COMPLETED:
            await self.diag_repo.update_session_status(
                session.id, DiagnosticSessionStatus.COMPLETED
            )

        return True

    async def _process_completion_item(
        self,
        current_user: User,
        item: SyncCompletionItem,
    ) -> bool:
        result = await self.db.execute(
            select(KnowledgeAtom).where(KnowledgeAtom.id == item.atom_id)
        )
        atom = result.scalar_one_or_none()
        if not atom:
            return False

        result = await self.db.execute(
            select(RemediationPath).where(
                RemediationPath.student_id == current_user.id,
                RemediationPath.competency_id == atom.competency_id,
            )
        )
        path = result.scalar_one_or_none()
        if not path:
            return False

        # Conflict resolution / last-write-wins (idempotent submission)
        res_comp = await self.db.execute(
            select(AtomCompletion).where(
                AtomCompletion.path_id == path.id,
                AtomCompletion.atom_id == item.atom_id,
            )
        )
        existing_completion = res_comp.scalar_one_or_none()

        if not existing_completion:
            completion = AtomCompletion(
                path_id=path.id,
                atom_id=item.atom_id,
                organization_id=path.organization_id,
                time_spent_ms=item.time_spent_ms,
                interactions_count=item.interactions_count,
            )
            self.db.add(completion)

        if path.atoms_completed is None:
            path.atoms_completed = []

        if item.atom_id not in path.atoms_completed:
            path.atoms_completed.append(item.atom_id)

        engine = RemediationEngine()
        new_difficulty = engine.difficulty_adjuster.adjust(
            current_difficulty=path.current_difficulty,
            response_time_ms=item.time_spent_ms,
            is_correct=item.is_correct,
            estimated_time_ms=30000,
        )
        path.current_difficulty = new_difficulty
        await self.db.commit()

        return True
