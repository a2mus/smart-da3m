---
title: 'Story 9.2: Auto-Grouping into Remediation Groups'
type: 'feature'
created: '2026-08-03'
status: 'done'
baseline_revision: '64a50ac95d2bd0b8956a0f315f2150fd832796bf'
final_revision: '68b57c08edd7aa9f1c9859f3b586e4e36b9e5764'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-9-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** `POST /api/v1/analytics/auto-group` currently implements raw inline DB query grouping logic in `backend/app/api/endpoints/analytics.py` instead of delegating data fetching to `AnalyticsService`/`AnalyticsRepo` and clustering calculations to stateless domain engine logic. Additionally, student grouping does not combine competency gaps with error types per tenant, and frontend heatmap lacks an overlay control to render suggested remediation groups.

**Approach:** Extract stateless auto-grouping algorithm into `RemediationEngine` (or `AutoGroupingEngine` in `app.engines`), wire `AnalyticsService` and `AnalyticsRepo` to fetch tenant-scoped student competency and error diagnostic data, update `POST /api/v1/analytics/auto-group` to delegate to `AnalyticsService`, add `autoGroup` API call in `analyticsService.ts` & action in `analyticsStore.ts`, and overlay suggested remediation groups directly on `CompetencyHeatmap.vue`.

## Boundaries & Constraints

**Always:** Ensure all student data used for auto-grouping is strictly filtered by the authenticated expert's `organization_id`. Delegate clustering logic to the engine layer (stateless). Return groups formatted as `[{competency, error_type, students: [...]}]`.

**Block If:** Any schema or API contract change requires unapproved breaking DB migrations.

**Never:** Reimplement inline SQL grouping logic inside API endpoint functions. Never bypass tenant isolation.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | `POST /api/v1/analytics/auto-group` with valid expert auth token & `group_by=competency` | `200 OK` with `AutoGroupResponse` containing clustered groups: `competency`, `error_type`, `students` list | Return empty groups array if no unmastered students exist |
| ERROR_TYPE_GROUPING | `POST /api/v1/analytics/auto-group` with `group_by=error_type` | `200 OK` with groups clustered by shared error classifications (RESOURCE, PROCESS, INCIDENTAL) | Empty list if no error diagnostic records match |
| INVALID_PARAM | Invalid `group_by` string parameter (e.g., `group_by=foo`) | `400 Bad Request` | Detail message indicating invalid `group_by` value |
| TENANT_ISOLATION | Expert from Org A calls `/api/v1/analytics/auto-group` | Only students in Org A are clustered; Org B students excluded | Isolated query filtering in `AnalyticsRepo` |

</intent-contract>

## Code Map

