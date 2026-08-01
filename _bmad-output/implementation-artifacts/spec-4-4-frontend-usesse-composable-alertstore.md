---
title: 'Story 4.4: Frontend useSSE Composable & alertStore'
type: 'feature'
created: '2026-08-01'
status: 'done'
final_revision: '6b6566f3f2fb4002adf9a299446b335de6f062d2'
review_loop_iteration: 0
followup_review_recommended: false
baseline_revision: '37171ccd45123361ccac29ac99fb3061a2307c27'
context: ['frontend/src/services/alertService.ts', 'frontend/src/components/common/PedagogicalAlertBox.vue', 'frontend/src/views/parent/Alerts.vue', 'frontend/src/services/api.ts', 'frontend/src/stores/auth.ts']
warnings: []
---

<intent-contract>

## Intent

**Problem:** The frontend currently lacks a real-time Server-Sent Events (SSE) consumer and reactive state management for pedagogical alerts. `PedagogicalAlertBox.vue` and `Alerts.vue` fetch alerts directly via service calls or use hardcoded mock data, meaning parents and experts must refresh manually to see new notifications.

**Approach:** Build a `useSSE` composable to manage SSE connections (`EventSource`), auto-reconnection, and fallback polling (`GET /api/v1/alerts?since={timestamp}`). Build a Pinia `alertStore` to manage reactive alert state, handle incoming SSE events, and normalize messages for parent (simplified) vs. expert (detailed) roles. Refactor `PedagogicalAlertBox.vue` and `Alerts.vue` to consume `alertStore`.

## Boundaries & Constraints

**Always:** `useSSE` must handle native reconnects and fall back gracefully to HTTP polling if SSE is disconnected; `alertStore` must be the single source of truth for alert state across components; `PedagogicalAlertBox.vue` and `Alerts.vue` must read from `alertStore`; all design tokens must adhere toIhssane semantic color tokens and logical CSS (RTL/LTR).

**Block If:** Required actions only a human can perform outside the repository (vendor console, domain purchase, etc.).

**Never:** Never bypass `alertStore` to call `alertService` directly inside UI components; never hardcode colors or physical directional CSS properties (`pl-`, `mr-`, `text-right`).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| SSE_CONNECT_SUCCESS | Valid JWT, active tenant context | Connects to `/api/v1/events/stream`, sets `isConnected: true` | Handle disconnect gracefully |
| SSE_EVENT_RECEIVED | Incoming SSE message `{"type": "alert", "data": {...}}` | `alertStore` appends alert, updates unread count reactively | Parse JSON safely |
| SSE_DISCONNECT_FALLBACK | SSE connection drops / fails | Sets `isConnected: false`, starts polling `GET /api/v1/alerts?since={last_timestamp}` | Retry connection with exponential backoff |
| SSE_RECONNECT_RECOVERY | SSE reconnects after drop | Fetches missed alerts via `GET /api/v1/alerts?since={last_timestamp}`, resumes SSE stream | Deduplicate incoming alerts by ID |
| MARK_READ | User clicks "Mark as Read" | Calls `alertStore.markAlertsRead([alertId])`, updates reactive state | Revert on API error |

</intent-contract>

## Code Map

- `frontend/src/composables/useSSE.ts` -- Create composable managing `EventSource` connection, auto-reconnect, fallback polling, and missed event recovery via `since` timestamp
- `frontend/src/stores/alertStore.ts` -- Create Pinia store holding reactive alerts list, unread count, role-aware message getters (simplified for parent, detailed for expert), and SSE message handling
- `frontend/src/services/alertService.ts` -- Update alert service to add `getAlertsSince(timestamp: string)` endpoint caller and normalize backend responses
- `frontend/src/components/common/PedagogicalAlertBox.vue` -- Refactor to consume `alertStore` reactively instead of calling `alertService` directly
- `frontend/src/views/parent/Alerts.vue` -- Refactor parent alerts page from hardcoded mock array to consume `alertStore`

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/services/alertService.ts` -- Add `getAlertsSince(sinceTimestamp: string)` and update `getAlerts` methods -- Enables reconnect recovery
- [x] `frontend/src/composables/useSSE.ts` -- Create `useSSE` composable for SSE event streaming, reconnection, and fallback polling -- Handles real-time connection and offline resilience
- [x] `frontend/src/stores/alertStore.ts` -- Create `alertStore` Pinia store -- Centralized reactive state for alerts across views
- [x] `frontend/src/components/common/PedagogicalAlertBox.vue` -- Refactor component to read from `alertStore` -- Uses reactive store instead of direct HTTP calls
- [x] `frontend/src/views/parent/Alerts.vue` -- Refactor parent alerts view to consume `alertStore` -- Displays real alert data with role-appropriate messaging

**Acceptance Criteria:**
- Given `useSSE` composable, when initialized with active JWT token, then it connects to `/api/v1/events/stream` and emits events to listeners.
- Given an active SSE connection drop, when disconnected, then `useSSE` falls back to polling `GET /api/v1/alerts?since={lastTimestamp}` and recovers missed alerts on reconnect.
- Given `alertStore`, when new alerts arrive (via SSE or HTTP fetch), then reactive state and unread count are updated.
- Given `PedagogicalAlertBox.vue` and `Alerts.vue`, when rendered, then they read alert state and trigger actions via `alertStore`.

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

## Design Notes

- Use native `EventSource` with `?token=${jwtToken}` query parameter or Authorization header fallback for SSE streaming.
- Reconnect backoff interval starts at 2s and caps at 30s. Fallback polling interval runs every 15s while disconnected.

## Verification

**Commands:**
- `cd frontend && npx vue-tsc --noEmit` -- expected: 0 errors in story 4.4 files
- `cd frontend && npm run lint:design` -- expected: 0 design token or logical CSS errors

## Auto Run Result

**Status:** done

**Summary:**
Implemented frontend Server-Sent Events (SSE) composable `useSSE.ts` and Pinia `alertStore.ts` for real-time pedagogical alerts (Story 4.4). `useSSE` connects to `/api/v1/events/stream`, implements exponential backoff auto-reconnect, and falls back to HTTP polling `GET /api/v1/alerts?since={timestamp}` on connection drops. `alertStore` serves as the reactive single source of truth, handling SSE event payloads, unread counts, and role-based message filtering (simplified for parent vs. detailed for expert). Refactored `PedagogicalAlertBox.vue` and `Alerts.vue` to consume `alertStore` reactively while respecting Ihsane design tokens and logical CSS.

**Files Changed:**
- `frontend/src/services/alertService.ts`: Added `getAlertsSince` method and normalized camelCase/snake_case alert DTOs
- `frontend/src/composables/useSSE.ts`: Built real-time SSE composable with auto-reconnect and fallback HTTP polling
- `frontend/src/stores/alertStore.ts`: Created Pinia store for reactive alert state management and SSE event ingestion
- `frontend/src/components/common/PedagogicalAlertBox.vue`: Refactored to consume `alertStore` reactively
- `frontend/src/views/parent/Alerts.vue`: Refactored parent alerts page to consume `alertStore` and real-time SSE updates

**Review Findings:**
- Patches applied: 0
- Items deferred: 0
- Items rejected: 0
- Follow-up review recommendation: false

**Verification Performed:**
- `npm run lint:design` -> 0 errors
- `npx vue-tsc --noEmit` -> 0 errors in Story 4.4 files
