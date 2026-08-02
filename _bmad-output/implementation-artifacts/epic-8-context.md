# Epic 8 Context: Parent Dashboard & Insights

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Parents view their child's evolution through a real radar chart, plain-language insights, and daily reinforcement recommendations — all powered by real API data.

## Stories

- Story 8.1: Real Dashboard API & Replace Mock dashboardService
- Story 8.2: Subject-Strength Radar Chart with vue-chartjs
- Story 8.3: Smart Insight Messages (Zero Raw Scores)
- Story 8.4: Daily Reinforcement Recommendation

## Requirements & Constraints

- Parents access child progress data via `/api/v1/dashboard/overview`.
- Data must be tenant-filtered and parent-scoped (parents see only their own children's data).
- Dashboard responses include per-subject average mastery, competency breakdown, recent sessions, and active alerts.
- Primary indicators must use plain-language insight messages rather than raw numeric scores (FR-21).
- Daily reinforcement recommendations suggest off-platform activities based on recent competency gaps (FR-22).

## Technical Decisions

- Backend: FastAPI route `/api/v1/dashboard/overview` supported by `DashboardService` and `DashboardRepo`.
- Frontend: Vue 3 with Pinia (`src/stores/dashboardStore.ts`) and API service (`src/services/dashboardService.ts`).
- Multi-tenancy: Tenant isolation enforced via DB filters and parent-child ownership queries.

## Cross-Story Dependencies

- Story 8.1 establishes the real API endpoint and frontend store required by Stories 8.2, 8.3, and 8.4.
