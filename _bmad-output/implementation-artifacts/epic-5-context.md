# Epic 5 Context: Offline-Resilient Student Experience

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

The goal of this epic is to ensure that students can continue their diagnostic and remediation activities seamlessly when their network connection drops. This offline capability prevents work loss by buffering answers and atom completions locally on the client using a write-behind pattern. By caching questions ahead of time, the platform shields young learners from technical interruptions, maintaining focus on their pedagogical progress.

## Stories

- Story 5.1: Dexie Write-Behind Buffer for Student Answers
- Story 5.2: Backend Sync Endpoint for Offline Sessions
- Story 5.3: Pre-Fetch Questions into Dexie & Connectivity Detection
- Story 5.4: useOfflineSync Composable

## Requirements & Constraints

- Local Content Cache (FR-29): The system must cache consumed modules and questions locally in IndexedDB using Dexie. This allows students to continue their sessions during connectivity drops. Republishing a module automatically invalidates the cached version.
- Background Sync of Analytics (FR-30): The system must queue answers and learning completions offline. These events must sync to the backend when connectivity is restored, ensuring no data is dropped.
- Student progress, answers, and pathway completions are preserved during disconnection.
- Syncing must be automatic, requiring no manual triggers from the student.
- The backend sync endpoint must be rate-limited and handle batch submissions.
- Student role offline-first: Only the student interface supports offline-first operations. Experts and parents require active network connectivity for content authoring, proposal validation, dashboard view updates, and other mutations.
- PWA architecture: The implementation relies on standard service workers (via `vite-plugin-pwa`) and Dexie (IndexedDB). It doesn't support native mobile wrappers in this release.
- Wire format transform: Request and response structures must undergo camelCase to snake_case translation at the Axios boundary. They must never leak snake_case keys into Pinia stores or Vue components.

## Technical Decisions

- Client-Side Datastore: Dexie is used to manage IndexedDB tables. The schema must include `pending_answers` (for write-behind buffering) and `cached_questions` (for pre-fetching).
- Write-Behind Pattern: The frontend writes student responses directly to Dexie. When online, these writes execute as write-through requests to the API. Offline status causes answers to queue in IndexedDB with a pending status.
- Connectivity Listener: A listener watches connectivity state via `navigator.onLine` and window events. Reconnection triggers a background flush of all pending items in chronological order.
- Backend Batch Sync API: A new endpoint `POST /api/v1/sync/batch` accepts batched answers and completions. The backend processes entries idempotently.
- Conflict Resolution:
  - For atom completions, the system uses last-write-wins.
  - Pathway state transitions treat the server as the authoritative source of truth.
- Idempotency: The endpoint `/api/v1/diagnostic/answer` must reject duplicate client-generated answer IDs to prevent double scoring or BKT mastery updates.

## UX & Interaction Patterns

- Student Status Visibility: A simple, non-intrusive status indicator must show whether the student is online or offline.
- Uninterrupted Session Flow: On connection loss, the UI must not block the student with modal error overlays. It should display a subtle toast or banner, queue the responses, and let the child proceed through pre-fetched questions.
- Reconnection Recovery: Once the network is restored, a quiet notification should show that local work has successfully synced.

## Cross-Story Dependencies

Story 5.1 (Dexie Write-Behind Buffer) needs the backend endpoint from Story 5.2 (Backend Sync Endpoint) to flush queued answers.

Wrapping the connectivity listeners and Dexie queue operations is the job of the Story 5.4 (useOfflineSync Composable) helper. It acts as the interface for both Story 5.1 and Story 5.3 (Pre-Fetch Questions & Connectivity Detection).

This Epic depends on Epic 1 (Multi-Tenant Platform Foundation) for organization context, as all cached items and sync requests must carry the active tenant ID.