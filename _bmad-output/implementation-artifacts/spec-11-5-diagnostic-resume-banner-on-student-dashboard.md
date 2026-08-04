---
title: 'Story 11.5: Diagnostic Resume Banner on Student Dashboard'
type: 'feature'
created: '2026-08-04'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: false
final_revision: '07ae4e3f3d35fc6285a7e5f2d56859015cce5c34'
context: ['_bmad-output/project-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** When a student has an active diagnostic session in `IN_PROGRESS` state and lands on `student/Dashboard.vue`, there is no banner prompting them to resume their test, causing friction and risk of abandoned progress.

**Approach:** Implement a diagnostic session check in `student/Dashboard.vue` (and a dedicated banner component) that checks for `IN_PROGRESS` sessions via Dexie offline DB and backend API, displays a prominent banner with current question progress "Resume Diagnostic (Question N/M)", navigates directly back to `DiagnosticRunner.vue` upon tapping, and allows explicit session abandonment.

## Boundaries & Constraints

**Always:** Follow semantic color scale, logical CSS properties (`ps-*`, `pe-*`, `start-*`, `end-*`), WCAG 2.1 AA accessibility guidelines, and i18n translation keys.

**Block If:** Backend or database changes require external human configuration.

**Never:** Use hardcoded hex colors or non-logical physical CSS properties (`ml-*`, `pl-*`).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Active Session Exists | Student has `IN_PROGRESS` diagnostic session | Prominent banner renders with "Resume Diagnostic (Question N/M)" and action buttons | Hide banner if session check fails |
| Banner Tap | Student clicks banner "Resume Diagnostic" | Navigates to `/student/diagnostic/:moduleId` | Handle missing module ID gracefully |
| Banner Dismiss | Student clicks "Abandon" button on banner | Confirms abandonment, updates session status to `ABANDONED`, removes banner | Show toast/error if abandon API fails |
| No Active Session | No `IN_PROGRESS` session found | Banner is not rendered | Silent no-op |

</intent-contract>

## Code Map

- `frontend/src/views/student/Dashboard.vue` -- Renders student dashboard and embeds DiagnosticResumeBanner component.
- `frontend/src/components/student/DiagnosticResumeBanner.vue` -- Displays banner for active diagnostic sessions with resume and abandon actions.
- `frontend/src/services/diagnosticService.ts` -- Provides `getActiveSession` and `abandonSession` API calls.
- `frontend/src/stores/offlineModule.ts` -- Helper to query Dexie `IN_PROGRESS` sessions.
- `backend/app/api/endpoints/diagnostic.py` -- Adds `/active-session` and `/session/{id}/abandon` endpoints.
- `backend/app/repositories/diagnostic_repo.py` -- Adds repository methods `get_active_student_session` and `abandon_session`.

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/repositories/diagnostic_repo.py` -- Add `get_active_student_session` and update status method for `ABANDONED` status -- Enables querying active in-progress sessions.
- [x] `backend/app/api/endpoints/diagnostic.py` -- Expose `GET /diagnostic/active-session` and `POST /diagnostic/session/{id}/abandon` endpoints -- Allows frontend to fetch active session and abandon when requested.
- [x] `frontend/src/services/diagnosticService.ts` -- Add `getActiveSession` and `abandonSession` methods -- Bridges frontend components to backend API.
- [x] `frontend/src/locales/ar.json` & `fr.json` -- Add i18n strings for diagnostic resume banner -- Ensures bilingual RTL/LTR support.
- [x] `frontend/src/components/student/DiagnosticResumeBanner.vue` -- Create banner component with resume and abandon actions -- Implements banner UI adhering to semantic tokens and logical CSS.
- [x] `frontend/src/views/student/Dashboard.vue` -- Integrate `DiagnosticResumeBanner` at the top of the main area -- Shows banner when active session exists.

**Acceptance Criteria:**
- Given a student has a diagnostic session in `IN_PROGRESS` state, when they land on `student/Dashboard.vue`, then a prominent banner reads: "Resume Diagnostic (Question N/M)".
- And tapping the banner returns directly to `DiagnosticRunner.vue` at the current question.
- And the banner is dismissible if the student explicitly chooses to abandon.

## Spec Change Log

## Review Triage Log

### 2026-08-04 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 5 (0 high, 2 medium, 3 low)
- defer: 2 (0 high, 0 medium, 2 low)
- reject: 1
- addressed_findings:
  - `[low]` `[patch]` Capped `question_number` calculation to maximum 10 in `get_active_session` endpoint and `DiagnosticResumeBanner.vue`.
  - `[medium]` `[patch]` Added session status validation `session.status == IN_PROGRESS` in `abandon_session` endpoint to prevent abandoning already completed/abandoned sessions.
  - `[medium]` `[patch]` Wrapped `abandonDiagnostic` local cleanup in `finally` block in `DiagnosticResumeBanner.vue` to guarantee Dexie offline store cleanup even if API call fails.
  - `[low]` `[patch]` Added fallback date validation in `checkActiveSession` for `started_at` timestamp parsing in `DiagnosticResumeBanner.vue`.
  - `[low]` `[patch]` Corrected spelling in Arabic locale (`"متأكد"`).

## Verification

**Commands:**
- `pnpm --prefix frontend test` -- expected: All frontend unit tests pass.
- `pytest backend/tests` -- expected: Backend API tests pass.

## Auto Run Result

### Summary of Implemented Change
- Implemented diagnostic session tracking and resume banner for the student dashboard.
- Frontend checks active `IN_PROGRESS` diagnostic session via backend API and Dexie offline DB fallback, displaying question progress (`Question N/M`), direct navigation resume, and explicit session abandonment.
- Backend added `GET /diagnostic/active-session` and `POST /diagnostic/session/{session_id}/abandon` endpoints with `IN_PROGRESS` status validation.

### Files Changed
- `backend/app/api/endpoints/diagnostic.py` — Exposed active session query and abandon endpoint with status validation.
- `backend/app/repositories/diagnostic_repo.py` — Added active session lookup query.
- `backend/app/schemas/diagnostic.py` — Added `ActiveDiagnosticSessionResponse` schema.
- `frontend/src/components/student/DiagnosticResumeBanner.vue` — Created responsive, accessible resume banner component.
- `frontend/src/services/diagnosticService.ts` — Added `getActiveSession` and `abandonSession` API integration.
- `frontend/src/views/student/Dashboard.vue` — Integrated `DiagnosticResumeBanner` at top of student dashboard.
- `frontend/src/locales/ar.json` & `fr.json` — Added i18n translation keys with RTL/LTR support.

### Review Findings Breakdown
- **Patches Applied (5):** Capped `question_number` at 10 max; added `IN_PROGRESS` status validation to abandon endpoint; guaranteed local Dexie store session cleanup in `finally` block; added date parsing fallback validation; corrected Arabic spelling (`متأكد`).
- **Deferred Findings (2):** `DiagnosticRepository.get_active_student_session` `.first()` multi-session handling; endpoint return schema Pydantic model refactor (appended as NEW entries to `deferred-work.md`).
- **Rejected (1):** Material icon directional note.

### Follow-up Review Recommendation
- `followup_review_recommended: false` — All findings were localized edge-case patches resolved cleanly.

### Residual Risks
- None. All status checks and fallback paths are verified.


