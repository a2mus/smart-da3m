"""Update remediationpathstatus enum with AD-2 state machine states.

Revision ID: 004_update_remediation_path_status_enum
Revises: 003_tenant_scoped_models
Create Date: 2026-08-01

"""
from alembic import op
import sqlalchemy as sa

revision = '004_update_remediation_path_status_enum'
down_revision = '003_tenant_scoped_models'
branch_labels = None
depends_on = None

NEW_STATES = [
    'DIAGNOSED',
    'PROPOSED',
    'VALIDATED',
    'PASSPORT_TESTING',
    'MASTERED',
    'RETIRED',
]


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        for state in NEW_STATES:
            bind.execute(sa.text(f"ALTER TYPE remediationpathstatus ADD VALUE IF NOT EXISTS '{state}'"))


def downgrade() -> None:
    pass
