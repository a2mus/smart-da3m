"""Add organization_id FK and create remaining 11 tenant-scoped domain tables.

Revision ID: 003_tenant_scoped_models
Revises: 002_organization_models
Create Date: 2026-08-01

"""
from alembic import op
import sqlalchemy as sa

revision = '003_tenant_scoped_models'
down_revision = '002_organization_models'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enum definitions
    modulestatus = sa.Enum('DRAFT', 'PUBLISHED', name='modulestatus')
    remediationtype = sa.Enum('AUDIO_VISUAL', 'SIMULATION', 'MIND_MAP', name='remediationtype')
    diagnosticsessionstatus = sa.Enum('IN_PROGRESS', 'COMPLETED', 'ABANDONED', name='diagnosticsessionstatus')
    remediationgroup = sa.Enum('A', 'B', 'C', name='remediationgroup')
    errorclassification = sa.Enum('RESOURCE', 'PROCESS', 'INCIDENTAL', 'NONE', name='errorclassification')
    masterylevel = sa.Enum('NOT_STARTED', 'ATTEMPTED', 'FAMILIAR', 'PROFICIENT', 'MASTERED', name='masterylevel')
    remediationpathstatus = sa.Enum('IN_PROGRESS', 'COMPLETED', 'FAILED', 'ABANDONED', name='remediationpathstatus')
    alertseverity = sa.Enum('INFO', 'WARNING', 'CRITICAL', name='alertseverity')
    alerttriggertype = sa.Enum('REPEATED_FAILURE', 'FRUSTRATION', 'PASSPORT_FAILED', 'INACTIVITY', 'ABANDONMENT', name='alerttriggertype')
    alertstatus = sa.Enum('UNREAD', 'READ', 'RESOLVED', 'DISMISSED', name='alertstatus')

    modulestatus.create(op.get_bind(), checkfirst=True)
    remediationtype.create(op.get_bind(), checkfirst=True)
    diagnosticsessionstatus.create(op.get_bind(), checkfirst=True)
    remediationgroup.create(op.get_bind(), checkfirst=True)
    errorclassification.create(op.get_bind(), checkfirst=True)
    masterylevel.create(op.get_bind(), checkfirst=True)
    remediationpathstatus.create(op.get_bind(), checkfirst=True)
    alertseverity.create(op.get_bind(), checkfirst=True)
    alerttriggertype.create(op.get_bind(), checkfirst=True)
    alertstatus.create(op.get_bind(), checkfirst=True)

    # 1. modules
    op.create_table(
        'modules',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('subject', sa.String(length=100), nullable=False),
        sa.Column('grade_level', sa.String(length=50), nullable=False),
        sa.Column('domain', sa.String(length=200), nullable=False),
        sa.Column('competency_id', sa.String(length=50), nullable=False),
        sa.Column('status', modulestatus, nullable=False, server_default='DRAFT'),
        sa.Column('is_shared', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_modules_organization_id'), 'modules', ['organization_id'], unique=False)
    op.create_index(op.f('ix_modules_subject'), 'modules', ['subject'], unique=False)
    op.create_index(op.f('ix_modules_grade_level'), 'modules', ['grade_level'], unique=False)
    op.create_index(op.f('ix_modules_competency_id'), 'modules', ['competency_id'], unique=False)
    op.create_index(op.f('ix_modules_status'), 'modules', ['status'], unique=False)

    # 2. questions
    op.create_table(
        'questions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('module_id', sa.Uuid(), nullable=False),
        sa.Column('content', sa.JSON(), nullable=False),
        sa.Column('difficulty_level', sa.Integer(), nullable=False),
        sa.Column('target_misconception_id', sa.String(length=50), nullable=True),
        sa.Column('estimated_time_sec', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('is_shared', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_questions_organization_id'), 'questions', ['organization_id'], unique=False)
    op.create_index(op.f('ix_questions_target_misconception_id'), 'questions', ['target_misconception_id'], unique=False)

    # 3. knowledge_atoms
    op.create_table(
        'knowledge_atoms',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('competency_id', sa.String(length=50), nullable=False),
        sa.Column('remediation_type', remediationtype, nullable=False),
        sa.Column('content', sa.JSON(), nullable=False),
        sa.Column('is_shared', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_knowledge_atoms_organization_id'), 'knowledge_atoms', ['organization_id'], unique=False)
    op.create_index(op.f('ix_knowledge_atoms_competency_id'), 'knowledge_atoms', ['competency_id'], unique=False)

    # 4. diagnostic_sessions
    op.create_table(
        'diagnostic_sessions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('student_id', sa.Uuid(), nullable=False),
        sa.Column('module_id', sa.Uuid(), nullable=False),
        sa.Column('status', diagnosticsessionstatus, nullable=False, server_default='IN_PROGRESS'),
        sa.Column('recommended_group', remediationgroup, nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_diagnostic_sessions_organization_id'), 'diagnostic_sessions', ['organization_id'], unique=False)

    # 5. diagnostic_answers
    op.create_table(
        'diagnostic_answers',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('session_id', sa.Uuid(), nullable=False),
        sa.Column('question_id', sa.Uuid(), nullable=False),
        sa.Column('is_correct', sa.Integer(), nullable=False),
        sa.Column('response_time_ms', sa.Integer(), nullable=False),
        sa.Column('error_classification', errorclassification, nullable=False),
        sa.Column('answered_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['diagnostic_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_diagnostic_answers_organization_id'), 'diagnostic_answers', ['organization_id'], unique=False)

    # 6. competency_profiles
    op.create_table(
        'competency_profiles',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('student_id', sa.Uuid(), nullable=False),
        sa.Column('competency_id', sa.String(length=50), nullable=False),
        sa.Column('mastery_level', masterylevel, nullable=True, server_default='NOT_STARTED'),
        sa.Column('p_learned', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('last_assessed', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_competency_profiles_organization_id'), 'competency_profiles', ['organization_id'], unique=False)
    op.create_index(op.f('ix_competency_profiles_competency_id'), 'competency_profiles', ['competency_id'], unique=False)

    # 7. remediation_paths
    op.create_table(
        'remediation_paths',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('student_id', sa.Uuid(), nullable=False),
        sa.Column('competency_id', sa.String(length=50), nullable=False),
        sa.Column('status', remediationpathstatus, nullable=False, server_default='IN_PROGRESS'),
        sa.Column('atoms_completed', sa.JSON(), nullable=True),
        sa.Column('current_difficulty', sa.Integer(), nullable=True, server_default='5'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_remediation_paths_organization_id'), 'remediation_paths', ['organization_id'], unique=False)
    op.create_index(op.f('ix_remediation_paths_competency_id'), 'remediation_paths', ['competency_id'], unique=False)

    # 8. atom_completions
    op.create_table(
        'atom_completions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('path_id', sa.Uuid(), nullable=False),
        sa.Column('atom_id', sa.Uuid(), nullable=False),
        sa.Column('time_spent_ms', sa.Integer(), nullable=False),
        sa.Column('interactions_count', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['atom_id'], ['knowledge_atoms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['path_id'], ['remediation_paths.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_atom_completions_organization_id'), 'atom_completions', ['organization_id'], unique=False)

    # 9. passport_assessments
    op.create_table(
        'passport_assessments',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('student_id', sa.Uuid(), nullable=False),
        sa.Column('competency_id', sa.String(length=50), nullable=False),
        sa.Column('passed', sa.Integer(), nullable=True),
        sa.Column('accuracy', sa.Integer(), nullable=True),
        sa.Column('questions_answered', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('correct_answers', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_passport_assessments_organization_id'), 'passport_assessments', ['organization_id'], unique=False)
    op.create_index(op.f('ix_passport_assessments_competency_id'), 'passport_assessments', ['competency_id'], unique=False)

    # 10. pedagogical_alerts
    op.create_table(
        'pedagogical_alerts',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('student_id', sa.Uuid(), nullable=False),
        sa.Column('trigger_type', alerttriggertype, nullable=False),
        sa.Column('severity', alertseverity, nullable=False),
        sa.Column('status', alertstatus, nullable=False, server_default='UNREAD'),
        sa.Column('simplified_message', sa.Text(), nullable=False),
        sa.Column('expert_message', sa.Text(), nullable=False),
        sa.Column('context_data', sa.JSON(), nullable=True),
        sa.Column('recommended_action', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pedagogical_alerts_organization_id'), 'pedagogical_alerts', ['organization_id'], unique=False)
    op.create_index(op.f('ix_pedagogical_alerts_student_id'), 'pedagogical_alerts', ['student_id'], unique=False)
    op.create_index(op.f('ix_pedagogical_alerts_severity'), 'pedagogical_alerts', ['severity'], unique=False)

    # 11. alert_recipients
    op.create_table(
        'alert_recipients',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('alert_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('dismissed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['alert_id'], ['pedagogical_alerts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alert_recipients_organization_id'), 'alert_recipients', ['organization_id'], unique=False)


def downgrade() -> None:
    op.drop_table('alert_recipients')
    op.drop_table('pedagogical_alerts')
    op.drop_table('passport_assessments')
    op.drop_table('atom_completions')
    op.drop_table('remediation_paths')
    op.drop_table('competency_profiles')
    op.drop_table('diagnostic_answers')
    op.drop_table('diagnostic_sessions')
    op.drop_table('knowledge_atoms')
    op.drop_table('questions')
    op.drop_table('modules')
