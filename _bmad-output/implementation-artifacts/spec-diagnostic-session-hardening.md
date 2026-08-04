---
title: 'Diagnostic Session Hardening'
type: 'bugfix'
created: '2026-08-04'
status: 'in-review'
baseline_revision: '38fcb4f2d277515cb818f31a51720b00f4cc3d1a'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
---

<intent-contract>

## Intent

**Problem:** Backend `POST /diagnostic/session/{session_id}/abandon` endpoint returns an inline dictionary `{"status": "success", "message": "Session abandoned"}` without a structured Pydantic schema response model (DW-19). Furthermore, `DiagnosticRepository.get_active_student_session` queries `DiagnosticSession` filtering by `IN_PROGRESS` and `.order_by(DiagnosticSession.started_at.desc())`, which lacks a deterministic tie-breaker (e.g. `id.desc()`) when multiple sessions share timestamps (DW-18).

**Approach:** Define `AbandonDiagnosticSessionResponse` schema in `app/schemas/diagnostic.py`, annotate `abandon_session` in `app/api/endpoints/diagnostic.py` with `response_model=AbandonDiagnosticSessionResponse`, and refine `get_active_student_session` query ordering in `app/repositories/diagnostic_repo.py` to order by `started_at.desc(), id.desc()`.

## Boundaries & Constraints

**Always:** Maintain HTTP 200 status code and JSON payload structure `{"status": "success", "message": "Session abandoned"}` for abandon endpoint. Enforce deterministic query ordering on active student session retrieval.

**Block If:** Schema additions require database migration or alter existing API response key contracts.

**Never:** Modify deferred-work ledger files directly.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Abandon session success | Valid in-progress session ID for current student | `AbandonDiagnosticSessionResponse` with status="success", message="Session abandoned" | 200 OK |
| Abandon non-existent session | Unknown session ID | 404 detail="Session not found" | HTTP 404 |
| Abandon completed/abandoned session | Session status != IN_PROGRESS | 400 detail="Session is not in progress" | HTTP 400 |
| Active session retrieval | Multiple sessions with same started_at timestamp | Most recent session deterministically selected via started_at desc, id desc tie-breaker | No error |

</intent-contract>

## Code Map

- `backend/app/schemas/diagnostic.py` -- Defines `AbandonDiagnosticSessionResponse` Pydantic response schema model.
- `backend/app/api/endpoints/diagnostic.py` -- Annotates `abandon_session` route with `response_model=AbandonDiagnosticSessionResponse`.
- `backend/app/repositories/diagnostic_repo.py` -- Refines `get_active_student_session` ordering query to include `DiagnosticSession.id.desc()`.
- `backend/tests/test_diagnostic_endpoint.py` -- Adds unit/integration test coverage for abandon session endpoint and active session query ordering.

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/schemas/diagnostic.py` -- Create `AbandonDiagnosticSessionResponse` model with `status: str = "success"` and `message: str = "Session abandoned"`.
- [x] `backend/app/api/endpoints/diagnostic.py` -- Add `response_model=AbandonDiagnosticSessionResponse` to `abandon_session` endpoint and update return statement to return `AbandonDiagnosticSessionResponse`.
- [x] `backend/app/repositories/diagnostic_repo.py` -- Update `get_active_student_session` query to order by `DiagnosticSession.started_at.desc(), DiagnosticSession.id.desc()`.
- [x] `backend/tests/test_diagnostic_endpoint.py` -- Add unit tests for `abandon_session` endpoint response validation and `get_active_student_session` query ordering tie-breaking.

**Acceptance Criteria:**
- Given an in-progress diagnostic session, when `POST /api/v1/diagnostic/session/{session_id}/abandon` is called, then it returns HTTP 200 with payload matching `AbandonDiagnosticSessionResponse`.
- Given a student with active diagnostic sessions, when `get_active_student_session` is executed, then results are ordered by `started_at DESC, id DESC`.

## Spec Change Log

## Review Triage Log

### 2026-08-04 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 0
- defer: 0
- reject: 0
- addressed_findings:
  - none

## Verification

**Commands:**
- `pytest backend/tests/test_diagnostic_endpoint.py` -- expected: All tests pass successfully.
