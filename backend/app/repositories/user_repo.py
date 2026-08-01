"""
User Repository for managing users, organizations, and organization members.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization, OrganizationMember, OrganizationType
from app.models.user import User, UserRole
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository handling database operations for users and organization memberships."""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    # ==================== User Operations ====================

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Fetch user by email address."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Fetch user by ID."""
        return await self.get(user_id)

    async def create_user(
        self,
        role: UserRole,
        email: Optional[str] = None,
        hashed_password: Optional[str] = None,
        pin_code_hash: Optional[str] = None,
        parent_id: Optional[UUID] = None,
    ) -> User:
        """Create a new user record."""
        return await self.create(
            email=email,
            hashed_password=hashed_password,
            pin_code_hash=pin_code_hash,
            role=role,
            parent_id=parent_id,
        )

    # ==================== Organization Operations ====================

    async def get_organization(self, org_id: UUID) -> Optional[Organization]:
        """Fetch organization by ID."""
        result = await self.db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        return result.scalar_one_or_none()

    async def create_organization(
        self, name: str, org_type: OrganizationType, is_system_org: bool = False
    ) -> Organization:
        """Create a new organization."""
        org = Organization(name=name, type=org_type, is_system_org=is_system_org)
        self.db.add(org)
        await self.db.commit()
        await self.db.refresh(org)
        return org

    async def add_organization_member(
        self, user_id: UUID, organization_id: UUID, role: UserRole
    ) -> OrganizationMember:
        """Add a user to an organization with a specific role."""
        member = OrganizationMember(
            user_id=user_id, organization_id=organization_id, role=role
        )
        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)
        return member

    async def get_user_memberships(
        self, user_id: UUID
    ) -> List[OrganizationMember]:
        """Fetch all organization memberships for a user."""
        result = await self.db.execute(
            select(OrganizationMember).where(OrganizationMember.user_id == user_id)
        )
        return list(result.scalars().all())
