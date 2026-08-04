---
title: 'DW-20: Rate limiting for Child PIN update endpoint'
type: 'feature'
created: '2026-08-04'
status: 'done'
baseline_revision: 'c80d38deb303a865da967d3a94bdc0613831b94f'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/project-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** The `POST /api/v1/auth/children/{id}/pin` endpoint lacks brute-force rate-limiting protection, leaving PIN configuration vulnerable to rapid automated attempts.

**Approach:** Implement rate limiting on `POST /api/v1/auth/children/{id}/pin` using an in-memory rate limiting mechanism (similar to `sync.py`) to enforce a maximum allowed rate of requests per user/child, protecting against brute-force attacks and returning HTTP 429 Too Many Requests when exceeded.

## Boundaries & Constraints

**Always:** Enforce rate limit per parent user (or targeted child) on `POST /api/v1/auth/children/{id}/pin`, return HTTP 429 Too Many Requests on overflow, and allow resetting the store for test isolation.

**Block If:** Breaking existing authentication flows or modifying database schemas.

**Never:** Allow unlimited PIN update requests on the child PIN endpoint.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | 1-5 requests within window | 200 OK with updated UserResponse | No error expected |
| RATE_EXCEEDED | Exceeding 5 requests / min per parent | HTTP 429 Too Many Requests | Return 429 status code with rate limit error message |

</intent-contract>

## Code Map

- `backend/app/api/endpoints/auth.py` -- Add rate limit enforcement to `reset_child_pin` endpoint and expose store reset helper for tests.
- `backend/tests/api/test_parent_pin.py` -- Add unit test for rate limiting behavior (HTTP 429).

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/api/endpoints/auth.py` -- Add rate limit enforcement to `reset_child_pin` endpoint.
- [x] `backend/tests/api/test_parent_pin.py` -- Add unit test `test_reset_child_pin_rate_limiting` for HTTP 429 handling.

**Acceptance Criteria:**
- Given an authenticated parent user sending multiple rapid requests to `POST /api/v1/auth/children/{id}/pin`, when the threshold is exceeded, then HTTP 429 Too Many Requests is returned.

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
- `pytest backend/tests/api/test_parent_pin.py` -- expected: All 6 PIN endpoint tests pass (including rate limiting).

## Auto Run Result

### Summary
Implemented rate limiting protection on `POST /api/v1/auth/children/{id}/pin` endpoint (DW-20) to defend against brute-force child PIN update attempts.

### Files Changed
- `backend/app/api/endpoints/auth.py`: Added in-memory rate limiter `enforce_pin_rate_limit` (max 5 requests/min per parent user), integrated into `reset_child_pin`, and exposed `reset_pin_rate_limit_store` helper.
- `backend/tests/api/test_parent_pin.py`: Added `test_reset_child_pin_rate_limiting` verifying HTTP 429 when threshold is exceeded.
- `_bmad-output/implementation-artifacts/spec-auth-pin-rate-limiting.md`: Feature specification and execution log.

