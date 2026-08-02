---
title: 'Story 5.3: Pre-Fetch Questions into Dexie & Connectivity Detection'
type: 'feature'
created: '2026-08-02'
status: 'in-progress'
baseline_revision: 'f5b3e85c471fec104552d90fe43a16b4b8857611'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-5-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** Diagnostic runner currently attempts live HTTP calls for every question without pre-caching questions into Dexie, causing sessions to fail if connectivity drops. Additionally, `getPendingSyncSessions()` and `markSessionSynced()` in `offlineModule.ts` are unused dead code.

**Approach:** Pre-fetch questions into Dexie IndexedDB when starting a diagnostic session, fallback to Dexie cached questions when network requests fail or client is offline (`navigator.onLine`), add a reactive `NetworkStatusIndicator.vue` for visual online/offline status, and wire session sync methods into offline sync processing.

## Boundaries & Constraints

**Always:**
- Use semantic Tailwind tokens (`bg-primary`, `bg-error`, `text-on-surface`, etc.) and logical CSS properties (`ps-`, `pe-`, etc.) for any UI components.
- Check `navigator.onLine` or handle fetch errors gracefully by serving cached questions from Dexie.
- Ensure `getPendingSyncSessions()` and `markSessionSynced()` are invoked during offline session sync flush.
- Transform HTTP responses via camelCase boundary transform as established in codebase conventions.

**Block If:**
- Implementing offline features requires altering backend database schemas or non-student user roles.

**Never:**
- Block the student UI with modal error dialogs on connection loss.
- Use raw hex colors or physical CSS direction properties (`pl-`, `pr-`) in Vue components.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Session Start Pre-Fetch | Online diagnostic session start | API returns upcoming module questions; questions bulk-inserted into Dexie `questions` table | If API fails, attempt to read existing cached questions from Dexie |
| Disconnected Mid-Test | Client loses connection during test (`navigator.onLine == false`) | Diagnostic runner serves next question from Dexie `getCachedQuestions()` | If no cached questions available, show graceful offline notice |
| Session Sync Flush | Reconnection with pending offline session | `getPendingSyncSessions()` returns sessions, synced to backend, `markSessionSynced()` marks them `COMPLETED` | Retry on next reconnection if sync fails |

</intent-contract>

## Code Map

- `frontend/src/stores/offlineModule.ts` -- Offline Dexie database store for question caching and offline session status management.
- `frontend/src/services/diagnosticService.ts` -- Service layer integrating question pre-fetching and Dexie fallback.
- `frontend/src/components/NetworkStatusIndicator.vue` -- Reactive online/offline visual status indicator component.
- `frontend/src/views/student/DiagnosticRunner.vue` -- Diagnostic session runner UI rendering network status and pre-fetched questions.
- `frontend/src/tests/offlineSync.test.ts` -- Unit tests for question pre-fetching into Dexie, connectivity fallback, and sync session state updates.

## Tasks & Acceptance

**Execution:**
- [ ] `frontend/src/stores/offlineModule.ts` -- Export and wire `cacheQuestions`, `getCachedQuestions`, `getPendingSyncSessions`, `markSessionSynced`, and session status updates -- Enables offline question caching and session lifecycle management.
- [ ] `frontend/src/services/diagnosticService.ts` -- Implement `preFetchModuleQuestions()` and update `getNextQuestion()` to fallback to Dexie when offline -- Enables offline question retrieval for students.
- [ ] `frontend/src/components/NetworkStatusIndicator.vue` -- Create visual status indicator component for online/offline state using semantic design tokens and logical CSS -- Informs student of connectivity state cleanly.
- [ ] `frontend/src/views/student/DiagnosticRunner.vue` -- Wire `NetworkStatusIndicator.vue` and question pre-fetching into the diagnostic execution loop -- Provides uninterrupted student experience during network drops.
- [ ] `frontend/src/tests/offlineSync.test.ts` -- Add unit tests for `cacheQuestions`, `getPendingSyncSessions`, `markSessionSynced`, and offline question resolution -- Verifies offline store and service integration.

**Acceptance Criteria:**
- Given `cacheQuestions()` exists in `offlineModule.ts`, when a diagnostic session starts, then the next N questions are pre-fetched and cached in Dexie.
- Given the student is offline or network fails, when requesting the next question, then questions are served from Dexie cache.
- Given `navigator.onLine` state changes, when online/offline events trigger, then `NetworkStatusIndicator.vue` displays current connection state.
- Given `getPendingSyncSessions()` and `markSessionSynced()` exist in `offlineModule.ts`, when offline sessions are synced, then they are retrieved and updated to `COMPLETED`.

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `cd frontend && npm run test` -- expected: All frontend unit tests pass including offlineSync.test.ts
