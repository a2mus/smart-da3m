"""
Unit and integration tests for Expert Validation Queue and Workflow (Story 3.3).
"""

import uuid
import pytest
from app.core.tenant import set_active_organization_id, reset_active_organization_id
from app.models.organization import Organization, OrganizationType
from app.models.remediation import RemediationPath, RemediationPathStatus
from app.repositories.remediation_repo import RemediationRepository


@pytest.mark.asyncio
async def test_repository_get_validation_queue(db):
    """Test repository queue filtering for school vs household (pedagogue pool) orgs."""
    school_org = Organization(
        id=uuid.uuid4(), name="Test School", type=OrganizationType.SCHOOL
    )
    household_org = Organization(
        id=uuid.uuid4(), name="Test Household", type=OrganizationType.HOUSEHOLD
    )
    db.add_all([school_org, household_org])
    await db.commit()

    student1_id = uuid.uuid4()
    student2_id = uuid.uuid4()

    school_path = RemediationPath(
        id=uuid.uuid4(),
        organization_id=school_org.id,
        student_id=student1_id,
        competency_id="MATH_ADD_01",
        status=RemediationPathStatus.PROPOSED,
        proposal_data={"atoms": [{"id": "atom-1"}]},
    )
    household_path = RemediationPath(
        id=uuid.uuid4(),
        organization_id=household_org.id,
        student_id=student2_id,
        competency_id="MATH_SUB_01",
        status=RemediationPathStatus.PROPOSED,
        proposal_data={"atoms": [{"id": "atom-2"}]},
    )
    db.add_all([school_path, household_path])
    await db.commit()

    token = set_active_organization_id(school_org.id)
    try:
        repo = RemediationRepository(db)

        # School queue should return school path only
        school_queue = await repo.get_validation_queue(
            organization_id=school_org.id, is_pedagogue_pool=False
        )
        assert len(school_queue) == 1
        assert school_queue[0].id == school_path.id

        # Pedagogue pool queue should return household path
        pool_queue = await repo.get_validation_queue(
            organization_id=None, is_pedagogue_pool=True
        )
        assert len(pool_queue) == 1
        assert pool_queue[0].id == household_path.id
    finally:
        reset_active_organization_id(token)


@pytest.mark.asyncio
async def test_repository_validate_and_reject_proposal(db):
    """Test validation (PROPOSED -> VALIDATED) and rejection (PROPOSED -> DIAGNOSED with feedback)."""
    org = Organization(
        id=uuid.uuid4(), name="Validation Org", type=OrganizationType.SCHOOL
    )
    db.add(org)
    await db.commit()

    path_to_validate = RemediationPath(
        id=uuid.uuid4(),
        organization_id=org.id,
        student_id=uuid.uuid4(),
        competency_id="AR_READ_01",
        status=RemediationPathStatus.PROPOSED,
    )
    path_to_reject = RemediationPath(
        id=uuid.uuid4(),
        organization_id=org.id,
        student_id=uuid.uuid4(),
        competency_id="AR_READ_02",
        status=RemediationPathStatus.PROPOSED,
    )
    db.add_all([path_to_validate, path_to_reject])
    await db.commit()

    token = set_active_organization_id(org.id)
    try:
        repo = RemediationRepository(db)

        # Approve path
        validated_path = await repo.validate_proposal(path_to_validate.id)
        assert validated_path.status == RemediationPathStatus.VALIDATED

        # Reject path with feedback
        feedback_text = "Needs simpler visual atoms for pre-literate stage"
        rejected_path = await repo.reject_proposal(path_to_reject.id, feedback_text)
        assert rejected_path.status == RemediationPathStatus.DIAGNOSED
        assert rejected_path.rejection_feedback == feedback_text
    finally:
        reset_active_organization_id(token)
