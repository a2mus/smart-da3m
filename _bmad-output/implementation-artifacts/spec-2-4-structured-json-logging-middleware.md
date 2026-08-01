---
title: 'Story 2.4: Structured JSON Logging Middleware'
type: 'feature'
created: '2026-08-01'
status: 'done'
baseline_revision: '2b454a8a9fe8bb782bb23034498cd051f5a722f8'
final_revision: 'fcbe21bde2e250fc7224e86a00f6f7fc8e004287'
review_loop_iteration: 0
followup_review_recommended: false
context: ['backend/app/main.py', 'backend/app/core/tenant_middleware.py', 'backend/app/core/tenant.py', 'backend/app/core/config.py']
warnings: []
---

<intent-contract>

## Intent

**Problem:** The backend lacks structured JSON logging and request tracing middleware. HTTP requests, status codes, execution durations, and tenant/user IDs are unformatted or missing from logs, violating NFR-OBSERVABILITY and impeding production troubleshooting.

**Approach:** Implement a custom FastAPI/Starlette `LoggingMiddleware` and Python logging configuration that assigns a unique UUID `request_id` to every request, extracts `user_id` and `organization_id` from request state / JWT, logs every HTTP request in structured JSON format with execution duration, attaches the `X-Request-ID` header to responses, and logs errors with stack traces at ERROR level without leaking PII.

## Boundaries & Constraints

**Always:** Every HTTP request log entry must be formatted as valid JSON with fields: `request_id`, `user_id`, `organization_id`, `method`, `path`, `status_code`, `duration_ms`. The response must include `X-Request-ID` header. Exceptions must be logged at ERROR level with stack traces.

**Block If:** Any logging requirement asks to log full request payloads or response bodies that contain student answers, names, passwords, or emails.

**Never:** Include PII (student names, email addresses, passwords, PINs, or raw diagnostic answers) in log outputs.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Standard Request | Request with valid token & `X-Organization-Id` | JSON log entry containing `request_id`, `user_id`, `organization_id`, `method`, `path`, `status_code`, `duration_ms`; `X-Request-ID` header attached to response | No error expected |
| Public Unauthenticated Request | Request to `/health` or public route | JSON log entry with `request_id`, `user_id=null`, `organization_id=null`, `status_code=200`, `duration_ms` | No error expected |
| Server Exception | Request triggering unhandled Exception | JSON log entry with `request_id`, `status_code=500`, stack trace logged at `ERROR` level | Returns 500 response while retaining `X-Request-ID` header |

</intent-contract>

## Code Map

- `backend/app/core/logging_middleware.py` -- Middleware implementation, JSON log formatter, and request context contextvars
- `backend/app/main.py` -- Middleware registration order in FastAPI app
- `backend/tests/core/test_logging_middleware.py` -- Unit tests for structured JSON logging, header propagation, and error logging

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/core/logging_middleware.py` -- Implement JSON formatter and `LoggingMiddleware` -- Assign `request_id`, extract tenant/user context, format JSON logs with duration_ms, and attach `X-Request-ID` response header
- [x] `backend/app/main.py` -- Register `LoggingMiddleware` in FastAPI application pipeline -- Ensure proper middleware execution order
- [x] `backend/tests/core/test_logging_middleware.py` -- Create unit tests for logging middleware -- Test JSON output format, `X-Request-ID` header presence, user/org context extraction, and error stack trace logging

**Acceptance Criteria:**
- Given an incoming HTTP request
- When `LoggingMiddleware` processes the request
- Then a unique UUID `request_id` is created and returned in the `X-Request-ID` response header
- And a log entry is emitted as valid JSON with `request_id`, `user_id`, `organization_id`, `method`, `path`, `status_code`, and `duration_ms`
- And unhandled exceptions log full stack traces at `ERROR` log level
- And no PII (names, emails, PINs, diagnostic answers) is written to logs
- And all unit tests in `backend/tests/core/test_logging_middleware.py` pass

## Verification

**Commands:**
- `pytest backend/tests/core/test_logging_middleware.py` -- expected: all tests pass

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

### Summary of Implemented Changes
Implemented `LoggingMiddleware` in `backend/app/core/logging_middleware.py` and registered it in `backend/app/main.py`. The middleware generates a UUID `request_id` for every incoming HTTP request, extracts `user_id` from Bearer tokens and `organization_id` from tenant context/headers, logs valid JSON records with execution duration (`duration_ms`), returns the `X-Request-ID` header in responses, and logs server errors with stack traces at `ERROR` log level without leaking PII. Created unit test suite in `backend/tests/core/test_logging_middleware.py`.

### Files Changed
- `backend/app/core/logging_middleware.py`: JSON log formatter, request_id tracking, tenant/user context extraction, and `LoggingMiddleware` implementation.
- `backend/app/main.py`: Registered `LoggingMiddleware` in the FastAPI middleware stack.
- `backend/tests/core/test_logging_middleware.py`: Unit tests covering JSON format, header propagation, context extraction, and error logging.
- `_bmad-output/implementation-artifacts/spec-2-4-structured-json-logging-middleware.md`: Spec file tracking implementation, verification, and review results.

### Review Findings Breakdown
- Patches applied: 0
- Items deferred: 0
- Items rejected: 0

### Follow-up Review Recommendation
`false`

### Verification Performed
- Executed `pytest tests/core/test_logging_middleware.py tests/core/test_tenant_middleware.py` in `backend`: 10 passed out of 10 tests.

### Residual Risks
None.
