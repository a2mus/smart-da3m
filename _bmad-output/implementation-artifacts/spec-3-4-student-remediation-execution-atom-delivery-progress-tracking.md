---
title: 'Story 3.4: Student Remediation Execution, Atom Delivery and Progress Tracking'
type: 'feature'
created: '2026-08-01'
status: 'done'
baseline_revision: 'a5c6e777acbadc651cc1439ccb97edd0e1af17e2'
final_revision: '6c17e5c2e7c3580da67ff00570326b1522e6921c'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-3-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** While pathways can be diagnosed, proposed, and validated by experts (Stories 3.1–3.3), students cannot yet execute validated remediation pathways. The backend lacks endpoints to start a validated path (`VALIDATED` -> `IN_PROGRESS`), deliver atoms strictly ordered from concrete to abstract (`AUDIO_VISUAL` -> `SIMULATION` -> `MIND_MAP`), track progress per atom completion, and auto-transition status from `IN_PROGRESS` -> `COMPLETED` when all atoms are finished.

**Approach:** Implement `POST /api/v1/remediation/pathway/{path_id}/start` to transition validated pathways to `IN_PROGRESS`. Update `GET /api/v1/remediation/pathway/{competency_id}` to deliver atoms in concrete-to-abstract priority order. Update `POST /api/v1/remediation/atoms/{atom_id}/complete` to record atom completion, update difficulty, recalculate progress percent, and auto-transition to `COMPLETED` (setting `completed_at`) when all pathway atoms are completed. Update `frontend/src/services/remediationService.ts` and create `frontend/src/views/student/RemediationExecutionView.vue` for interactive student delivery and progress tracking.

## Boundaries & Constraints

**Always:** Enforce AD-2 state machine transition guards (`VALIDATED` -> `IN_PROGRESS`, `IN_PROGRESS` -> `COMPLETED`). Sort knowledge atoms by concrete-to-abstract ordering (`AUDIO_VISUAL`=1, `SIMULATION`=2, `MIND_MAP`=3). Ensure multi-tenant scoping on all queries.

**Block If:** Operator/human actions outside the repository are required.

**Never:** Allow unvalidated (`PROPOSED` or `DIAGNOSED`) pathways to be started by students. Allow invalid status transitions bypassing the service state machine layer.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Start Validated Pathway | `POST /api/v1/remediation/pathway/{path_id}/start` on `VALIDATED` path | Path status transitions to `IN_PROGRESS` | 200 OK |
| Start Unvalidated Pathway | `POST /api/v1/remediation/pathway/{path_id}/start` on `PROPOSED` path | State transition guard blocks request | 409 Conflict |
| Concrete-to-Abstract Atom Delivery | `GET /api/v1/remediation/pathway/{competency_id}` | Returned atoms sorted by `AUDIO_VISUAL` -> `SIMULATION` -> `MIND_MAP` | 200 OK |
| Complete Intermediate Atom | `POST /api/v1/remediation/atoms/{atom_id}/complete` on item 1 of 3 | `atoms_completed` updated, `progress_percent` ~33.3%, status stays `IN_PROGRESS` | 200 OK |
| Complete Final Atom | `POST /api/v1/remediation/atoms/{atom_id}/complete` on final atom | `atoms_completed` updated, status auto-transitions `IN_PROGRESS` -> `COMPLETED`, `completed_at` timestamp set | 200 OK |

</intent-contract>

## Code Map

