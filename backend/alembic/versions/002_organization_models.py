"""Create organization and organization_members tables and seed system org.

Revision ID: 002_organization_models
Revises: 6721010c96a7
Create Date: 2026-08-01

"""
import uuid
from datetime import datetime, timezone
from alembic import op
import sqlalchemy as sa

revision = '002_organization_models'
down_revision = '6721010c96a7'
branch_labels = None
depends_on = None

SYSTEM_ORG_ID = uuid.UUID('00000000-0000-0000-0000-000000000001')


def upgrade() -> None:
    # Create enum type for organization type if it does not exist
    organizationtype = sa.Enum('SCHOOL', 'HOUSEHOLD', name='organizationtype')
    organizationtype.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'organizations',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', organizationtype, nullable=False),
        sa.Column('is_system_org', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'], unique=False)
    op.create_index(op.f('ix_organizations_type'), 'organizations', ['type'], unique=False)

    userrole = sa.Enum('STUDENT', 'PARENT', 'EXPERT', name='userrole')

    op.create_table(
        'organization_members',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('role', userrole, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organization_members_organization_id'), 'organization_members', ['organization_id'], unique=False)
    op.create_index(op.f('ix_organization_members_role'), 'organization_members', ['role'], unique=False)
    op.create_index(op.f('ix_organization_members_user_id'), 'organization_members', ['user_id'], unique=False)

    # Seed default system organization
    organizations_table = sa.table(
        'organizations',
        sa.column('id', sa.Uuid()),
        sa.column('name', sa.String()),
        sa.column('type', sa.String()),
        sa.column('is_system_org', sa.Boolean()),
        sa.column('created_at', sa.DateTime(timezone=True)),
        sa.column('updated_at', sa.DateTime(timezone=True)),
    )
    now = datetime.now(timezone.utc)
    op.bulk_insert(
        organizations_table,
        [
            {
                'id': SYSTEM_ORG_ID,
                'name': 'System Organization',
                'type': 'SCHOOL',
                'is_system_org': True,
                'created_at': now,
                'updated_at': now,
            }
        ]
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_organization_members_user_id'), table_name='organization_members')
    op.drop_index(op.f('ix_organization_members_role'), table_name='organization_members')
    op.drop_index(op.f('ix_organization_members_organization_id'), table_name='organization_members')
    op.drop_table('organization_members')

    op.drop_index(op.f('ix_organizations_type'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_name'), table_name='organizations')
    op.drop_table('organizations')

    organizationtype = sa.Enum('SCHOOL', 'HOUSEHOLD', name='organizationtype')
    organizationtype.drop(op.get_bind(), checkfirst=True)
