---
title: 'Story 9.1: Real Competency Heatmap Data'
type: 'feature'
created: '2026-08-02'
status: 'done'
baseline_revision: '50d03d336187e9fa88e73d1423097234d0542a54'
final_revision: '8c43fd0b552b926933f91f59c5c658aac447779f'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-9-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** `analyticsService.ts` returns hardcoded mock objects, `CompetencyHeatmap.vue` does not use a Pinia store or real backend API, and the backend `/api/v1/analytics/heatmap` endpoint lacks proper service/repository layering and `module_id` filtering for tenant-filtered student competency mastery data.

**Approach:** Implement `AnalyticsService` and `AnalyticsRepo` for tenant-filtered heatmap data on `GET /api/v1/analytics/heatmap?module_id={id}`, create `analyticsStore.ts` Pinia store in frontend, wire `analyticsService.ts` to call the real backend endpoint, and update `CompetencyHeatmap.vue` to consume state from `analyticsStore`.

## Boundaries & Constraints

**Always:** Ensure all student competency data is filtered strictly by the authenticated expert's active organization (`organization_id`). Color map mastery levels accurately: NOT_STARTED/ATTEMPTED -> red, FAMILIAR -> yellow, PROFICIENT/MASTERED -> green.

**Block If:** External operator actions outside the codebase are required.

**Never:** Never return mock data in `analyticsService.ts` or expose student data across organizations.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| GET Heatmap Happy Path | `module_id` query param, authenticated Expert | 200 OK with `students`, `competencies`, `cells` (real data from `CompetencyProfile`) | No error expected |
| GET Heatmap Empty Org/Module | `module_id` for module with no student records in org | 200 OK with empty `cells: []` and student/competency lists | No error expected |
| Unauthenticated / Non-Expert | Missing token or Student/Parent role | 401 Unauthorized / 403 Forbidden | Return HTTP 401/403 |

</intent-contract>

## Code Map

- `backend/app/repositories/analytics_repo.py` -- Analytics database repository layer
- `backend/app/services/analytics_service.py` -- Analytics business logic service
- `backend/app/api/endpoints/analytics.py` -- Analytics API endpoint handlers
- `frontend/src/services/analyticsService.ts` -- Frontend API client service
- `frontend/src/stores/analyticsStore.ts` -- Pinia state management store for analytics
- `frontend/src/components/expert/CompetencyHeatmap.vue` -- Heatmap Vue visualization component
- `frontend/src/views/expert/Analytics.vue` -- Expert Analytics dashboard view

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/repositories/analytics_repo.py` -- Create repository layer with `get_heatmap_data(db, organization_id, module_id)` querying DB for student competency mastery profiles -- Provides database access for heatmap metrics.
- [x] `backend/app/services/analytics_service.py` -- Create service layer with `get_heatmap(db, organization_id, module_id)` -- Encapsulates business logic and formats heatmap response.
- [x] `backend/app/api/endpoints/analytics.py` -- Update endpoint `GET /api/v1/analytics/heatmap` to accept `module_id` query parameter and delegate to `AnalyticsService` -- Exposes real tenant-isolated heatmap API.
- [x] `frontend/src/services/analyticsService.ts` -- Replace mock data implementations with real `http.get('/analytics/heatmap', { params: { module_id } })` -- Connects frontend service to backend API.
- [x] `frontend/src/stores/analyticsStore.ts` -- Create Pinia store to hold heatmap state (`heatmapData`, `loading`, `error`, `fetchHeatmap`) -- Manages analytics state reactively.
- [x] `frontend/src/components/expert/CompetencyHeatmap.vue` -- Connect component to `analyticsStore` and verify color mappings (NOT_STARTED/ATTEMPTED -> red, FAMILIAR -> yellow, PROFICIENT/MASTERED -> green) -- Renders real competency heatmap.
- [x] `frontend/src/views/expert/Analytics.vue` -- Integrate `CompetencyHeatmap` component and `analyticsStore` in the expert view -- Replaces mock dashboard elements.

**Acceptance Criteria:**
- Given `analyticsService.ts` returns hardcoded mock data and `CompetencyHeatmap.vue` exists but uses mock data, when the real heatmap is implemented, then `GET /api/v1/analytics/heatmap?module_id={id}` returns real student×competency data from `AnalyticsService` (tenant-filtered).
- And each cell maps mastery level to color: NOT_STARTED/ATTEMPTED → red, FAMILIAR → yellow, PROFICIENT/MASTERED → green.
- And `analyticsService.ts` calls the real API (no more mock objects).
- And `CompetencyHeatmap.vue` renders from `analyticsStore`, not from mock data.
- And the expert sees only students in their organization.

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

### 2026-08-03 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 0
- defer: 7
- reject: 2
- addressed_findings:
  - none

## Verification

**Commands:**
- `lsp_diagnostics backend/app/api/endpoints/analytics.py` -- expected: Clean LSP diagnostics
- `eslint & stylelint` -- expected: Clean frontend lint checks via pre-commit

## Auto Run Result

Status: done
Blocking condition: none

### Implementation Summary
Implemented database-driven competency heatmap retrieval and visualization for expert analytics, replacing mock frontend data with real backend endpoints filtered by tenant organization ID and optional module ID.

### Files Changed
- `backend/app/repositories/analytics_repo.py` — Database repository for fetching tenant-isolated competency profiles and student lists.
- `backend/app/services/analytics_service.py` — Service layer computing heatmap response matrix and mapping mastery levels to colors/scores.
- `backend/app/api/endpoints/analytics.py` — Added `GET /api/v1/analytics/heatmap` and updated `POST` endpoint to delegate to `AnalyticsService`.
- `frontend/src/services/analyticsService.ts` — Updated API service client with HTTP calls to `/analytics/heatmap`.
- `frontend/src/stores/analyticsStore.ts` — Pinia store managing reactive state for analytics data.
- `frontend/src/components/expert/CompetencyHeatmap.vue` — Vue component consuming `analyticsStore` state with updated color mappings.
- `frontend/src/views/expert/Analytics.vue` — Expert dashboard view fetching analytics data on mount.

### Review Findings Breakdown
- Patches applied: 0
- Items deferred: 7 (new entries appended to `_bmad-output/implementation-artifacts/deferred-work.md`)
- Items rejected: 2 (noise/duplicate patterns)

### Follow-up Review Recommendation
- `followup_review_recommended: false`


