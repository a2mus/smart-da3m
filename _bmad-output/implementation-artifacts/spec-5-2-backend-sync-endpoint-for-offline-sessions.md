---
title: 'Story 5.2: Backend Sync Endpoint for Offline Sessions'
type: 'feature'
created: '2026-08-02'
status: 'done'
baseline_revision: '2bcfee66cfa248095f476cfe52818e1e472b84f1'
final_revision: 'ab0845859186a38e778c0226caea7b97b8dc4611'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-5-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** Frontend offline operations queue answers and atom completions locally in Dexie during connectivity loss, but no unified batch sync endpoint `/api/v1/sync/batch` exists to process queued items upon reconnection.

**Approach:** Build `POST /api/v1/sync/batch` endpoint accepting `{answers: [...], completions: [...], since: timestamp}`. Implement idempotent processing per item, last-write-wins conflict resolution for atom completions, server-authoritative state transitions, rate limiting, and return `{accepted: int, rejected: int, errors: [{id, reason}]}`.

## Boundaries & Constraints

**Always:**
- Process each item in the batch independently so a single failure does not abort valid items.
- Ensure atom completions are idempotent (last-write-wins) and diagnostic answers handle duplicate client-generated submissions safely.
- Server state machine remains authoritative for pathway state transitions.
- Return `{accepted: int, rejected: int, errors: [{id: str, reason: str}]}` response format.
- Protect `/api/v1/sync/batch` with rate limiting.

**Block If:**
- Required backend data models require un-migrated DB schema changes breaking existing repositories.

**Never:**
- Allow a single item error to fail the entire batch request (partial success model).
- Overwrite server-authoritative state transitions with stale client states.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Valid Batch Sync | `POST /api/v1/sync/batch` with 2 valid pending answers and 1 atom completion | All items processed successfully; returns `{accepted: 3, rejected: 0, errors: []}` | None |
| Duplicate Re-sync | `POST /api/v1/sync/batch` with previously synced answer or atom completion ID | Processed idempotently without duplicating DB records; returns accepted | Idempotent skip, returns accepted |
| Partial Item Error | Batch contains 1 valid answer and 1 invalid `question_id` | Valid answer accepted, invalid item reported in `errors`; returns `{accepted: 1, rejected: 1, errors: [{id, reason}]}` | Record item in error list without rolling back valid items |
| Rate Limit Exceeded | Rapid repeated requests to `/api/v1/sync/batch` | HTTP 429 Too Many Requests | Rate limit handler rejects request |

</intent-contract>

## Code Map

- `backend/app/schemas/sync.py` -- Define `SyncBatchRequest`, `SyncBatchResponse`, `SyncAnswerItem`, `SyncCompletionItem`, and `SyncErrorDetail` Pydantic schemas.
- `backend/app/repositories/sync_repo.py` -- Create `SyncRepository` handling idempotent batch answer submissions and batch atom completions.
- `backend/app/api/endpoints/sync.py` -- Create router for `POST /api/v1/sync/batch` with rate limiting, tenant filtering, and response reporting.
- `backend/app/main.py` -- Register `sync.router` under `/api/v1/sync` prefix.
- `backend/tests/test_sync_endpoint.py` -- Pytest suite for batch sync processing, idempotency, partial success handling, and rate limiting.

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/schemas/sync.py` -- Create Pydantic models `SyncBatchRequest`, `SyncBatchResponse`, `SyncAnswerItem`, `SyncCompletionItem`, `SyncErrorDetail` -- Establishes validation schema for offline batch sync.
- [x] `backend/app/repositories/sync_repo.py` -- Create repository to process answers and atom completions idempotently with last-write-wins semantics -- Encapsulates batch DB logic.
- [x] `backend/app/api/endpoints/sync.py` -- Implement `POST /api/v1/sync/batch` endpoint with rate-limiting and error collecting -- Provides API endpoint for frontend offline queue flushes.
- [x] `backend/app/main.py` -- Include `sync.router` with `/api/v1/sync` prefix and tag `sync` -- Exposes sync API.
- [x] `backend/tests/test_sync_endpoint.py` -- Add unit tests for batch sync, duplicate processing, partial failure, and rate limiting -- Verifies API behavior and idempotency.

**Acceptance Criteria:**
- Given no `/api/v1/sync` endpoint exists, when the sync endpoint is built, then `POST /api/v1/sync/batch` accepts `{answers: [...], completions: [...], since: timestamp}`.
- Given batched offline items are submitted, when processing items, then each item is processed idempotently (duplicate detection by client ID / session_id + question_id) and returns `{accepted: int, rejected: int, errors: [{id: str, reason: str}]}`.
- Given atom completions and state transitions are synced, when conflicts arise, then atom completions use last-write-wins and state transitions treat server state machine as authoritative.
- Given rate-limiting is applied, when excessive requests hit `/api/v1/sync/batch`, then HTTP 429 Too Many Requests is returned.

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
- `cd backend && pytest tests/test_sync_endpoint.py` -- expected: All pytest unit tests pass for batch sync endpoint

## Auto Run Result

### Summary
Implemented the backend offline batch synchronization endpoint `POST /api/v1/sync/batch` for Story 5.2. The endpoint accepts batched diagnostic answer submissions and knowledge atom completions queued during client network drops. It processes items independently and idempotently (last-write-wins for atom completions, returning accepted for duplicate diagnostic answers without double BKT updates). Applied rate limiting (30 requests/minute per student) and returned standard batch processing summary `{accepted: int, rejected: int, errors: [{id, reason}]}`.

### Files Changed
- `backend/app/schemas/sync.py`: Created Pydantic models `SyncBatchRequest`, `SyncBatchResponse`, `SyncAnswerItem`, `SyncCompletionItem`, and `SyncErrorDetail`.
- `backend/app/repositories/sync_repo.py`: Created `SyncRepository` handling idempotent batch answer submissions and batch atom completions.
- `backend/app/api/endpoints/sync.py`: Created endpoint `POST /api/v1/sync/batch` with in-memory rate limiting and error detail collection.
- `backend/app/main.py`: Registered `sync.router` under `/api/v1/sync` prefix.
- `backend/tests/test_sync_endpoint.py`: Created unit tests for batch sync processing, idempotency, partial success handling, and rate limiting.

### Review Findings Breakdown
- Patches applied: 0
- Items deferred: 0
- Items rejected: 0

### Follow-up Review Recommendation
`false`

### Verification Performed
- `cd backend && venv\Scripts\python.exe -m pytest tests/test_sync_endpoint.py` -> 3 tests passed in 0.21s.

### Residual Risks
- None.
