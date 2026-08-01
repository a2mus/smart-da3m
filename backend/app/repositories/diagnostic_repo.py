"""
Diagnostic Repository for managing diagnostic sessions, answers, and competency profiles.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.diagnostic import (
    CompetencyProfile,
    DiagnosticAnswer,
    DiagnosticSession,
    DiagnosticSessionStatus,
    ErrorClassification,
    MasteryLevel,
    RemediationGroup,
)
from app.repositories.base import BaseRepository


class DiagnosticRepository(BaseRepository[DiagnosticSession]):
    """Repository handling database operations for diagnostic features."""

    def __init__(self, db: AsyncSession):
        super().__init__(DiagnosticSession, db)

    # ==================== Diagnostic Session ====================

    async def create_session(
        self,
        student_id: UUID,
        module_id: UUID,
        organization_id: UUID,
        status: DiagnosticSessionStatus = DiagnosticSessionStatus.IN_PROGRESS,
    ) -> DiagnosticSession:
        """Create a new diagnostic session."""
        return await self.create(
            student_id=student_id,
            module_id=module_id,
            organization_id=organization_id,
            status=status,
        )

    async def get_session(self, session_id: UUID) -> Optional[DiagnosticSession]:
        """Get a diagnostic session by ID."""
        return await self.get(session_id)

    async def update_session_status(
        self,
        session_id: UUID,
        status: DiagnosticSessionStatus,
        recommended_group: Optional[RemediationGroup] = None,
    ) -> Optional[DiagnosticSession]:
        """Update diagnostic session status and optional recommended group."""
        update_data = {"status": status}
        if recommended_group is not None:
            update_data["recommended_group"] = recommended_group
        return await self.update(session_id, **update_data)

    async def list_student_sessions(
        self, student_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[DiagnosticSession]:
        """List diagnostic sessions for a given student."""
        result = await self.db.execute(
            select(DiagnosticSession)
            .where(DiagnosticSession.student_id == student_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    # ==================== Diagnostic Answer ====================

    async def record_answer(
        self,
        session_id: UUID,
        question_id: UUID,
        organization_id: UUID,
        is_correct: int,
        response_time_ms: int,
        error_classification: ErrorClassification,
    ) -> DiagnosticAnswer:
        """Record a student answer in a diagnostic session."""
        answer = DiagnosticAnswer(
            session_id=session_id,
            question_id=question_id,
            organization_id=organization_id,
            is_correct=is_correct,
            response_time_ms=response_time_ms,
            error_classification=error_classification,
        )
        self.db.add(answer)
        await self.db.commit()
        await self.db.refresh(answer)
        return answer

    async def get_session_answers(
        self, session_id: UUID
    ) -> List[DiagnosticAnswer]:
        """Get all answers submitted for a diagnostic session."""
        result = await self.db.execute(
            select(DiagnosticAnswer).where(DiagnosticAnswer.session_id == session_id)
        )
        return list(result.scalars().all())

    # ==================== Competency Profile ====================

    async def get_competency_profile(
        self, student_id: UUID, competency_id: str
    ) -> Optional[CompetencyProfile]:
        """Get a student's competency profile by student ID and competency ID."""
        result = await self.db.execute(
            select(CompetencyProfile).where(
                CompetencyProfile.student_id == student_id,
                CompetencyProfile.competency_id == competency_id,
            )
        )
        return result.scalar_one_or_none()

    async def update_or_create_competency_profile(
        self,
        student_id: UUID,
        competency_id: str,
        organization_id: UUID,
        p_learned: float,
        mastery_level: MasteryLevel,
    ) -> CompetencyProfile:
        """Create or update a student's competency profile."""
        profile = await self.get_competency_profile(student_id, competency_id)
        if profile:
            profile.p_learned = p_learned
            profile.mastery_level = mastery_level
            await self.db.commit()
            await self.db.refresh(profile)
            return profile

        profile = CompetencyProfile(
            student_id=student_id,
            competency_id=competency_id,
            organization_id=organization_id,
            p_learned=p_learned,
            mastery_level=mastery_level,
        )
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def get_student_competencies(
        self, student_id: UUID
    ) -> List[CompetencyProfile]:
        """Get all competency profiles for a student."""
        result = await self.db.execute(
            select(CompetencyProfile).where(CompetencyProfile.student_id == student_id)
        )
        return list(result.scalars().all())
