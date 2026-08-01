"""
Unit and integration tests for Student Remediation Execution, Atom Delivery and Progress Tracking (Story 3.4).
"""

import uuid
import pytest
from app.core.tenant import set_active_organization_id, reset_active_organization_id
from app.models.content import KnowledgeAtom, RemediationType
from app.models.organization import Organization, OrganizationType
from app.models.remediation import RemediationPath, RemediationPathStatus
from app.repositories.remediation_repo import RemediationRepository
from app.engines.remediation_engine import PathwayGenerator
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_start_pathway_valid_and_invalid_transitions(db):
    """Test starting a pathway: VALIDATED -> IN_PROGRESS succeeds; PROPOSED -> IN_PROGRESS fails."""
    org = Organization(
        id=uuid.uuid4(), name="Execution Org", type=OrganizationType.SCHOOL
    )
    db.add(org)
    await db.commit()

    validated_path = RemediationPath(
        id=uuid.uuid4(),
        organization_id=org.id,
        student_id=uuid.uuid4(),
        competency_id="MATH_EXEC_01",
        status=RemediationPathStatus.VALIDATED,
    )
    proposed_path = RemediationPath(
        id=uuid.uuid4(),
        organization_id=org.id,
        student_id=uuid.uuid4(),
        competency_id="MATH_EXEC_02",
        status=RemediationPathStatus.PROPOSED,
    )
    db.add_all([validated_path, proposed_path])
    await db.commit()

    token = set_active_organization_id(org.id)
    try:
        repo = RemediationRepository(db)

        # Starting validated path succeeds
        started_path = await repo.start_pathway(validated_path.id)
        assert started_path.status == RemediationPathStatus.IN_PROGRESS

        # Starting proposed path fails with HTTP 409 Conflict
        with pytest.raises(HTTPException) as exc_info:
            await repo.start_pathway(proposed_path.id)
        assert exc_info.value.status_code == 409
    finally:
        reset_active_organization_id(token)


def test_concrete_to_abstract_atom_ordering():
    """Test that pathway generator orders atoms: AUDIO_VISUAL -> SIMULATION -> MIND_MAP."""
    atoms = [
        {
            "id": "atom-mind-map",
            "competency_id": "MATH_GEOM_01",
            "remediation_type": "MIND_MAP",
            "content": {"title": "Abstract Mind Map"},
        },
        {
            "id": "atom-audio-visual",
            "competency_id": "MATH_GEOM_01",
            "remediation_type": "AUDIO_VISUAL",
            "content": {"title": "Concrete Video"},
        },
        {
            "id": "atom-simulation",
            "competency_id": "MATH_GEOM_01",
            "remediation_type": "SIMULATION",
            "content": {"title": "Interactive Simulation"},
        },
    ]

    generator = PathwayGenerator()
    ordered_atoms = generator.generate(
        competency_id="MATH_GEOM_01",
        student_group="C",
        available_atoms=atoms,
    )

    types = [a["remediation_type"] for a in ordered_atoms]
    assert types == ["AUDIO_VISUAL", "SIMULATION", "MIND_MAP"]


@pytest.mark.asyncio
async def test_atom_completion_and_pathway_auto_complete(db):
    """Test completing atoms and auto-transitioning path status IN_PROGRESS -> COMPLETED when all atoms finished."""
    org = Organization(
        id=uuid.uuid4(), name="Completion Org", type=OrganizationType.SCHOOL
    )
    db.add(org)
    await db.commit()

    atom1 = KnowledgeAtom(
        id=uuid.uuid4(),
        organization_id=org.id,
        competency_id="COMP_TEST_01",
        remediation_type=RemediationType.AUDIO_VISUAL,
        content={"title": "Atom 1"},
    )
    atom2 = KnowledgeAtom(
        id=uuid.uuid4(),
        organization_id=org.id,
        competency_id="COMP_TEST_01",
        remediation_type=RemediationType.SIMULATION,
        content={"title": "Atom 2"},
    )
    db.add_all([atom1, atom2])
    await db.commit()

    path = RemediationPath(
        id=uuid.uuid4(),
        organization_id=org.id,
        student_id=uuid.uuid4(),
        competency_id="COMP_TEST_01",
        status=RemediationPathStatus.IN_PROGRESS,
        atoms_completed=[],
    )
    db.add(path)
    await db.commit()

    token = set_active_organization_id(org.id)
    try:
        repo = RemediationRepository(db)

        # Complete first atom
        await repo.record_atom_completion(
            path_id=path.id,
            atom_id=atom1.id,
            organization_id=org.id,
            time_spent_ms=10000,
        )
        updated_path = await repo.get_path(path.id)
        assert len(updated_path.atoms_completed) == 1
        assert updated_path.status == RemediationPathStatus.IN_PROGRESS

        # Complete second (final) atom
        await repo.record_atom_completion(
            path_id=path.id,
            atom_id=atom2.id,
            organization_id=org.id,
            time_spent_ms=12000,
        )
        completed_path = await repo.complete_pathway_if_finished(path.id, total_atoms_count=2)
        assert completed_path.status == RemediationPathStatus.COMPLETED
        assert completed_path.completed_at is not None
    finally:
        reset_active_organization_id(token)
