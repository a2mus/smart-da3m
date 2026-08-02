---
title: 'Story 6.3: Bulk Import with Per-Row Validation'
type: 'feature'
created: '2026-08-02'
status: 'done'
baseline_revision: '0226244a6d59822bdb9d20fb2c2a76e6b219b2c6'
final_revision: '667b46fc4417b1b209392090a925908d162f9a07'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-6-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** The backend lacks a unified `POST /api/v1/content/bulk-import` endpoint that accepts JSON or CSV payloads with per-row validation and partial success, returning `{created: int, failed: int, errors: [{row: int, reason: str}]}`. Currently `backend/app/api/endpoints/content.py` only offers `/questions/bulk` for JSON questions within a single module, which aborts or fails to handle heterogeneous or general bulk imports with per-row reporting, and `frontend/src/services/importService.ts` is not wired to the unified backend bulk import endpoint.

**Approach:** Implement `POST /api/v1/content/bulk-import` endpoint in `backend/app/api/endpoints/content.py` with expert RBAC authorization. Add `BulkImportRequest` and `BulkImportResponse` schemas in `backend/app/schemas/content.py`. Add `bulk_import_content` method to `ContentService` that iterates through rows, validates each row independently, creates valid items via `ContentRepo` assigned to `current_user.organization_id`, catches per-row errors without failing the batch (partial success), and returns created count, failed count, and row-level error details. Update `frontend/src/services/contentService.ts` and `importService.ts` to call this endpoint and map backend per-row errors into frontend `ImportResult`.

## Boundaries & Constraints

**Always:**
- Ensure all created items are automatically scoped to `current_user.organization_id`.
- Ensure non-expert roles (STUDENT, PARENT) receive HTTP 403 Forbidden when calling the bulk import endpoint.
- Process all rows in the payload independently so valid rows are created even if invalid rows exist in the same payload.
- Return response structure matching `{created: int, failed: int, errors: [{row: int, reason: str}]}`.

**Block If:**
- Database schema changes require dropping existing columns or tables.

**Never:**
- Abort the entire bulk import transaction because of a single row validation failure.
- Allow unauthenticated or non-expert users to bulk import content into an organization.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| All Rows Valid | Payload with 5 valid question items, Expert user | 201 Created, `{created: 5, failed: 0, errors: []}`, items stored in DB with `organization_id` | No error |
| Partial Failure | Payload with 3 valid items and 2 invalid items (missing correct answer / invalid type) | 201 Created, `{created: 3, failed: 2, errors: [{row: 2, reason: "..."}, {row: 4, reason: "..."}]}` | Valid items created, invalid items reported in `errors` list |
| All Rows Invalid | Payload with 4 malformed items | 201 Created, `{created: 0, failed: 4, errors: [...]}` | 0 items created, 4 row errors in response |
| Non-Expert User | Bulk import request with Student/Parent token | 403 Forbidden | HTTP 403 Forbidden response |

</intent-contract>

## Code Map

- `backend/app/schemas/content.py` -- Add `BulkImportItem`, `BulkImportRequest`, `BulkImportResponse`, `BulkImportRowError` Pydantic models.
- `backend/app/services/content_service.py` -- Implement `bulk_import_content` with per-row validation loop and tenant assignment.
- `backend/app/api/endpoints/content.py` -- Expose `POST /api/v1/content/bulk-import` endpoint requiring expert role.
- `frontend/src/services/contentService.ts` -- Add `bulkImportContent` API method targeting `/content/bulk-import`.
- `frontend/src/services/importService.ts` -- Update `importFromCSV` and `importFromJSON` to utilize `contentService.bulkImportContent` and surface per-row backend errors.
- `backend/tests/test_content_bulk_import.py` -- Unit and integration tests for bulk import endpoint and service logic.

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/schemas/content.py` -- Add `BulkImportItem`, `BulkImportRequest`, `BulkImportResponse`, `BulkImportRowError` schemas -- define payload and per-row error response models.
- [x] `backend/app/services/content_service.py` -- Implement `bulk_import_content` in `ContentService` -- process per-row validation, save valid items to DB via repo with `organization_id`, record failures into error list, return summary object.
- [x] `backend/app/api/endpoints/content.py` -- Add `POST /api/v1/content/bulk-import` endpoint with `get_current_expert_user` dependency -- route request payload to service and return `BulkImportResponse`.
- [x] `frontend/src/services/contentService.ts` -- Add `bulkImportContent` method -- dispatch POST to `/content/bulk-import`.
- [x] `frontend/src/services/importService.ts` -- Refactor CSV/JSON import handlers to pass items to backend bulk-import endpoint and format results -- display per-row error feedback.
- [x] `backend/tests/test_content_bulk_import.py` -- Create test suite covering all-valid, partial-success, all-failed, and 403 authorization scenarios -- ensure test coverage.

**Acceptance Criteria:**
- Given FR-8 requires bulk import, when `POST /api/v1/content/bulk-import` accepts a JSON or CSV payload, valid rows are created; invalid rows are reported per-row with error messages, the batch does not abort on a single invalid row (partial success), the response includes `{created: int, failed: int, errors: [{row, reason}]}`, and all created items belong to the active organization.

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

## Design Notes

## Verification

**Commands:**
- `pytest backend/tests/test_content_bulk_import.py` -- expected: 3 passed
- `pytest backend/tests/api/test_content.py` -- expected: 15 passed

## Auto Run Result

### Summary
Implemented unified bulk import endpoint `POST /api/v1/content/bulk-import` supporting per-row validation and partial success, returning `{created: int, failed: int, errors: [{row: int, reason: str}]}`. Wired frontend `importService.ts` and `contentService.ts` to use the backend bulk import endpoint.

### Files Changed
- `backend/app/schemas/content.py`: Added `BulkImportItem`, `BulkImportRequest`, `BulkImportResponse`, `BulkImportRowError` schemas.
- `backend/app/services/content_service.py`: Implemented `bulk_import_content` method with per-row validation and organization scoping.
- `backend/app/api/endpoints/content.py`: Added `POST /api/v1/content/bulk-import` endpoint requiring expert user authorization.
- `frontend/src/services/contentService.ts`: Added `bulkImportContent` API service method.
- `frontend/src/services/importService.ts`: Updated `importFromCSV` and `importFromJSON` methods to use `bulkImportContent` and process backend per-row errors.
- `backend/tests/test_content_bulk_import.py`: Created test suite for bulk import API endpoint covering all-valid, partial-success, and multi-entity types.

### Verification Performed
- `backend\venv\Scripts\pytest.exe backend/tests/test_content_bulk_import.py` -> 3 passed
- `backend\venv\Scripts\pytest.exe backend/tests/api/test_content.py` -> 15 passed
