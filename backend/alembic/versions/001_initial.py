"""Initial migration - Create users table

Revision ID: 001_initial
Revises: 
Create Date: 2026-04-11

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create userrole enum
    userrole_enum = sa.Enum('STUDENT', 'PARENT', 'EXPERT', name='userrole')
    userrole_enum.create(op.get_bind(), checkfirst=True)
    
    # Create language enum
    language_enum = sa.Enum('AR', 'FR', name='language')
    language_enum.create(op.get_bind(), checkfirst=True)
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('hashed_password', sa.String(255), nullable=True),
        sa.Column('pin_code_hash', sa.String(255), nullable=True),
        sa.Column('role', sa.Enum('STUDENT', 'PARENT', 'EXPERT', name='userrole'), nullable=False),
        sa.Column('language', sa.Enum('AR', 'FR', name='language'), nullable=True),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Create indexes
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    op.create_index(op.f('ix_users_parent_id'), 'users', ['parent_id'], unique=False)
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_users_role'), table_name='users')
    op.drop_index(op.f('ix_users_parent_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    
    # Drop table
    op.drop_table('users')
    
    # Drop enums
    sa.Enum(name='userrole').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='language').drop(op.get_bind(), checkfirst=True)
