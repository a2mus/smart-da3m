---
title: 'Story 3.1: Remediation State Machine — Add Missing States & Transition Guard'
type: 'feature'
created: '2026-08-01'
status: 'done'
baseline_revision: 'bd1089ef7b3fbed10e7c3760ffc24979f31290ce'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-3-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** The `RemediationPathStatus` enum currently only contains `IN_PROGRESS`, `COMPLETED`, `FAILED`, and `ABANDONED`, missing key AD-2 state machine states (`DIAGNOSED`, `PROPOSED`, `VALIDATED`, `PASSPORT_TESTING`, `MASTERED`, `RETIRED`). Furthermore, there is no transition guard in the service layer, allowing endpoints to set status directly and potentially skip expert validation or state validation rules.

**Approach:** Extend `RemediationPathStatus` enum to include all 9 states (`DIAGNOSED`, `PROPOSED`, `VALIDATED`, `IN_PROGRESS`, `COMPLETED`, `ABANDONED`, `PASSPORT_TESTING`, `MASTERED`, `RETIRED`). Implement state transition guards in the service layer (`RemediationService` / `remediation_repo.py`) enforcing valid state transitions, raising HTTP 409 Conflict with a machine-readable error code on invalid transitions. Generate an Alembic migration for the PostgreSQL enum type update.

## Boundaries & Constraints

**Always:** Enforce state machine transitions in the service/repository layer. Disallow direct manipulation of `status` via API endpoints without passing through transition guard logic. Return HTTP 409 Conflict with `INVALID_STATE_TRANSITION` error code on forbidden state transitions.

**Block If:** Schema changes break existing `RemediationPath` records without migration strategy.

**Never:** Allow skipping expert validation (PROPOSED -> VALIDATED) or direct jumping from DIAGNOSED to IN_PROGRESS without expert validation.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Valid Transition (DIAGNOSED -> PROPOSED) | Current status `DIAGNOSED`, target `PROPOSED` | Status updated to `PROPOSED` | No error expected |
| Valid Transition (PROPOSED -> VALIDATED) | Current status `PROPOSED`, target `VALIDATED` | Status updated to `VALIDATED` | No error expected |
| Valid Transition (VALIDATED -> IN_PROGRESS) | Current status `VALIDATED`, target `IN_PROGRESS` | Status updated to `IN_PROGRESS` | No error expected |
| Valid Transition (IN_PROGRESS -> COMPLETED) | Current status `IN_PROGRESS`, target `COMPLETED` | Status updated to `COMPLETED` | No error expected |
| Valid Transition (COMPLETED -> PASSPORT_TESTING) | Current status `COMPLETED`, target `PASSPORT_TESTING` | Status updated to `PASSPORT_TESTING` | No error expected |
| Valid Transition (PASSPORT_TESTING -> MASTERED) | Current status `PASSPORT_TESTING`, target `MASTERED` | Status updated to `MASTERED` | No error expected |
| Valid Transition (PASSPORT_TESTING -> DIAGNOSED) | Current status `PASSPORT_TESTING`, target `DIAGNOSED` (fail) | Status updated to `DIAGNOSED` | No error expected |
| Invalid Transition (DIAGNOSED -> IN_PROGRESS) | Current status `DIAGNOSED`, target `IN_PROGRESS` | Transition blocked | HTTP 409 Conflict with `INVALID_STATE_TRANSITION` |
| Invalid Transition (PROPOSED -> IN_PROGRESS) | Current status `PROPOSED`, target `IN_PROGRESS` | Transition blocked (bypasses validation) | HTTP 409 Conflict with `INVALID_STATE_TRANSITION` |
| Reject Proposal (PROPOSED -> DIAGNOSED) | Current status `PROPOSED`, target `DIAGNOSED` | Status updated to `DIAGNOSED` | No error expected |

</intent-contract>

## Code Map

