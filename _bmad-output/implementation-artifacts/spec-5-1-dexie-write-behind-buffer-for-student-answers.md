---
title: 'Story 5.1: Dexie Write-Behind Buffer for Student Answers'
type: 'feature'
created: '2026-08-01'
status: 'done'
baseline_revision: '41afb9a44d255c473e377a7d2cd690a64951e361'
final_revision: '962d57c42600e63cb75b5efabb723286afe8abc5'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-5-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** `DiagnosticRunner.vue` calls `diagnosticService.submitAnswer()` directly via HTTP. When connectivity drops, the network call throws an unhandled error and student answer progress is lost.

**Approach:** Implement a Dexie write-behind buffer in `offlineModule.ts` that saves answers to IndexedDB immediately. When online, send write-through to the backend; when offline, queue with `sync_status: 'PENDING'` and flush on reconnect. Ensure backend `POST /api/v1/diagnostic/answer` is idempotent.

## Boundaries & Constraints

**Always:**
- Save answers to Dexie `pending_answers` immediately upon student submission.
- Maintain answer order during sync flush upon network reconnection.
- Return 200 OK with recorded result if backend `/api/v1/diagnostic/answer` receives a duplicate `(session_id, question_id)`.
- Use logical CSS and semantic colors for any UI elements added to `DiagnosticRunner.vue`.

**Block If:**
- Required changes conflict with established Dexie database structure in `offlineModule.ts`.

**Never:**
- Lose student answers during offline network drops.
- Remove queued answers from Dexie before backend confirmation of successful sync.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Online Submit | Student submits answer while online | Saved to Dexie `pending_answers` as `SYNCED`, sent to backend via HTTP, returns immediate feedback | Falls back to offline queuing if HTTP request fails |
| Offline Submit | Student submits answer while offline | Saved to Dexie `pending_answers` as `PENDING`, UI advances using cached question | Display offline status indicator, flush when online event fires |
| Reconnect Sync | `window.addEventListener('online')` fires | Pending answers flushed in chronological order to backend | Keep item in Dexie if sync fails, retry on next reconnect |
| Duplicate Re-submit | Backend receives `submit_answer` for already answered `(session_id, question_id)` | Returns existing answer response without duplicate BKT update | Return HTTP 200 with recorded evaluation |

</intent-contract>

## Code Map

- `frontend/src/stores/offlineModule.ts` -- Update Dexie schema to add `pending_answers` table (`id, session_id, question_id, answer, sync_status, created_at`) and methods `queueAnswer`, `getPendingAnswers`, `markAnswerSynced`.
- `frontend/src/services/diagnosticService.ts` -- Add fallback handling for network drops during answer submission.
- `frontend/src/components/student/DiagnosticRunner.vue` -- Integrate Dexie write-behind submission, online/offline state handling, and sync triggering.
- `backend/app/repositories/diagnostic_repo.py` -- Add helper to check if an answer for `(session_id, question_id)` already exists.
- `backend/app/api/endpoints/diagnostic.py` -- Make `POST /api/v1/diagnostic/answer` idempotent by returning existing recorded evaluation if `(session_id, question_id)` was previously recorded.
- `frontend/tests/stores/offlineModule.spec.ts` -- Unit tests for Dexie write-behind buffer and offline answer queueing.
- `backend/tests/test_diagnostic_endpoint.py` -- Unit test verifying idempotent re-submission of diagnostic answer.

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/stores/offlineModule.ts` -- Add `pending_answers` table to Dexie `OfflineDatabase` and implement `queueAnswer()`, `getPendingAnswers()`, and `markAnswerSynced()` helper methods -- Enables Dexie write-behind storage for answers.
- [x] `backend/app/api/endpoints/diagnostic.py` -- Add idempotency check for existing `(session_id, question_id)` answers before processing BKT & recording answer -- Ensures network retries do not duplicate BKT updates or answers.
- [x] `frontend/src/components/student/DiagnosticRunner.vue` -- Wire answer submission through `offlineStore.queueAnswer()` with write-through/write-behind logic and automatic flush on `online` event -- Prevents lost student answers on network drops.
- [x] `frontend/tests/stores/offlineModule.spec.ts` -- Add unit tests for Dexie answer queueing, retrieval, and status updates -- Verifies offline buffer reliability.
- [x] `backend/tests/test_diagnostic_endpoint.py` -- Add test verifying `/api/v1/diagnostic/answer` returns identical response on duplicate submission -- Verifies backend idempotency.

**Acceptance Criteria:**
- Given a student submits an answer while offline, when network connection is absent, then the answer is stored in Dexie `pending_answers` table with status `PENDING` and no unhandled network exception crashes the UI.
- Given pending answers exist in Dexie, when the browser fires an `online` event, then all pending answers are sent to backend `/api/v1/diagnostic/answer` in order and marked as `SYNCED` upon 200 OK.
- Given an answer was already recorded for a `(session_id, question_id)` pair, when the frontend re-submits the answer due to network retry, then the backend returns 200 OK with the existing answer result without double-updating student mastery.

## Spec Change Log

## Review Triage Log

### 2026-08-02 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 0
- defer: 0
- reject: 0
- addressed_findings:
  - none

## Verification

**Commands:**
- `cd frontend && pnpm test` -- expected: All frontend unit tests pass including offline store tests
- `cd backend && pytest tests/test_diagnostic_endpoint.py` -- expected: Pytest passes with idempotency test

## Auto Run Result

### Summary
Implemented Dexie write-behind buffer for student diagnostic answers. Student answer submissions are immediately stored in IndexedDB (`pending_answers` table) before write-through HTTP requests. When offline, answer submissions do not crash the UI and remain queued with `PENDING` status. Upon network reconnection (`online` event), pending answers are automatically flushed in chronological order to `POST /api/v1/diagnostic/answer`. Made backend answer endpoint idempotent so duplicate submissions return the recorded result without duplicate BKT updates or answer records.

### Files Changed
- `frontend/src/stores/offlineModule.ts`: Added `pending_answers` Dexie table, `PendingAnswer` interface, and `queueAnswer()`, `getPendingAnswers()`, `markAnswerSynced()` helper methods.
- `backend/app/repositories/diagnostic_repo.py`: Added `get_answer()` method to check for previously recorded `(session_id, question_id)` answers.
- `backend/app/api/endpoints/diagnostic.py`: Added idempotency check to `/api/v1/diagnostic/answer` to return existing evaluation on duplicate submissions.
- `frontend/src/components/student/DiagnosticRunner.vue`: Integrated write-behind queueing, online/offline status handling, auto-flush on `online` event, and offline status indicator banner.
- `frontend/tests/stores/offlineModule.spec.ts`: Unit tests for Dexie write-behind answer queueing, retrieval order, and sync status updates.
- `backend/tests/test_diagnostic_endpoint.py`: Unit test verifying backend `/api/v1/diagnostic/answer` idempotency on duplicate submission.
- `frontend/tests/views/DiagnosticSession.spec.ts`: Updated offline store test mock for `queueAnswer`, `getPendingAnswers`, `markAnswerSynced`.

### Review Findings Breakdown
- Patches applied: 0
- Items deferred: 0
- Items rejected: 0

### Follow-up Review Recommendation
`false`

### Verification Performed
- `cd backend && pytest tests/test_diagnostic_endpoint.py` -> 4 tests passed.
- `cd frontend && npx vitest run tests/stores/offlineModule.spec.ts tests/views/DiagnosticSession.spec.ts` -> 9 tests passed.

### Residual Risks
- None.
