"""
Dashboard Repository for accessing child profiles, competencies, diagnostic sessions, and remediation paths.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.diagnostic import CompetencyProfile, DiagnosticSession, MasteryLevel
from app.models.organization import OrganizationMember
from app.models.remediation import RemediationPath
from app.models.user import User, UserRole
from app.repositories.base import BaseRepository


class DashboardRepo(BaseRepository[User]):
    """Repository encapsulating database operations for the parent dashboard."""

    def __init__(self, db: AsyncSession, tenant_id: Optional[UUID] = None):
        super().__init__(User, db)
        self.tenant_id = tenant_id

    async def get_children_for_parent(self, parent_id: UUID) -> List[User]:
        """Fetch all children belonging to a specific parent within the active tenant scope."""
        query = select(User).where(
            User.parent_id == parent_id,
            User.role == UserRole.STUDENT,
        )
        if self.tenant_id is not None:
            query = query.join(
                OrganizationMember,
                (OrganizationMember.user_id == User.id)
                & (OrganizationMember.organization_id == self.tenant_id),
            )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_child_by_id(self, student_id: UUID) -> Optional[User]:
        """Fetch student user by ID with optional tenant scope."""
        query = select(User).where(
            User.id == student_id,
            User.role == UserRole.STUDENT,
        )
        if self.tenant_id is not None:
            query = query.join(
                OrganizationMember,
                (OrganizationMember.user_id == User.id)
                & (OrganizationMember.organization_id == self.tenant_id),
            )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_child_competency_profiles(
        self, student_id: UUID
    ) -> List[CompetencyProfile]:
        """Fetch competency profiles for a student."""
        query = select(CompetencyProfile).where(
            CompetencyProfile.student_id == student_id
        )
        if self.tenant_id is not None and hasattr(CompetencyProfile, "organization_id"):
            query = query.where(CompetencyProfile.organization_id == self.tenant_id)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_recent_diagnostic_sessions(
        self, student_id: UUID, limit: int = 5
    ) -> List[DiagnosticSession]:
        """Fetch recent diagnostic sessions for a student."""
        query = (
            select(DiagnosticSession)
            .where(DiagnosticSession.student_id == student_id)
            .order_by(DiagnosticSession.started_at.desc())
            .limit(limit)
        )
        if self.tenant_id is not None and hasattr(DiagnosticSession, "organization_id"):
            query = query.where(DiagnosticSession.organization_id == self.tenant_id)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_recent_remediation_paths(
        self, student_id: UUID, limit: int = 5
    ) -> List[RemediationPath]:
        """Fetch recent remediation paths for a student."""
        query = (
            select(RemediationPath)
            .where(RemediationPath.student_id == student_id)
            .order_by(RemediationPath.started_at.desc())
            .limit(limit)
        )
        if self.tenant_id is not None and hasattr(RemediationPath, "organization_id"):
            query = query.where(RemediationPath.organization_id == self.tenant_id)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_latest_failed_competency(
        self, student_id: UUID
    ) -> Optional[CompetencyProfile]:
        """Fetch student's most recently assessed failed/attempted competency profile."""
        query = (
            select(CompetencyProfile)
            .where(
                CompetencyProfile.student_id == student_id,
                CompetencyProfile.mastery_level.in_(
                    [MasteryLevel.NOT_STARTED, MasteryLevel.ATTEMPTED]
                ),
            )
            .order_by(CompetencyProfile.last_assessed.desc())
            .limit(1)
        )
        if self.tenant_id is not None and hasattr(CompetencyProfile, "organization_id"):
            query = query.where(CompetencyProfile.organization_id == self.tenant_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()
