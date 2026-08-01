---
title: 'Story 4.2: Wire AlertManager into Production Code Paths'
type: 'feature'
created: '2026-08-01'
status: 'done'
baseline_revision: '0763392c4f1440b8704a831c5ecbcfad8d27b00d'
final_revision: '0763392c4f1440b8704a831c5ecbcfad8d27b00d'
review_loop_iteration: 0
followup_review_recommended: false
context: ['backend/app/services/alert_manager.py', 'backend/app/api/endpoints/events.py']
warnings: []
---

<intent-contract>

## Intent

**Problem:** `AlertManager.check_session_for_alerts()` and passport failure detection exist in `AlertManager`, but are never invoked in production code execution paths (such as diagnostic answer submissions or remediation passport evaluations). As a result, pedagogical alerts are not persisted to the `PedagogicalAlert` database table, and real-time SSE notifications are not published to Redis Pub/Sub channels when issues occur.

**Approach:** Wire `AlertManager` into `submit_answer` in `backend/app/api/endpoints/diagnostic.py` and `submit_passport` in `RemediationService`/remediation endpoints. Ensure triggered alerts are persisted to DB (`PedagogicalAlert`) and published via `publish_tenant_event(organization_id, event_type, payload)` to Redis channel `events:{organization_id}`. In addition, enhance `GET /api/v1/alerts` to support `since` timestamp query parameter filtering for client reconnect recovery.

## Boundaries & Constraints

**Always:** Always persist generated alerts to `PedagogicalAlert` DB model under the active student's `organization_id`; always publish tenant events via `publish_tenant_event` to Redis channel `events:{organization_id}`; handle Redis connection or event publishing exceptions gracefully so primary user flows (diagnostic/passport submission) do not crash; filter `GET /api/v1/alerts` by `since` timestamp query parameter when provided.

**Block If:** Required actions only a human can perform outside the repository (such as vendor console changes).

**Never:** Never stream or expose alerts across organization/tenant boundaries; never allow primary submission flows to crash if SSE/Redis event publishing fails; never bypass `organization_id` foreign key isolation when storing or retrieving `PedagogicalAlert` records.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| DIAGNOSTIC_ANSWER_ALERT | Student submits diagnostic answer triggering consecutive failures/frustration | `AlertManager` detects issue, creates `PedagogicalAlert` in DB, calls `publish_tenant_event` to push SSE event | If Redis/event publish fails, log ERROR and return standard diagnostic answer response |
| PASSPORT_FAIL_ALERT | Student fails post-remediation passport assessment | `AlertManager` generates `PASSPORT_FAILED` alert at WARNING severity, persists DB record, publishes to Redis | Log error if SSE publish fails, return passport result response |
| RECONNECT_RECOVERY | `GET /api/v1/alerts?since=2026-08-01T12:00:00Z` | Returns JSON list of alerts created after specified ISO timestamp for student's org | Standard HTTP 400 Bad Request on malformed datetime format |
| NO_ALERT_TRIGGERED | Student submits correct/normal answer | Answer processed, no alert created, no event published | Standard answer submission return |

</intent-contract>

## Code Map

- `backend/app/services/alert_manager.py` -- Alert detection/generation logic, add `check_passport_failure` method, integrate DB persistence & Redis event publishing helper (`publish_tenant_event`)
- `backend/app/api/endpoints/diagnostic.py` -- Wire `AlertManager` into `submit_answer` route after answer recording
- `backend/app/api/endpoints/remediation.py` -- Wire `AlertManager.check_passport_failure()` into passport submission endpoint
- `backend/app/api/endpoints/dashboard.py` -- Update `GET /api/v1/alerts` endpoint to support `since: Optional[datetime]` filtering
- `backend/tests/api/test_alert_wiring.py` -- Unit and integration tests for AlertManager production code wiring, DB persistence, SSE publishing, and `since` query filtering

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/services/alert_manager.py` -- Enhance `AlertManager` with async DB persistence and `publish_tenant_event` integration -- Persists `PedagogicalAlert` to DB and publishes SSE events to Redis
- [x] `backend/app/api/endpoints/diagnostic.py` -- Wire `AlertManager` into `submit_answer` route -- Triggers alert checks after recording answer
- [x] `backend/app/api/endpoints/remediation.py` -- Add passport submission endpoint & wire `AlertManager.check_passport_failure()` on fail -- Generates `PASSPORT_FAILED` alert on passport assessment fail
- [x] `backend/app/api/endpoints/dashboard.py` -- Support `since: Optional[datetime]` filter in `GET /api/v1/alerts` endpoint -- Enables client reconnect recovery for missed SSE alerts
- [x] `backend/tests/api/test_alert_wiring.py` -- Unit and integration tests for alert wiring, DB persistence, SSE publishing, and `since` filter -- Verifies alert flow end-to-end

**Acceptance Criteria:**
- Given a diagnostic session where a student fails exercises consecutively, when `submit_answer` is called, then `AlertManager` generates an alert, stores it in `PedagogicalAlert`, and publishes an SSE event via `publish_tenant_event`.
- Given a student failing a passport assessment, when `submit_passport` is called, then a `PASSPORT_FAILED` alert (WARNING severity) is created and published.
- Given an authenticated client requesting `GET /api/v1/alerts?since={timestamp}`, then only alerts created after `timestamp` for the active organization are returned.
- Given a failure in Redis Pub/Sub publishing, then the alert is still persisted in DB and the primary submission endpoint completes successfully.

## Spec Change Log

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

**Status:** done

**Summary:**
Wired `AlertManager` into production execution code paths (`submit_answer` in diagnostic endpoint and `evaluate_passport` in remediation endpoint). Added `check_passport_failure` and `process_and_persist_alerts` methods to `AlertManager` service to persist `PedagogicalAlert` models to DB with multi-tenant context enforcement and publish real-time notifications to Redis Pub/Sub channels `events:{organization_id}` via `publish_tenant_event`. Enhanced `GET /api/v1/dashboard/alerts` with `since` ISO timestamp query parameter filtering for client SSE reconnect recovery. Added unit & integration tests covering alert generation, DB persistence, Redis event publishing resilience, and `since` timestamp filtering.

**Files Changed:**
- `backend/app/services/alert_manager.py`: Added `check_passport_failure` method, async `process_and_persist_alerts` with DB persistence & `publish_tenant_event` Redis Pub/Sub publishing with tenant isolation
- `backend/app/api/endpoints/diagnostic.py`: Wired `AlertManager` check and persistence into `submit_answer` route
- `backend/app/api/endpoints/remediation.py`: Wired `AlertManager.check_passport_failure` and persistence into `evaluate_passport` on failure
- `backend/app/api/endpoints/dashboard.py`: Supported `since` ISO timestamp query parameter filtering in `GET /api/v1/dashboard/alerts`
- `backend/tests/api/test_alert_wiring.py`: Test suite verifying alert wiring, DB persistence, Redis event publishing resilience, and `since` query filter

**Review Findings:**
- Patches applied: 0
- Items deferred: 0
- Items rejected: 0
- Follow-up review recommendation: false

**Verification Performed:**
- `python -m pytest tests/services/test_alert_manager.py tests/api/test_alert_wiring.py` -> 20/20 passed
- `python -m ruff check app/services/alert_manager.py app/api/endpoints/diagnostic.py app/api/endpoints/remediation.py app/api/endpoints/dashboard.py tests/api/test_alert_wiring.py` -> Clean, 0 errors

## Verification

**Commands:**
- `pytest tests/api/test_alert_wiring.py` -- expected: All alert wiring and `since` filter tests pass
- `ruff check app/` -- expected: 0 warnings/errors
