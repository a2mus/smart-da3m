"""
Unit tests for tenant-scoped models and organization_id foreign key presence.
"""

import uuid
import pytest
from app.models.alert import AlertRecipient, AlertSeverity, AlertStatus, AlertTriggerType, PedagogicalAlert
from app.models.content import KnowledgeAtom, Module, ModuleStatus, Question, RemediationType
from app.models.diagnostic import (
    CompetencyProfile,
    DiagnosticAnswer,
    DiagnosticSession,
    DiagnosticSessionStatus,
    ErrorClassification,
    MasteryLevel,
    RemediationGroup,
)
from app.models.organization import Organization, OrganizationType
from app.models.remediation import AtomCompletion, PassportAssessment, RemediationPath, RemediationPathStatus


def test_content_models_tenant_scoping():
    org_id = uuid.uuid4()
    module = Module(
        organization_id=org_id,
        subject="Mathematics",
        grade_level="Y1-2",
        domain="Arithmetic",
        competency_id="COMP-01",
        status=ModuleStatus.DRAFT,
        is_shared=False,
    )
    assert module.organization_id == org_id
    assert module.is_shared is False

    question = Question(
        organization_id=org_id,
        module_id=uuid.uuid4(),
        content={"text": "1 + 1 = ?"},
        difficulty_level=1,
        is_shared=True,
    )
    assert question.organization_id == org_id
    assert question.is_shared is True

    atom = KnowledgeAtom(
        organization_id=org_id,
        competency_id="COMP-01",
        remediation_type=RemediationType.AUDIO_VISUAL,
        content={"title": "Visual Counting"},
        is_shared=False,
    )
    assert atom.organization_id == org_id
    assert atom.is_shared is False


def test_diagnostic_models_tenant_scoping():
    org_id = uuid.uuid4()
    student_id = uuid.uuid4()

    session = DiagnosticSession(
        organization_id=org_id,
        student_id=student_id,
        module_id=uuid.uuid4(),
        status=DiagnosticSessionStatus.IN_PROGRESS,
    )
    assert session.organization_id == org_id

    answer = DiagnosticAnswer(
        organization_id=org_id,
        session_id=uuid.uuid4(),
        question_id=uuid.uuid4(),
        is_correct=1,
        response_time_ms=1500,
        error_classification=ErrorClassification.NONE,
    )
    assert answer.organization_id == org_id

    profile = CompetencyProfile(
        organization_id=org_id,
        student_id=student_id,
        competency_id="COMP-01",
        mastery_level=MasteryLevel.FAMILIAR,
        p_learned=0.6,
    )
    assert profile.organization_id == org_id


def test_remediation_models_tenant_scoping():
    org_id = uuid.uuid4()
    student_id = uuid.uuid4()

    path = RemediationPath(
        organization_id=org_id,
        student_id=student_id,
        competency_id="COMP-01",
        status=RemediationPathStatus.IN_PROGRESS,
    )
    assert path.organization_id == org_id

    completion = AtomCompletion(
        organization_id=org_id,
        path_id=uuid.uuid4(),
        atom_id=uuid.uuid4(),
        time_spent_ms=5000,
    )
    assert completion.organization_id == org_id

    passport = PassportAssessment(
        organization_id=org_id,
        student_id=student_id,
        competency_id="COMP-01",
        passed=1,
        accuracy=100,
    )
    assert passport.organization_id == org_id


def test_alert_models_tenant_scoping():
    org_id = uuid.uuid4()
    student_id = uuid.uuid4()

    alert = PedagogicalAlert(
        organization_id=org_id,
        student_id=student_id,
        trigger_type=AlertTriggerType.REPEATED_FAILURE,
        severity=AlertSeverity.WARNING,
        status=AlertStatus.UNREAD,
        simplified_message="Child struggled twice on arithmetic.",
        expert_message="Student failed COMP-01 twice in 7 days.",
    )
    assert alert.organization_id == org_id

    recipient = AlertRecipient(
        organization_id=org_id,
        alert_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
    )
    assert recipient.organization_id == org_id
