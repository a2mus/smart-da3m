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
    # Idempotently create enum types using PL/pgSQL (IF NOT EXISTS not supported for TYPE in PG)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE userrole AS ENUM ('STUDENT', 'PARENT', 'EXPERT');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE language AS ENUM ('AR', 'FR');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$
    """)

    # Create users table — use sa.Text for enum columns to avoid SQLAlchemy
    # re-emitting the CREATE TYPE DDL through its internal event system.
    # The actual PG column type is enforced via the explicit CREATE TYPE above.
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('hashed_password', sa.String(255), nullable=True),
        sa.Column('pin_code_hash', sa.String(255), nullable=True),
        sa.Column('role', sa.Text(), nullable=False),
        sa.Column('language', sa.Text(), nullable=True),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )

    # Add check constraints to enforce enum values at DB level
    op.execute(
        "ALTER TABLE users ADD CONSTRAINT users_role_check "
        "CHECK (role IN ('STUDENT', 'PARENT', 'EXPERT'))"
    )
    op.execute(
        "ALTER TABLE users ADD CONSTRAINT users_language_check "
        "CHECK (language IN ('AR', 'FR'))"
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
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS language")