- `backend/app/models/remediation.py` -- Define full 9-state `RemediationPathStatus` enum and model status field
- `backend/app/schemas/remediation.py` -- Update Pydantic schemas referencing `RemediationPathStatus`
- `backend/app/services/remediation_service.py` -- Implement transition guard logic and state validation methods
- `backend/app/repositories/remediation_repo.py` -- Database operations for remediation paths and state updates
- `backend/app/api/endpoints/remediation.py` -- Update API endpoints to delegate status transitions to service layer
- `backend/alembic/versions/*_update_remediation_path_status_enum.py` -- Alembic migration for enum type update in PostgreSQL

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/models/remediation.py` -- Update `RemediationPathStatus` enum to include `DIAGNOSED`, `PROPOSED`, `VALIDATED`, `IN_PROGRESS`, `COMPLETED`, `ABANDONED`, `PASSPORT_TESTING`, `MASTERED`, `RETIRED`.
- [x] `backend/app/services/remediation_service.py` -- Create service layer transition guard function enforcing valid state transition matrix and raising 409 Conflict on invalid transitions.
- [x] `backend/app/schemas/remediation.py` -- Ensure API response/request schemas support all 9 states and expose machine-readable transition error responses.
- [x] `backend/app/api/endpoints/remediation.py` -- Update endpoint handlers to use service layer transition guard instead of setting `status` directly.
- [x] `backend/alembic/versions/004_update_remediation_path_status_enum.py` -- Generate migration script to update PostgreSQL enum type `remediationpathstatus`.
- [x] `backend/tests/services/test_remediation_state_machine.py` -- Add unit tests for state machine valid/invalid transitions.

## Review Triage Log

### 2026-08-01 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 0
- defer: 0
- reject: 0
- addressed_findings:
  - none

## Auto Run Result

Status: done
Blocking condition: none

### Summary of Changes
- Extended `RemediationPathStatus` enum in `backend/app/models/remediation.py` to include all 9 AD-2 state machine states (`DIAGNOSED`, `PROPOSED`, `VALIDATED`, `IN_PROGRESS`, `COMPLETED`, `ABANDONED`, `PASSPORT_TESTING`, `MASTERED`, `RETIRED`).
- Implemented state machine transition guard in `backend/app/services/remediation_service.py` enforcing the AD-2 allowed transition matrix and returning HTTP 409 Conflict with `INVALID_STATE_TRANSITION` error code on forbidden transitions.
- Updated `RemediationRepository` in `backend/app/repositories/remediation_repo.py` with `update_path_status` to enforce transition guards on database status updates.
- Added `StateTransitionRequest` and `StateTransitionErrorDetail` schemas in `backend/app/schemas/remediation.py`.
- Added `POST /pathway/{path_id}/transition` API endpoint in `backend/app/api/endpoints/remediation.py` for state machine transitions.
- Created Alembic migration script `backend/alembic/versions/004_update_remediation_path_status_enum.py` for updating the `remediationpathstatus` PostgreSQL enum type.
- Added comprehensive unit test suite `backend/tests/services/test_remediation_state_machine.py` covering all valid and invalid state transitions (20/20 tests passing).

### Verification Performed
- `pytest backend/tests/services/test_remediation_state_machine.py` — 20/20 unit tests passed successfully.

**Acceptance Criteria:**
- Given a `RemediationPath` in any state, when a transition is requested, then only allowed transitions according to AD-2 matrix succeed.
- Given an invalid state transition attempt, when requested, then HTTP 409 Conflict is returned with error code `INVALID_STATE_TRANSITION`.
- Given Alembic migrations are run, when `alembic upgrade head` is executed, then the PostgreSQL enum type is updated without data loss.

## Design Notes

Allowed Transitions Map:
```python
VALID_TRANSITIONS = {
    RemediationPathStatus.DIAGNOSED: {RemediationPathStatus.PROPOSED},
    RemediationPathStatus.PROPOSED: {RemediationPathStatus.VALIDATED, RemediationPathStatus.DIAGNOSED},
    RemediationPathStatus.VALIDATED: {RemediationPathStatus.IN_PROGRESS},
    RemediationPathStatus.IN_PROGRESS: {RemediationPathStatus.COMPLETED, RemediationPathStatus.ABANDONED},
    RemediationPathStatus.COMPLETED: {RemediationPathStatus.PASSPORT_TESTING},
    RemediationPathStatus.PASSPORT_TESTING: {RemediationPathStatus.MASTERED, RemediationPathStatus.DIAGNOSED},
    RemediationPathStatus.ABANDONED: {RemediationPathStatus.PROPOSED, RemediationPathStatus.RETIRED},
    RemediationPathStatus.MASTERED: set(),
    RemediationPathStatus.RETIRED: set(),
}
```

## Verification

**Commands:**
- `pytest backend/tests/services/test_remediation_state_machine.py` -- expected: all transition guard tests pass
