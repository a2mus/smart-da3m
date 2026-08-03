"""
Analytics Repository for competency heatmap data querying.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.diagnostic import CompetencyProfile, DiagnosticSession, MasteryLevel
from app.models.organization import OrganizationMember
from app.models.user import User, UserRole
from app.repositories.base import BaseRepository


class AnalyticsRepo(BaseRepository[CompetencyProfile]):
    """Repository encapsulating database operations for analytics and heatmaps."""

    def __init__(self, db: AsyncSession):
        super().__init__(CompetencyProfile, db)

    async def get_heatmap_data(
        self, organization_id: UUID, module_id: Optional[UUID] = None
    ) -> List[CompetencyProfile]:
        """
        Fetch competency profiles for students within an organization,
        optionally filtered by module_id.
        """
        query = select(CompetencyProfile).where(
            CompetencyProfile.organization_id == organization_id
        )

        if module_id is not None:
            student_ids_subquery = (
                select(DiagnosticSession.student_id)
                .where(
                    DiagnosticSession.organization_id == organization_id,
                    DiagnosticSession.module_id == module_id,
                )
                .distinct()
            )
            query = query.where(CompetencyProfile.student_id.in_(student_ids_subquery))

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_students_for_heatmap(
        self, organization_id: UUID, module_id: Optional[UUID] = None
    ) -> List[User]:
        """
        Fetch student users within an organization,
        optionally filtered by module_id.
        """
        query = (
            select(User)
            .join(OrganizationMember, OrganizationMember.user_id == User.id)
            .where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.role == UserRole.STUDENT,
            )
        )

        if module_id is not None:
            student_ids_subquery = (
                select(DiagnosticSession.student_id)
                .where(
                    DiagnosticSession.organization_id == organization_id,
                    DiagnosticSession.module_id == module_id,
                )
                .distinct()
            )
            query = query.where(User.id.in_(student_ids_subquery))

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_auto_group_data(
        self,
        organization_id: UUID,
        student_ids: Optional[List[UUID]] = None,
        competency_ids: Optional[List[str]] = None,
    ) -> List[CompetencyProfile]:
        """
        Fetch unmastered competency profiles (NOT_STARTED, ATTEMPTED) for students
        in the given organization.
        """
        query = select(CompetencyProfile).where(
            CompetencyProfile.organization_id == organization_id,
            CompetencyProfile.mastery_level.in_(
                [MasteryLevel.NOT_STARTED, MasteryLevel.ATTEMPTED]
            ),
        )

        if student_ids:
            query = query.where(CompetencyProfile.student_id.in_(student_ids))

        if competency_ids:
            query = query.where(CompetencyProfile.competency_id.in_(competency_ids))

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_remediation_card_data(
        self,
        organization_id: UUID,
        student_id: Optional[UUID] = None,
        group_id: Optional[str] = None,
    ) -> List[User]:
        """
        Fetch students and their unmastered competencies for remediation cards.
        """
        query = (
            select(User)
            .join(OrganizationMember, OrganizationMember.user_id == User.id)
            .where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.role == UserRole.STUDENT,
            )
        )

        if student_id is not None:
            query = query.where(User.id == student_id)

        result = await self.db.execute(query)
        return list(result.scalars().all())
