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
from app.schemas.analytics import HeatmapFilters


class AnalyticsRepo(BaseRepository[CompetencyProfile]):
    """Repository encapsulating database operations for analytics and heatmaps."""

    def __init__(self, db: AsyncSession):
        super().__init__(CompetencyProfile, db)

    async def get_heatmap_data(
        self,
        organization_id: Optional[UUID],
        module_id: Optional[UUID] = None,
        filters: Optional[HeatmapFilters] = None,
    ) -> List[CompetencyProfile]:
        """
        Fetch competency profiles for students within an organization,
        optionally filtered by module_id or HeatmapFilters.
        """
        query = select(CompetencyProfile)
        if organization_id is not None:
            query = query.where(CompetencyProfile.organization_id == organization_id)

        if module_id is not None:
            student_ids_subquery = select(DiagnosticSession.student_id).where(
                DiagnosticSession.module_id == module_id,
            )
            if organization_id is not None:
                student_ids_subquery = student_ids_subquery.where(
                    DiagnosticSession.organization_id == organization_id
                )
            student_ids_subquery = student_ids_subquery.distinct()
            query = query.where(CompetencyProfile.student_id.in_(student_ids_subquery))

        if filters:
            if filters.student_ids:
                query = query.where(CompetencyProfile.student_id.in_(filters.student_ids))
            if filters.competency_ids:
                query = query.where(CompetencyProfile.competency_id.in_(filters.competency_ids))

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_students_for_heatmap(
        self,
        organization_id: Optional[UUID],
        module_id: Optional[UUID] = None,
        filters: Optional[HeatmapFilters] = None,
    ) -> List[User]:
        """
        Fetch student users within an organization,
        optionally filtered by module_id or HeatmapFilters.
        """
        query = (
            select(User)
            .join(OrganizationMember, OrganizationMember.user_id == User.id)
            .where(
                OrganizationMember.role == UserRole.STUDENT,
            )
        )
        if organization_id is not None:
            query = query.where(OrganizationMember.organization_id == organization_id)

        if module_id is not None:
            student_ids_subquery = select(DiagnosticSession.student_id).where(
                DiagnosticSession.module_id == module_id,
            )
            if organization_id is not None:
                student_ids_subquery = student_ids_subquery.where(
                    DiagnosticSession.organization_id == organization_id
                )
            student_ids_subquery = student_ids_subquery.distinct()
            query = query.where(User.id.in_(student_ids_subquery))

        if filters and filters.student_ids:
            query = query.where(User.id.in_(filters.student_ids))

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_auto_group_data(
        self,
        organization_id: Optional[UUID],
        student_ids: Optional[List[UUID]] = None,
        competency_ids: Optional[List[str]] = None,
    ) -> List[CompetencyProfile]:
        """
        Fetch unmastered competency profiles (NOT_STARTED, ATTEMPTED) for students
        in the given organization.
        """
        query = select(CompetencyProfile).where(
            CompetencyProfile.mastery_level.in_(
                [MasteryLevel.NOT_STARTED, MasteryLevel.ATTEMPTED]
            ),
        )
        if organization_id is not None:
            query = query.where(CompetencyProfile.organization_id == organization_id)

        if student_ids:
            query = query.where(CompetencyProfile.student_id.in_(student_ids))

        if competency_ids:
            query = query.where(CompetencyProfile.competency_id.in_(competency_ids))

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_remediation_cards_data(
        self,
        organization_id: Optional[UUID],
        student_id: Optional[UUID] = None,
        student_ids: Optional[List[UUID]] = None,
    ) -> List[CompetencyProfile]:
        query = select(CompetencyProfile).where(
            CompetencyProfile.mastery_level.in_(
                [MasteryLevel.NOT_STARTED, MasteryLevel.ATTEMPTED]
            ),
        )
        if organization_id is not None:
            query = query.where(CompetencyProfile.organization_id == organization_id)

        if student_id is not None:
            query = query.where(CompetencyProfile.student_id == student_id)
        elif student_ids:
            query = query.where(CompetencyProfile.student_id.in_(student_ids))

        result = await self.db.execute(query)
        return list(result.scalars().all())
