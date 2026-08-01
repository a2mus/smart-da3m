"""
Unit tests for Remediation Pathway State Machine and Transition Guard (AD-2).
"""

import pytest
from fastapi import HTTPException

from app.models.remediation import RemediationPathStatus
from app.services.remediation_service import (
    VALID_TRANSITIONS,
    RemediationService,
    validate_transition,
)


def test_remediation_path_status_contains_all_ad2_states():
    """Verify that RemediationPathStatus enum contains all 9 required AD-2 states."""
    expected_states = {
        "DIAGNOSED",
        "PROPOSED",
        "VALIDATED",
        "IN_PROGRESS",
        "COMPLETED",
        "ABANDONED",
        "PASSPORT_TESTING",
        "MASTERED",
        "RETIRED",
    }
    actual_states = {status.value for status in RemediationPathStatus}
    assert expected_states.issubset(actual_states)


@pytest.mark.parametrize(
    "current_status,target_status",
    [
        (RemediationPathStatus.DIAGNOSED, RemediationPathStatus.PROPOSED),
        (RemediationPathStatus.PROPOSED, RemediationPathStatus.VALIDATED),
        (RemediationPathStatus.PROPOSED, RemediationPathStatus.DIAGNOSED),
        (RemediationPathStatus.VALIDATED, RemediationPathStatus.IN_PROGRESS),
        (RemediationPathStatus.IN_PROGRESS, RemediationPathStatus.COMPLETED),
        (RemediationPathStatus.IN_PROGRESS, RemediationPathStatus.ABANDONED),
        (RemediationPathStatus.COMPLETED, RemediationPathStatus.PASSPORT_TESTING),
        (RemediationPathStatus.PASSPORT_TESTING, RemediationPathStatus.MASTERED),
        (RemediationPathStatus.PASSPORT_TESTING, RemediationPathStatus.DIAGNOSED),
        (RemediationPathStatus.ABANDONED, RemediationPathStatus.PROPOSED),
        (RemediationPathStatus.ABANDONED, RemediationPathStatus.RETIRED),
    ],
)
def test_valid_state_transitions(current_status, target_status):
    """Verify that allowed transitions pass state machine guard without error."""
    assert validate_transition(current_status, target_status) is True
    assert RemediationService.validate_state_transition(current_status, target_status) is True


@pytest.mark.parametrize(
    "current_status,target_status",
    [
        (RemediationPathStatus.DIAGNOSED, RemediationPathStatus.IN_PROGRESS),
        (RemediationPathStatus.PROPOSED, RemediationPathStatus.IN_PROGRESS),
        (RemediationPathStatus.DIAGNOSED, RemediationPathStatus.COMPLETED),
        (RemediationPathStatus.VALIDATED, RemediationPathStatus.MASTERED),
        (RemediationPathStatus.MASTERED, RemediationPathStatus.IN_PROGRESS),
        (RemediationPathStatus.RETIRED, RemediationPathStatus.IN_PROGRESS),
        (RemediationPathStatus.COMPLETED, RemediationPathStatus.IN_PROGRESS),
    ],
)
def test_invalid_state_transitions_raise_409(current_status, target_status):
    """Verify that invalid transitions raise HTTP 409 Conflict with INVALID_STATE_TRANSITION code."""
    with pytest.raises(HTTPException) as exc_info:
        validate_transition(current_status, target_status)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail["code"] == "INVALID_STATE_TRANSITION"
    assert current_status.value in exc_info.value.detail["message"]
    assert target_status.value in exc_info.value.detail["message"]


def test_get_allowed_transitions():
    """Verify that get_allowed_transitions returns correct targets."""
    allowed_from_diagnosed = RemediationService.get_allowed_transitions(RemediationPathStatus.DIAGNOSED)
    assert allowed_from_diagnosed == {RemediationPathStatus.PROPOSED}

    allowed_from_mastered = RemediationService.get_allowed_transitions(RemediationPathStatus.MASTERED)
    assert allowed_from_mastered == set()
