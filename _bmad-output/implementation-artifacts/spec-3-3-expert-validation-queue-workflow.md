---
title: 'Story 3.3: Expert Validation Queue & Workflow'
type: 'feature'
created: '2026-08-01'
status: 'done'
baseline_revision: '01844170817064b589c6e95080fd6a38047d3515'
final_revision: 'fd53b2086eaed71fc9fe826878d4a338e7db4512'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-3-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** AI-generated remediation proposals (status `PROPOSED`) must be reviewed and approved by pedagogical experts before students can access or execute them. Currently, there are no validation queue endpoints or expert approval/rejection workflows in the API or frontend.

**Approach:** Implement `GET /api/v1/remediation/validation-queue` with multi-tenant routing (SCHOOL org proposals route to school experts; HOUSEHOLD proposals route to platform pedagogue pool). Implement approval (`POST /api/v1/remediation-paths/{id}/validate`) and rejection (`POST /api/v1/remediation-paths/{id}/reject`) endpoints with state machine guards, persisting rejection feedback for AI regeneration. Create a frontend validation queue view at `/expert/validation`.

## Boundaries & Constraints

**Always:** Enforce AD-2 state machine transition guards (PROPOSED -> VALIDATED on approve; PROPOSED -> DIAGNOSED on reject). Route SCHOOL proposals to the school's organization and HOUSEHOLD proposals to the platform pedagogue pool. Store expert rejection feedback on the remediation path.

**Block If:** Operator/human actions outside the repository are required.

**Never:** Allow unvalidated `PROPOSED` paths to be started by students. Allow invalid status transitions bypassing the service state machine layer.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| List Validation Queue (School Expert) | `GET /api/v1/remediation/validation-queue` for SCHOOL org user | Returns all `PROPOSED` remediation paths belonging to the school org | 200 OK |
| List Validation Queue (Platform Pedagogue) | `GET /api/v1/remediation/validation-queue` for platform pedagogue/household | Returns all `PROPOSED` remediation paths for `HOUSEHOLD` orgs | 200 OK |
| Approve Proposal | `POST /api/v1/remediation-paths/{id}/validate` on `PROPOSED` path | Path status transitions to `VALIDATED` | 200 OK |
| Reject Proposal with Feedback | `POST /api/v1/remediation-paths/{id}/reject` with `{"feedback": "Focus on visual atoms"}` | Path status transitions to `DIAGNOSED`, `rejection_feedback` saved | 200 OK |
| Invalid State Approval | `POST /api/v1/remediation-paths/{id}/validate` on `IN_PROGRESS` path | Blocked by state machine guard | 409 Conflict |

</intent-contract>

## Code Map

- `backend/app/models/remediation.py` -- Add `proposal_data` and `rejection_feedback` fields to `RemediationPath`
- `backend/app/schemas/remediation.py` -- Define validation queue and reject/approve request/response schemas
- `backend/app/repositories/remediation_repo.py` -- Implement `get_validation_queue`, `validate_proposal`, `reject_proposal`
- `backend/app/api/endpoints/remediation.py` -- Implement `/validation-queue`, `/remediation-paths/{id}/validate`, `/remediation-paths/{id}/reject`
- `frontend/src/views/expert/ValidationQueueView.vue` -- Create frontend expert validation queue view
- `frontend/src/router/index.ts` -- Register `/expert/validation` route
- `backend/tests/api/test_expert_validation_queue.py` -- Unit and integration tests for validation queue API

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/models/remediation.py` -- Add `proposal_data` (JSON) and `rejection_feedback` (String) to `RemediationPath`
- [x] `backend/app/schemas/remediation.py` -- Add `ValidationQueueItemResponse`, `RejectProposalRequest`, `ApproveProposalResponse`
- [x] `backend/app/repositories/remediation_repo.py` -- Add `get_validation_queue`, `validate_proposal`, `reject_proposal`
- [x] `backend/app/api/endpoints/remediation.py` -- Add `GET /remediation/validation-queue`, `POST /remediation-paths/{id}/validate`, `POST /remediation-paths/{id}/reject`
- [x] `frontend/src/views/expert/ValidationQueueView.vue` -- Create Vue validation queue component for expert review
- [x] `frontend/src/router/index.ts` -- Add `/expert/validation` route
- [x] `backend/tests/api/test_expert_validation_queue.py` -- Add test suite for queue filtering, validation, rejection feedback, and state guards

**Acceptance Criteria:**
- Given a path is in `PROPOSED` state, when an expert requests `GET /api/v1/remediation/validation-queue`, then matching proposed paths are returned.
- Given a proposal in `PROPOSED` state, when `POST /api/v1/remediation-paths/{id}/validate` is called, then status changes to `VALIDATED`.
- Given a proposal in `PROPOSED` state, when `POST /api/v1/remediation-paths/{id}/reject` is called with feedback, then status changes to `DIAGNOSED` and feedback is stored.
- Given a SCHOOL org, proposals are routed to that school's experts; given a HOUSEHOLD org, proposals route to platform pedagogue pool.
- Given the frontend app, `/expert/validation` route renders the validation queue view.

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

### Summary
Implemented Expert Validation Queue and Workflow (Story 3.3). Added multi-tenant proposal routing (SCHOOL vs HOUSEHOLD platform pedagogue pool), validation/approval endpoints, rejection with feedback handling, state machine guards, unit test coverage, and a Vue frontend validation queue interface at `/expert/validation`.

### Files Changed
- `backend/app/models/remediation.py` -- Added `proposal_data` and `rejection_feedback` fields to `RemediationPath`
- `backend/app/schemas/remediation.py` -- Defined `ValidationQueueItemResponse`, `RejectProposalRequest`, `ApproveProposalResponse`
- `backend/app/repositories/remediation_repo.py` -- Added `get_validation_queue`, `validate_proposal`, `reject_proposal` methods
- `backend/app/api/endpoints/remediation.py` -- Added `GET /validation-queue`, `POST /remediation-paths/{id}/validate`, `POST /remediation-paths/{id}/reject`
- `frontend/src/views/expert/ValidationQueueView.vue` -- Created Vue validation queue component for expert review
- `frontend/src/router/index.ts` -- Registered `/expert/validation` route
- `backend/tests/api/test_expert_validation_queue.py` -- Added test suite for validation queue filtering and status transitions

### Review Findings Breakdown
- Patches applied: 0
- Items deferred: 0
- Items rejected: 0

### Verification Performed
- `pytest tests/api/test_expert_validation_queue.py tests/services/test_remediation_state_machine.py` passed 22/22 tests (100% pass rate).

## Verification

**Commands:**
- `cd backend && pytest tests/api/test_expert_validation_queue.py` -- expected: All validation queue and transition tests pass
