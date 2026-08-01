"""
Remediation Repository for managing learning pathways, atom completions, and passport assessments.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.remediation import AtomCompletion, PassportAssessment, RemediationPath, RemediationPathStatus
from app.repositories.base import BaseRepository
from app.services.remediation_service import validate_transition


class RemediationRepository(BaseRepository[RemediationPath]):
    """Repository handling database operations for remediation paths, completions, and assessments."""

    def __init__(self, db: AsyncSession):
        super().__init__(RemediationPath, db)

    # ==================== Remediation Path Operations ====================

    async def update_path_status(
        self, path_id: UUID, target_status: RemediationPathStatus
    ) -> Optional[RemediationPath]:
        """Update remediation path status after enforcing transition guard."""
        path = await self.get_path(path_id)
        if not path:
            return None

        # Enforce state machine guard
        validate_transition(path.status, target_status)

        path.status = target_status
        await self.db.commit()
        await self.db.refresh(path)
        return path

    async def create_path(
        self,
        student_id: UUID,
        competency_id: str,
        organization_id: UUID,
        status: RemediationPathStatus = RemediationPathStatus.IN_PROGRESS,
        current_difficulty: int = 5,
    ) -> RemediationPath:
        """Create a new remediation path."""
        return await self.create(
            student_id=student_id,
            competency_id=competency_id,
            organization_id=organization_id,
            status=status,
            current_difficulty=current_difficulty,
            atoms_completed=[],
        )

    async def get_path(self, path_id: UUID) -> Optional[RemediationPath]:
        """Get remediation path by ID."""
        return await self.get(path_id)

    async def get_active_student_path(
        self, student_id: UUID, competency_id: str
    ) -> Optional[RemediationPath]:
        """Get currently active remediation path for a student and competency."""
        result = await self.db.execute(
            select(RemediationPath).where(
                RemediationPath.student_id == student_id,
                RemediationPath.competency_id == competency_id,
                RemediationPath.status == RemediationPathStatus.IN_PROGRESS,
            )
        )
        return result.scalar_one_or_none()

    async def list_student_paths(
        self, student_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[RemediationPath]:
        """List remediation paths for a student."""
        result = await self.db.execute(
            select(RemediationPath)
            .where(RemediationPath.student_id == student_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    # ==================== Atom Completion Operations ====================

    async def record_atom_completion(
        self,
        path_id: UUID,
        atom_id: UUID,
        organization_id: UUID,
        time_spent_ms: int,
        interactions_count: int = 1,
    ) -> AtomCompletion:
        """Record atom completion for a student's remediation path."""
        completion = AtomCompletion(
            path_id=path_id,
            atom_id=atom_id,
            organization_id=organization_id,
            time_spent_ms=time_spent_ms,
            interactions_count=interactions_count,
        )
        self.db.add(completion)

        # Update atoms_completed JSON on RemediationPath
        path = await self.get_path(path_id)
        if path:
            current_completed = list(path.atoms_completed or [])
            atom_str = str(atom_id)
            if atom_str not in current_completed:
                current_completed.append(atom_str)
                path.atoms_completed = current_completed

        await self.db.commit()
        await self.db.refresh(completion)
        return completion

    async def get_path_completions(self, path_id: UUID) -> List[AtomCompletion]:
        """Get all atom completions for a remediation path."""
        result = await self.db.execute(
            select(AtomCompletion).where(AtomCompletion.path_id == path_id)
        )
        return list(result.scalars().all())

    # ==================== Passport Assessment Operations ====================

    async def create_passport_assessment(
        self,
        student_id: UUID,
        competency_id: str,
        organization_id: UUID,
    ) -> PassportAssessment:
        """Create a new passport assessment attempt."""
        assessment = PassportAssessment(
            student_id=student_id,
            competency_id=competency_id,
            organization_id=organization_id,
        )
        self.db.add(assessment)
        await self.db.commit()
        await self.db.refresh(assessment)
        return assessment

    async def record_passport_result(
        self,
        assessment_id: UUID,
        passed: int,
        accuracy: int,
        questions_answered: int,
        correct_answers: int,
    ) -> Optional[PassportAssessment]:
        """Record final results for a passport assessment attempt."""
        result = await self.db.execute(
            select(PassportAssessment).where(PassportAssessment.id == assessment_id)
        )
        assessment = result.scalar_one_or_none()
        if not assessment:
            return None

        assessment.passed = passed
        assessment.accuracy = accuracy
        assessment.questions_answered = questions_answered
        assessment.correct_answers = correct_answers
        await self.db.commit()
        await self.db.refresh(assessment)
        return assessment