- `backend/app/engines/remediation_engine.py` -- Pure stateless auto-grouping clustering domain logic.
- `backend/app/repositories/analytics_repo.py` -- Data retrieval queries for tenant-scoped unmastered student competencies and error classifications.
- `backend/app/services/analytics_service.py` -- Business service delegating DB fetch to repo and clustering to engine.
- `backend/app/api/endpoints/analytics.py` -- API endpoint delegating `POST /api/v1/analytics/auto-group` to `AnalyticsService`.
- `backend/app/schemas/analytics.py` -- Request/Response schemas for auto-grouping (`AutoGroupResponse`, `RemediationGroupCluster`).
- `frontend/src/services/analyticsService.ts` -- Frontend HTTP client method for `autoGroup`.
- `frontend/src/stores/analyticsStore.ts` -- Pinia store managing state for `autoGroups` and `fetchAutoGroups`.
- `frontend/src/components/expert/CompetencyHeatmap.vue` -- Heatmap component rendering auto-group overlay.

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/engines/remediation_engine.py` -- Add `AutoGroupingEngine` / stateless grouping method -- Pure logic for clustering student data by competency and error type.
- [x] `backend/app/repositories/analytics_repo.py` -- Add `get_auto_group_data` method -- Retrieve tenant-filtered student competency profiles and diagnostic error classifications.
- [x] `backend/app/services/analytics_service.py` -- Add `auto_group_students` method -- Coordinate data retrieval and engine clustering.
- [x] `backend/app/schemas/analytics.py` -- Ensure response schema includes `competency`, `error_type`, and `students`.
- [x] `backend/app/api/endpoints/analytics.py` -- Update `auto_group_students` endpoint to call `AnalyticsService`.
- [x] `frontend/src/services/analyticsService.ts` -- Add `autoGroup` API integration.
- [x] `frontend/src/stores/analyticsStore.ts` -- Add `autoGroups` state and `fetchAutoGroups` action.
- [x] `frontend/src/components/expert/CompetencyHeatmap.vue` -- Implement remediation group overlay controls and UI visualization.
- [x] `backend/tests/api/test_analytics.py` -- Add unit & integration tests for auto-group endpoint.

**Acceptance Criteria:**
- Given student diagnostic and competency data in DB, when expert calls `POST /api/v1/analytics/auto-group`, then endpoint delegates to `AnalyticsService` & `RemediationEngine`.
- Given auto-grouping response, then returned list contains groups with `{competency, error_type, students: [...]}` fields.
- Given heatmap page in frontend, when expert toggles auto-group overlay, then suggested groups are highlighted on top of heatmap grid.

## Verification

**Commands:**
- `pytest backend/tests/api/test_analytics_auto_group.py backend/tests/test_engines.py` -- expected: 15 passed in 0.16s

## Spec Change Log

## Review Triage Log

### 2026-08-03 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 2: (high 1, low 1)
- defer: 1: (low 1)
- reject: 0
- addressed_findings:
  - `high` `patch` Restored `get_students_for_heatmap` method in `AnalyticsRepo` (`backend/app/repositories/analytics_repo.py`) to resolve runtime `AttributeError` in `AnalyticsService.get_heatmap()`.
  - `low` `patch` Updated `AnalyticsService.auto_group_students` (`backend/app/services/analytics_service.py`) to extract `getattr(p, "error_type", None) or "PROCESS"` dynamically.

## Design Notes

Stateless auto-grouping clustering logic is encapsulated in `RemediationEngine.auto_group_students` in the backend engine layer. Data access for unmastered competency profiles is handled by `AnalyticsRepo.get_auto_group_data`, and business coordination happens in `AnalyticsService.auto_group_students`. `POST /api/v1/analytics/auto-group` endpoint delegates directly to `AnalyticsService`. In the frontend, `analyticsStore.ts` manages state for suggested groups and overlay visibility, while `CompetencyHeatmap.vue` renders suggested remediation groups over the heatmap interface.

## Auto Run Result

### Implementation Summary
- Added `auto_group_students` method to `RemediationEngine` in `backend/app/engines/remediation_engine.py` to statelessly cluster students by shared competency gaps and error types.
- Added `get_auto_group_data` and restored `get_students_for_heatmap` in `backend/app/repositories/analytics_repo.py` for fetching tenant-filtered student profiles.
- Updated `AnalyticsService.auto_group_students` in `backend/app/services/analytics_service.py` to coordinate DB data retrieval and engine clustering.
- Updated `POST /api/v1/analytics/auto-group` in `backend/app/api/endpoints/analytics.py` to delegate to `AnalyticsService`.
- Added `autoGroup` method in `frontend/src/services/analyticsService.ts` and updated `StudentGroup` interface.
- Added `showAutoGroupsOverlay` state, `autoGroupBy` ref, `fetchStudentGroups`, and `toggleAutoGroupsOverlay` actions in `frontend/src/stores/analyticsStore.ts`.
- Added auto-group overlay control toolbar and suggested remediation groups banner in `frontend/src/components/expert/CompetencyHeatmap.vue`.
- Added automated unit and integration test suite in `backend/tests/api/test_analytics_auto_group.py` (all 15 backend tests passing).

### Changed Files
- `backend/app/engines/remediation_engine.py`: Implemented stateless `auto_group_students` method.
- `backend/app/repositories/analytics_repo.py`: Implemented tenant-filtered `get_auto_group_data` query and restored `get_students_for_heatmap`.
- `backend/app/services/analytics_service.py`: Added `auto_group_students` coordination service method with dynamic `error_type` fallback.
- `backend/app/api/endpoints/analytics.py`: Updated `/auto-group` endpoint to delegate to `AnalyticsService`.
- `frontend/src/services/analyticsService.ts`: Added `autoGroup` HTTP request method with `group_by` parameter.
- `frontend/src/stores/analyticsStore.ts`: Added state management for auto-group overlay and groupings.
- `frontend/src/components/expert/CompetencyHeatmap.vue`: Added auto-group overlay controls and group visualization banner.
- `backend/tests/api/test_analytics_auto_group.py`: Added unit and integration tests.

### Review Findings Breakdown
- Patches applied: 2 (Restored missing `get_students_for_heatmap` method in `AnalyticsRepo`; dynamic `error_type` extraction in `AnalyticsService`)
- Items deferred: 1 (Unreferenced legacy inline helper functions `_group_by_competency` and `_group_by_error_type` in `analytics.py`)
- Items rejected: 0

### Verification
- Ran `pytest backend/tests/api/test_analytics_auto_group.py backend/tests/test_engines.py` -> 15 passed in 0.14s.

