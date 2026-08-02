---
title: 'Story 5.4: useOfflineSync Composable'
type: 'feature'
created: '2026-08-02'
status: 'done'
baseline_revision: 'e659f8b70dd954a31814da1fb4537a3e43b3cc00'
final_revision: '4c8c4d72345b2a3350d938b2103697cfbe1e8c88'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-5-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** Diagnostic and remediation Vue views directly duplicate connectivity event listeners, Dexie store operations, and manual answer sync flushing logic across multiple components.

**Approach:** Create a central Vue 3 composable `useOfflineSync.ts` encapsulating `isOnline`, `pendingCount`, `isSyncing`, `syncNow()`, `queueAnswer()`, `queueCompletion()`, and Service Worker background sync registration, then refactor `DiagnosticRunner.vue` and `RemediationSession.vue` to consume this composable.

## Boundaries & Constraints

**Always:**
- Use Vue Composition API (`ref`, `computed`, `onMounted`, `onUnmounted`) and maintain reactivity for `isOnline` and `pendingCount`.
- Listen to window `online` / `offline` events and update `isOnline` state accordingly.
- Keep wire format camelCase to snake_case boundary transforms handled properly.

**Block If:**
- Implementing offline features requires altering backend database schemas or non-student user roles.

**Never:**
- Duplicate `window.addEventListener('online', ...)` or Dexie queueing logic inside individual views.
- Block the student UI with modal error overlays on connection loss.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Reactive Status | Client connection state changes | `isOnline` ref updates immediately; `pendingCount` reflects Dexie pending count | Default to `navigator.onLine` or `true` if undefined |
| Queue Answer Offline | Client calls `queueAnswer(answerData)` while offline | Answer written to Dexie `pending_answers`, `pendingCount` increments | Catch Dexie errors gracefully and log warning |
| Manual / Auto Sync | Reconnection or explicit call to `syncNow()` | Flushes `pending_answers` and `pending_sessions` to backend, updates Dexie records, refreshes `pendingCount` | Retry failed items on next sync attempt |
| PWA Sync Integration | Browser supports Service Worker background sync (`SyncManager`) | Registers `'offline-sync'` tag on service worker registration | Fall back to window `online` listener if background sync unavailable |

</intent-contract>

## Code Map

- `frontend/src/composables/useOfflineSync.ts` -- Central Vue 3 composable encapsulating offline buffer, connectivity events, and sync flush logic.
- `frontend/src/stores/offlineModule.ts` -- Dexie IndexedDB store for cached questions, pending answers, and offline session states.
- `frontend/src/components/student/DiagnosticRunner.vue` -- Diagnostic test runner component refactored to use `useOfflineSync`.
- `frontend/src/views/student/RemediationSession.vue` -- Student remediation session view refactored to use `useOfflineSync`.
- `frontend/tests/composables/useOfflineSync.spec.ts` -- Unit tests for `useOfflineSync` composable.

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/composables/useOfflineSync.ts` -- Create composable exposing `isOnline`, `pendingCount`, `isSyncing`, `syncNow`, `queueAnswer`, `queueCompletion` -- Encapsulates offline connectivity and write-behind sync logic.
- [x] `frontend/src/components/student/DiagnosticRunner.vue` -- Refactor inline connectivity listeners and flush logic to use `useOfflineSync` -- Simplifies diagnostic view and uses composable.
- [x] `frontend/src/views/student/RemediationSession.vue` -- Integrate `useOfflineSync` for offline atom completion and answer queueing -- Enables offline sync for remediation sessions.
- [x] `frontend/tests/composables/useOfflineSync.spec.ts` -- Write unit tests for `useOfflineSync` covering online state, answer queueing, and syncNow execution -- Verifies composable behavior and reactivity.

**Acceptance Criteria:**
- Given `useOfflineSync.ts` exists, when imported in Vue components, then it exposes reactive `isOnline`, `pendingCount`, `isSyncing`, `syncNow()`, `queueAnswer()`, and `queueCompletion()`.
- Given the student is offline, when an answer or completion is submitted, then `queueAnswer()` / `queueCompletion()` queues it in Dexie and `pendingCount` updates.
- Given pending items in Dexie, when connection is restored or `syncNow()` is invoked, then all pending answers and sessions flush to the backend and `pendingCount` resets.
- Given `DiagnosticRunner.vue` and `RemediationSession.vue`, when student performs activities, then both views use `useOfflineSync` instead of direct manual store/event wiring.

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
- `cd frontend && npm run test` -- expected: All frontend unit tests pass including `useOfflineSync.spec.ts`

## Auto Run Result

Status: done
Final Revision: 4c8c4d72345b2a3350d938b2103697cfbe1e8c88

### Summary of Changes
Implemented `useOfflineSync` Vue 3 composable (`frontend/src/composables/useOfflineSync.ts`) to centralize network state monitoring (`isOnline`), pending queue tracking (`pendingCount`), write-behind buffer queueing (`queueAnswer`, `queueCompletion`), and automatic/manual sync flushing (`syncNow`). Refactored `DiagnosticRunner.vue` and `RemediationSession.vue` to utilize this composable, and added unit tests in `frontend/tests/composables/useOfflineSync.spec.ts`.

### Files Changed
- `frontend/src/composables/useOfflineSync.ts` — Composable encapsulating connectivity listeners, pending item queueing, and Dexie write-behind flush logic.
- `frontend/src/components/student/DiagnosticRunner.vue` — Refactored to replace inline connectivity event listeners and sync methods with `useOfflineSync`.
- `frontend/src/views/student/RemediationSession.vue` — Refactored to call `queueCompletion` on atom completion and render the offline status banner.
- `frontend/tests/composables/useOfflineSync.spec.ts` — Unit test suite verifying reactive states, queueing, and syncNow execution.
- `frontend/tests/views/DiagnosticSession.spec.ts` — Updated mock for `offlineStore`.
- `_bmad-output/implementation-artifacts/spec-5-4-useofflinesync-composable.md` — Specification and execution log.

### Verification Performed
- Executed `npx vitest run tests/composables/useOfflineSync.spec.ts tests/stores/offlineModule.spec.ts tests/views/DiagnosticSession.spec.ts` in `frontend` — All 13 tests passed.
- Pre-commit Husky hooks (`eslint --fix`, `stylelint --fix`) passed cleanly upon git commit.