- `backend/app/schemas/remediation.py` -- Define `StartPathwayResponse` and update atom completion response schemas
- `backend/app/repositories/remediation_repo.py` -- Implement `start_pathway` and `check_and_complete_pathway`
- `backend/app/api/endpoints/remediation.py` -- Implement `POST /pathway/{path_id}/start` and update atom completion logic
- `frontend/src/services/remediationService.ts` -- Add `startPathway`, `completeAtom`, `getRemediationPathway` API calls
- `frontend/src/views/student/RemediationExecutionView.vue` -- Create student atom execution and progress tracking view
- `frontend/src/router/index.ts` -- Register `/student/remediation/:competencyId` route
- `backend/tests/api/test_student_remediation_execution.py` -- Test suite for pathway execution, concrete-to-abstract delivery, progress calculation, and state auto-completion

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/schemas/remediation.py` -- Add `StartPathwayResponse` schema and atom completion update fields
- [x] `backend/app/repositories/remediation_repo.py` -- Add `start_pathway` (`VALIDATED` -> `IN_PROGRESS`) and `complete_pathway_if_finished` (`IN_PROGRESS` -> `COMPLETED`)
- [x] `backend/app/api/endpoints/remediation.py` -- Add `POST /pathway/{path_id}/start`, enforce atom delivery ordering, and auto-complete pathway when all atoms are completed
- [x] `frontend/src/services/remediationService.ts` -- Add service methods for `startPathway`, `completeAtom`, and `getRemediationPathway`
- [x] `frontend/src/views/student/RemediationExecutionView.vue` -- Create student execution interface with concrete-to-abstract atom delivery, progress bar, and completion summary
- [x] `frontend/src/router/index.ts` -- Register `/student/remediation/:competencyId` route
- [x] `backend/tests/api/test_student_remediation_execution.py` -- Add unit and integration tests covering student pathway start, atom delivery order, completion tracking, and state machine guards

**Acceptance Criteria:**
- Given a `VALIDATED` remediation path, when a student calls `POST /api/v1/remediation/pathway/{path_id}/start`, then the path status transitions to `IN_PROGRESS`.
- Given a `PROPOSED` or `DIAGNOSED` path, when `POST /api/v1/remediation/pathway/{path_id}/start` is called, then HTTP 409 Conflict is returned.
- Given a request for a remediation pathway, returned knowledge atoms are strictly ordered by concrete-to-abstract progression (`AUDIO_VISUAL` -> `SIMULATION` -> `MIND_MAP`).
- Given an `IN_PROGRESS` pathway, when the final atom is completed via `POST /api/v1/remediation/atoms/{atom_id}/complete`, then status automatically transitions to `COMPLETED` and `completed_at` is set.
- Given the student frontend, `/student/remediation/:competencyId` displays current progress, atom delivery in concrete-to-abstract sequence, and unlocks Passport test upon completion.

## Verification

**Commands:**
- `cd backend && pytest tests/api/test_student_remediation_execution.py tests/services/test_remediation_state_machine.py` -- expected: All execution, atom delivery, and state transition tests pass

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
Implemented Student Remediation Execution, Atom Delivery and Progress Tracking (Story 3.4). Added `POST /api/v1/remediation/pathway/{path_id}/start` endpoint to transition validated pathways to `IN_PROGRESS`, concrete-to-abstract atom delivery sequence (`AUDIO_VISUAL` -> `SIMULATION` -> `MIND_MAP`), atom completion progress tracking with automatic state transition to `COMPLETED` and timestamp recording, Vue student execution interface (`RemediationExecutionView.vue`), frontend router registration (`/student/remediation/:competencyId`), and unit/integration pytest suite.

### Files Changed
- `backend/app/schemas/remediation.py` -- Added `StartPathwayResponse` schema
- `backend/app/repositories/remediation_repo.py` -- Added `start_pathway` (`VALIDATED` -> `IN_PROGRESS`) and `complete_pathway_if_finished` (`IN_PROGRESS` -> `COMPLETED`)
- `backend/app/api/endpoints/remediation.py` -- Added `POST /pathway/{path_id}/start`, concrete-to-abstract ordering, and auto-completion logic
- `frontend/src/services/remediationService.ts` -- Added `startPathway` API method
- `frontend/src/views/student/RemediationExecutionView.vue` -- Created Vue student remediation execution view
- `frontend/src/router/index.ts` -- Registered `/student/remediation/:competencyId` route
- `backend/tests/api/test_student_remediation_execution.py` -- Added test suite for pathway start, atom delivery, and progress auto-completion

### Review Findings Breakdown
- Patches applied: 0
- Items deferred: 0
- Items rejected: 0

### Verification Performed
- `pytest tests/api/test_student_remediation_execution.py tests/services/test_remediation_state_machine.py` passed 23/23 tests (100% pass rate).
