"""
Diagnostic Repository for managing diagnostic sessions, answers, and competency profiles.
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.engines.spaced_repetition import SpacedRepetitionScheduler
from app.models.diagnostic import (
    CompetencyProfile,
    DiagnosticAnswer,
    DiagnosticSession,
    DiagnosticSessionStatus,
    ErrorClassification,
    MasteryLevel,
    RemediationGroup,
)
from app.models.spaced_repetition import SpacedRepetition
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

    # ==================== Spaced Repetition (FR-16) ====================

    async def get_spaced_repetition_item(
        self, student_id: UUID, question_id: UUID, organization_id: UUID
    ) -> Optional[SpacedRepetition]:
        """Get a specific spaced repetition record for a student and question."""
        result = await self.db.execute(
            select(SpacedRepetition).where(
                SpacedRepetition.student_id == student_id,
                SpacedRepetition.question_id == question_id,
                SpacedRepetition.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def record_failed_item(
        self,
        student_id: UUID,
        question_id: UUID,
        organization_id: UUID,
        now: Optional[datetime] = None,
    ) -> SpacedRepetition:
        """Record or reset a failed item for spaced re-surfacing."""
        current_time = now or datetime.now(timezone.utc)
        scheduler = SpacedRepetitionScheduler()
        next_date, interval, ease = scheduler.calculate_next_review(
            current_interval=1, ease_factor=2.5, is_correct=False, current_time=current_time
        )

        item = await self.get_spaced_repetition_item(student_id, question_id, organization_id)
        if item:
            item.next_review_date = next_date
            item.interval_days = interval
            item.ease_factor = ease
            await self.db.commit()
            await self.db.refresh(item)
            return item

        item = SpacedRepetition(
            student_id=student_id,
            question_id=question_id,
            organization_id=organization_id,
            next_review_date=next_date,
            interval_days=interval,
            ease_factor=ease,
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def get_due_spaced_repetition_items(
        self,
        student_id: UUID,
        organization_id: UUID,
        now: Optional[datetime] = None,
    ) -> List[SpacedRepetition]:
        """Get all due spaced repetition items for a student."""
        current_time = now or datetime.now(timezone.utc)
        result = await self.db.execute(
            select(SpacedRepetition).where(
                SpacedRepetition.student_id == student_id,
                SpacedRepetition.organization_id == organization_id,
                SpacedRepetition.next_review_date <= current_time,
            )
        )
        return list(result.scalars().all())

    async def record_spaced_repetition_answer(
        self,
        student_id: UUID,
        question_id: UUID,
        organization_id: UUID,
        is_correct: bool,
        now: Optional[datetime] = None,
    ) -> Optional[SpacedRepetition]:
        """Update spaced repetition item based on answer correctness."""
        current_time = now or datetime.now(timezone.utc)
        item = await self.get_spaced_repetition_item(student_id, question_id, organization_id)
        if not item:
            if not is_correct:
                return await self.record_failed_item(student_id, question_id, organization_id, current_time)
            return None

        scheduler = SpacedRepetitionScheduler()
        next_date, interval, ease = scheduler.calculate_next_review(
            current_interval=item.interval_days,
            ease_factor=item.ease_factor,
            is_correct=is_correct,
            current_time=current_time,
        )

        item.next_review_date = next_date
        item.interval_days = interval
        item.ease_factor = ease
        await self.db.commit()
        await self.db.refresh(item)
        return item
