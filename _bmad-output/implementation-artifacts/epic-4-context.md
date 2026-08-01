# Epic 4 Context: Real-Time Pedagogical Alerts & Notifications

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

The platform detects persistent difficulty and raises severity-tiered alerts (INFO/WARNING/CRITICAL), pushed in real time to parents and experts via Server-Sent Events (SSE). Parents receive simplified messages; experts receive detailed pedagogical context, and the orphaned AlertManager is wired into production code paths.

## Stories

- Story 4.1: SSE Endpoint & sse-starlette Integration
- Story 4.2: Wire AlertManager into Production Code Paths
- Story 4.3: Alert Trigger Thresholds (Resolve OQ-4)
- Story 4.4: Frontend useSSE Composable & alertStore

## Requirements & Constraints

- FR-27: Generate pedagogical alerts and push via SSE in real time.
- AD-5: SSE via Redis Pub/Sub per tenant (organization_id).
- Caddy reverse proxy must exclude `/api/v1/events/stream` from gzip/zstd compression buffer.
- Alerts must be persisted to `PedagogicalAlert` DB model for reconnect recovery via `GET /api/v1/alerts?since={timestamp}`.
- Authenticated endpoint: JWT validated on SSE connection.

## Technical Decisions

- Use `sse-starlette` for FastAPI `EventSourceResponse` endpoint.
- Redis Pub/Sub channels keyed by `organization_id`.
- Reconnect recovery supported via query parameter `since`.

## Cross-Story Dependencies

- Story 4.1 provides the SSE backend endpoint and Redis Pub/Sub bridge.
- Story 4.2 wires AlertManager to publish to Redis Pub/Sub and DB.
- Story 4.3 configures threshold triggers used by AlertManager.
- Story 4.4 builds the frontend `useSSE` composable and Pinia `alertStore`.
