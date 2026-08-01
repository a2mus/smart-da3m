"""Tests for Organization and OrganizationMember models."""

import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization, OrganizationMember, OrganizationType
from app.models.user import User, UserRole


@pytest.mark.asyncio
async def test_organization_model_instantiation():
    """Test Organization model instantiation attributes."""
    org_id = uuid.uuid4()
    org = Organization(
        id=org_id,
        name="École Al Ihsane",
        type=OrganizationType.SCHOOL,
        is_system_org=False,
    )
    assert org.id == org_id
    assert org.name == "École Al Ihsane"
    assert org.type == OrganizationType.SCHOOL
    assert org.is_system_org is False


@pytest.mark.asyncio
async def test_organization_member_model_instantiation():
    """Test OrganizationMember association model instantiation attributes."""
    member_id = uuid.uuid4()
    user_id = uuid.uuid4()
    org_id = uuid.uuid4()
    member = OrganizationMember(
        id=member_id,
        user_id=user_id,
        organization_id=org_id,
        role=UserRole.EXPERT,
    )
    assert member.id == member_id
    assert member.user_id == user_id
    assert member.organization_id == org_id
    assert member.role == UserRole.EXPERT


@pytest.mark.asyncio
async def test_organization_db_persistence(db: AsyncSession):
    """Test persisting Organization and OrganizationMember in the database."""
    org = Organization(
        name="Household Family Test",
        type=OrganizationType.HOUSEHOLD,
        is_system_org=False,
    )
    db.add(org)

    user = User(
        email="parent_org_test@example.com",
        hashed_password="hashed_pw",
        role=UserRole.PARENT,
    )
    db.add(user)
    await db.commit()

    member = OrganizationMember(
        user_id=user.id,
        organization_id=org.id,
        role=UserRole.PARENT,
    )
    db.add(member)
    await db.commit()

    assert org.id is not None
    assert member.id is not None
    assert member.user_id == user.id
    assert member.organization_id == org.id
