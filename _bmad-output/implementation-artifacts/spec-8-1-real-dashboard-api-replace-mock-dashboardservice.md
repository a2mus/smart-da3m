---
title: 'Story 8.1: Real Dashboard API & Replace Mock dashboardService'
type: 'feature'
created: '2026-08-02'
status: 'in-review'
baseline_revision: 'f14393a4ff615a30268b339f8faac6d1263a2d8f'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-8-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** `dashboardService.ts` on the frontend returns hardcoded mock objects via `Promise.resolve()`, and the backend `/api/v1/dashboard/overview` endpoint uses a direct aggregator without a dedicated `DashboardRepo` repository layer for tenant isolation. Furthermore, no reactive Pinia `dashboardStore.ts` exists to manage parent dashboard state.

**Approach:** Implement `DashboardRepo` in `backend/app/repositories/dashboard_repo.py` to enforce tenant isolation and encapsulate dashboard queries. Update `DashboardService` / `DashboardAggregator` and endpoint `/api/v1/dashboard/overview`. Refactor frontend `dashboardService.ts` to fetch real data via HTTP, create Pinia `src/stores/dashboardStore.ts`, and update `src/views/parent/Dashboard.vue` to reactively consume the store.

## Boundaries & Constraints

**Always:** Enforce tenant isolation (`organization_id`) and parent scoping (`parent_id`) on all backend dashboard queries. Use Pinia in `dashboardStore.ts` for frontend reactive state.

**Block If:** Backend schemas or models require incompatible breaking changes.

**Never:** Use mock data in `dashboardService.ts` or hardcode student data in responses. Do not bypass tenant filtering.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| GET Overview Happy Path | Authenticated parent with 2 children | Returns `ParentDashboardResponse` with real child mastery, subjects, activities, recommendations | HTTP 200 OK |
| Parent with No Children | Authenticated parent with 0 children | Returns `ParentDashboardResponse` with `children_count: 0`, empty `children` array | HTTP 200 OK |
| Unauthorized Child Access | Parent requests child_id belonging to another parent/tenant | HTTP 403 Forbidden error response | Returns 403 Forbidden with clear error detail |
| Frontend Store API Failure | Network error when calling `/api/v1/dashboard/overview` | `dashboardStore.error` set to localized error string, `loading` reset to false | Displays error alert in Dashboard.vue |

</intent-contract>

## Code Map

- `backend/app/repositories/dashboard_repo.py` -- New repository encapsulating tenant-isolated database queries for parent dashboard data.
- `backend/app/services/dashboard_service.py` -- Dashboard aggregation service using `DashboardRepo` for data retrieval and summary generation.
- `backend/app/api/endpoints/dashboard.py` -- FastAPI endpoint handling `/overview`, `/children`, and `/children/{child_id}`.
- `frontend/src/services/dashboardService.ts` -- API client service calling real backend endpoints via axios (`api.get`).
- `frontend/src/stores/dashboardStore.ts` -- New Pinia store managing parent dashboard state, selected child, loading, and error states.
- `frontend/src/views/parent/Dashboard.vue` -- Parent dashboard Vue component updated to consume `dashboardStore`.

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/repositories/dashboard_repo.py` -- Create `DashboardRepo` extending `BaseRepository` to handle tenant-filtered and parent-scoped queries for children, mastery profiles, and activities.
- [x] `backend/app/services/dashboard_service.py` -- Update `DashboardService` / `DashboardAggregator` to use `DashboardRepo` for database operations.
- [x] `backend/app/api/endpoints/dashboard.py` -- Ensure `/api/v1/dashboard/overview` and `/children` endpoints properly leverage `DashboardService` with tenant and parent scoping.
- [x] `frontend/src/services/dashboardService.ts` -- Replace mock data with real API calls using the project HTTP client (`@/services/api`).
- [x] `frontend/src/stores/dashboardStore.ts` -- Create Pinia store to manage children list, selected child, detailed dashboard data, loading, and errors.
- [x] `frontend/src/views/parent/Dashboard.vue` -- Refactor component to use `useDashboardStore()` reactively instead of direct service invocation.
- [x] `backend/tests/api/test_dashboard.py` -- Add/update integration tests verifying tenant isolation, parent scoping, and overview API payload structure.

**Acceptance Criteria:**
- Given `dashboardService.ts` returns hardcoded mock objects and `DashboardAggregator` exists but lacks a repository layer
- When `GET /api/v1/dashboard/overview` is called by an authenticated parent
- Then it returns real data from `DashboardService` (calling tenant-filtered `DashboardRepo`)
- And response includes: per-subject average mastery, competency breakdown, recent sessions, active alerts
- And `dashboardService.ts` calls real API endpoints without mock fallbacks
- And parent sees only their own children's data (enforced by tenant + parent_id)
- And `src/stores/dashboardStore.ts` manages dashboard state reactively

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

## Design Notes

Backend repository pattern: `DashboardRepo` receives `AsyncSession` and optional `tenant_id`. Extends or follows `BaseRepository` patterns found in `user_repo.py` and `diagnostic_repo.py`.

Frontend Pinia store: `useDashboardStore` defines actions `fetchOverview()`, `fetchChildDetails(childId)`, and getters `selectedChildData`.

## Verification

**Commands:**
- `pytest backend/tests/api/test_dashboard.py` -- expected: All dashboard tests pass successfully.
- `pnpm --prefix frontend test` -- expected: Frontend unit tests and build checks pass without errors.
