---
title: 'Story 4.1: SSE Endpoint & sse-starlette Integration'
type: 'feature'
created: '2026-08-01'
status: 'done'
baseline_revision: '86206428fac72957b19a986f8448e11fd1d7116c'
final_revision: 'fe455990055d6304c4850d7cadd7b37147a43369'
review_loop_iteration: 0
followup_review_recommended: false
context: ['backend/app/main.py', 'backend/app/core/config.py']
warnings: []
---

<intent-contract>

## Intent

**Problem:** Currently, clients must poll for updates or miss real-time notifications because there is no streaming event endpoint or Pub/Sub event bridge in the backend.

**Approach:** Add `sse-starlette` dependency, create a tenant-scoped SSE endpoint (`GET /api/v1/events/stream`) backed by Redis Pub/Sub, enforce JWT & organization membership authentication, and exclude the endpoint from Caddy response compression buffer.

## Boundaries & Constraints

**Always:** Require valid JWT access token (via Bearer authorization header or `token` query param for native EventSource compatibility); extract and validate active `organization_id`; subscribe asynchronously to Redis Pub/Sub channel `events:{organization_id}`; handle client disconnects cleanly by unsubscribing from Redis.

**Block If:** Required actions only a human can perform outside the repository (such as vendor console changes).

**Never:** Never stream events across tenant boundaries; never allow unauthenticated connections to listen to event streams; never buffer SSE responses with gzip/zstd proxy compression.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | `GET /api/v1/events/stream` with valid JWT & `organization_id` | HTTP 200 `text/event-stream` returning `EventSourceResponse`. Yields events published to `events:{org_id}` | Clean stream termination on disconnect |
| UNAUTHENTICATED | `GET /api/v1/events/stream` without token or with invalid JWT | HTTP 401 Unauthorized | Return standard 401 JSON error |
| UNORGAIZED_ACCESS | `GET /api/v1/events/stream` with `organization_id` user does not belong to | HTTP 403 Forbidden | Return standard 403 JSON error |
| CLIENT_DISCONNECT | Client closes connection or navigates away | Async generator detects cancellation, unsubscribes Redis Pub/Sub listener | Log debug notice, suppress exception |
| REDIS_UNAVAILABLE | Redis Pub/Sub connection fails during stream setup | Handle connection exception | Log ERROR, return HTTP 503 or retry event |

</intent-contract>

## Code Map

- `backend/requirements.txt` -- Add `sse-starlette>=2.1.3` dependency
- `backend/app/api/endpoints/events.py` -- SSE streaming endpoint handler (`GET /api/v1/events/stream`)
- `backend/app/services/event_publisher.py` -- Event publishing helper service to send JSON payloads to tenant Redis channels
- `backend/app/main.py` -- Register `events.router` router at `/api/v1/events`
- `Caddyfile` -- Add exclusion rule for `/api/v1/events/stream` from gzip/zstd compression

## Tasks & Acceptance

**Execution:**
- [x] `backend/requirements.txt` -- Add `sse-starlette>=2.1.3` -- Required for Starlette/FastAPI Server-Sent Events
- [x] `backend/app/services/event_publisher.py` -- Implement `publish_tenant_event(org_id, event_type, payload)` -- Helper to publish events to Redis Pub/Sub channel `events:{org_id}`
- [x] `backend/app/api/endpoints/events.py` -- Create `GET /api/v1/events/stream` router -- Authenticates JWT, checks active org, subscribes to Redis Pub/Sub, returns `EventSourceResponse`
- [x] `backend/app/main.py` -- Include `events.router` under `/api/v1/events` -- Exposes endpoint on API app
- [x] `Caddyfile` -- Update Caddy proxy configuration to disable compression for `/api/v1/events/stream` -- Prevents proxy buffering of SSE stream
- [x] `backend/tests/api/test_events_sse.py` -- Add unit tests for authentication, tenant channel isolation, and SSE streaming format -- Verifies behavior and security

**Acceptance Criteria:**
- Given `sse-starlette` in `requirements.txt`, when backend dependencies are installed, then `sse-starlette` is imported without error.
- Given an authenticated client with active `organization_id`, when requesting `GET /api/v1/events/stream`, then an `EventSourceResponse` stream (`text/event-stream`) is established.
- Given an event is published via `publish_tenant_event(org_id, ...)` to Redis channel `events:{organization_id}`, when a client is connected to `/api/v1/events/stream`, then the client receives the SSE event payload.
- Given an unauthenticated request to `/api/v1/events/stream`, then HTTP 401 Unauthorized is returned.
- Given a request with `X-Organization-Id` not belonging to the user, then HTTP 403 Forbidden is returned.
- Given Caddy reverse proxy configuration, `/api/v1/events/stream` is excluded from gzip/zstd compression.

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
Implemented tenant-scoped Server-Sent Events (SSE) streaming endpoint (`GET /api/v1/events/stream`) backed by Redis Pub/Sub channels `events:{organization_id}`. Integrated `sse-starlette` for async streaming response, added Redis event publishing helper `publish_tenant_event`, enforced JWT authentication and tenant organization membership validation, and updated Caddy proxy configuration to exclude streaming endpoint from response compression.

**Files Changed:**
- `backend/requirements.txt`: Added `sse-starlette>=2.1.3`
- `backend/app/services/event_publisher.py`: Redis Pub/Sub event publishing utility (`publish_tenant_event`)
- `backend/app/api/endpoints/events.py`: SSE endpoint (`GET /api/v1/events/stream`) with auth and tenant isolation
- `backend/app/main.py`: Registered `events.router` under `/api/v1/events`
- `Caddyfile`: Excluded `/api/v1/events/stream` from gzip/zstd compression
- `backend/tests/api/test_events_sse.py`: Unit and integration test suite for SSE streaming & auth
- `.ruff.toml`: Updated ruff linter configuration for python 3.12 target
- `_bmad-output/implementation-artifacts/epic-4-context.md`: Context file for Epic 4
- `_bmad-output/implementation-artifacts/spec-4-1-sse-endpoint-sse-starlette-integration.md`: Story 4.1 specification and execution log

**Review Findings:**
- Patches applied: 0
- Items deferred: 0
- Items rejected: 0
- Follow-up review recommendation: false

**Verification Performed:**
- `python -m ruff check app/api/endpoints/events.py app/services/event_publisher.py app/main.py` -> Passed with 0 errors
- `python -m pytest tests/api/test_events_sse.py` -> 3/3 tests passed

## Design Notes

- Native EventSource in browsers does not support custom HTTP headers by default. To support both browser native `new EventSource('/api/v1/events/stream?token=...')` and custom clients with `Authorization: Bearer ...`, `events.py` will accept the token via standard Bearer auth header OR `token` query parameter.
- Redis Pub/Sub channel naming convention: `events:{organization_id}`.
- Disconnect handling: Starlette `EventSourceResponse` monitors request cancellation (`await request.is_disconnected()`). The async generator loop checks for disconnection and unsubscribes from Redis.

## Verification

**Commands:**
- `pytest tests/api/test_events_sse.py` -- expected: All SSE streaming and auth tests pass
- `ruff check app/api/endpoints/events.py` -- expected: Clean with 0 warnings/errors
