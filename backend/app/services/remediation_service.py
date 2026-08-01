"""
Remediation Service layer enforcing AD-2 state machine transition guards.
"""

from typing import Dict, Set
from fastapi import HTTPException, status

from app.models.remediation import RemediationPath, RemediationPathStatus


class InvalidStateTransitionError(Exception):
    """Exception raised when an invalid state transition is attempted."""

    def __init__(
        self,
        current_status: RemediationPathStatus,
        target_status: RemediationPathStatus,
    ):
        self.current_status = current_status
        self.target_status = target_status
        self.message = (
            f"Cannot transition from {current_status.value} to {target_status.value}"
        )
        super().__init__(self.message)


# AD-2 Allowed State Transitions Matrix
VALID_TRANSITIONS: Dict[RemediationPathStatus, Set[RemediationPathStatus]] = {
    RemediationPathStatus.DIAGNOSED: {RemediationPathStatus.PROPOSED},
    RemediationPathStatus.PROPOSED: {
        RemediationPathStatus.VALIDATED,
        RemediationPathStatus.DIAGNOSED,
    },
    RemediationPathStatus.VALIDATED: {RemediationPathStatus.IN_PROGRESS},
    RemediationPathStatus.IN_PROGRESS: {
        RemediationPathStatus.COMPLETED,
        RemediationPathStatus.ABANDONED,
    },
    RemediationPathStatus.COMPLETED: {RemediationPathStatus.PASSPORT_TESTING},
    RemediationPathStatus.PASSPORT_TESTING: {
        RemediationPathStatus.MASTERED,
        RemediationPathStatus.DIAGNOSED,
    },
    RemediationPathStatus.ABANDONED: {
        RemediationPathStatus.PROPOSED,
        RemediationPathStatus.RETIRED,
    },
    RemediationPathStatus.MASTERED: set(),
    RemediationPathStatus.RETIRED: set(),
}


def validate_transition(
    current_status: RemediationPathStatus,
    target_status: RemediationPathStatus,
) -> bool:
    """
    Validate state transition against the AD-2 matrix.
    Raises HTTP 409 Conflict with INVALID_STATE_TRANSITION detail on forbidden transitions.
    """
    allowed_targets = VALID_TRANSITIONS.get(current_status, set())
    if target_status not in allowed_targets:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "INVALID_STATE_TRANSITION",
                "message": f"Cannot transition from {current_status.value} to {target_status.value}",
                "current_status": current_status.value,
                "target_status": target_status.value,
            },
        )
    return True


class RemediationService:
    """Service handling state transitions and business logic for remediation paths."""

    @staticmethod
    def validate_state_transition(
        current_status: RemediationPathStatus,
        target_status: RemediationPathStatus,
    ) -> bool:
        """Validate if target_status is a valid next state from current_status."""
        return validate_transition(current_status, target_status)

    @staticmethod
    def get_allowed_transitions(
        current_status: RemediationPathStatus,
    ) -> Set[RemediationPathStatus]:
        """Get set of allowed target statuses from current_status."""
        return VALID_TRANSITIONS.get(current_status, set())
