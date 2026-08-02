---
title: 'Story 8.4: Daily Reinforcement Recommendation'
type: 'feature'
created: '2026-08-02'
status: 'done'
baseline_revision: '48196c73e6628139a9546029f90ec266b0ce7644'
final_revision: 'dc4f4bc0403c21cc96a5e6595a2452ad76c71fa4'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-8-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** Parent dashboard recommendations currently return generic multi-item score-based recommendations without linking to the child's actual most recent failed competency, error type, or off-platform non-screen activity template library.

**Approach:** Implement a deterministic daily reinforcement recommendation engine in `backend/app/services/dashboard_service.py` that queries the child's latest failed competency/error type via `DashboardRepo`, selects an off-platform activity from a template library keyed by competency + error type, caches the single recommendation per child per day, and exposes it via `/api/v1/dashboard/overview`. Update frontend `dashboardService.ts`, `dashboardStore.ts`, and `Dashboard.vue` to display this single daily off-platform activity card per child.

## Boundaries & Constraints

**Always:** Enforce exactly one recommendation card per child per day (FR-22). Key recommendation to child's most recent failed competency and error type. Ensure activity is off-platform (non-screen). Cache recommendation per child and date. Enforce tenant isolation.

**Block If:** Backend schemas or database models require incompatible breaking changes.

**Never:** Return multiple daily reinforcement cards when exactly one is required. Hardcode screen-based activities as off-platform recommendations. Bypass tenant or parent ownership filters.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Single Daily Card | Parent opens dashboard for child with recent failed competency (e.g., Arabic Taa Marbuta) | Dashboard returns exactly 1 off-platform activity card (e.g. "Practice writing تاء مربوطة with your child for 10 minutes using sand tray") | Fallback to general off-platform practice template if no failed competency found |
| Daily Caching | Multiple requests on same date for same child | Same cached recommendation returned until date boundary changes | Generate fresh recommendation on first request of new day |
| No Failed Competencies | Student has 100% mastery or no assessments | Return default positive off-platform bonding activity (e.g., "Read a story together for 10 minutes") | Handle gracefully without 500 errors |

</intent-contract>

## Code Map

- `backend/app/schemas/dashboard.py` -- Recommendation and ChildDashboardData schemas updated with daily reinforcement fields
- `backend/app/repositories/dashboard_repo.py` -- Query child's most recent failed competency and error type
- `backend/app/services/dashboard_service.py` -- Template library, daily recommendation generation, and date-based caching logic
- `backend/app/api/endpoints/dashboard.py` -- Endpoints returning child dashboard data with daily reinforcement recommendation
- `frontend/src/services/dashboardService.ts` -- TypeScript types for daily reinforcement recommendation card
- `frontend/src/views/parent/Dashboard.vue` -- UI component rendering the single daily reinforcement card per child

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/schemas/dashboard.py` -- Update Recommendation schema to support off-platform daily recommendation fields -- Ensure API schema compliance
- [x] `backend/app/repositories/dashboard_repo.py` -- Implement `get_latest_failed_competency(student_id)` -- Fetch child's most recent failed competency and error type from diagnostic sessions
- [x] `backend/app/services/dashboard_service.py` -- Add template library and daily caching for `generate_daily_recommendation` -- Ensure exactly 1 off-platform recommendation per day per child
- [x] `backend/app/api/endpoints/dashboard.py` -- Pass daily recommendation through dashboard overview endpoint -- Expose endpoint for frontend consumption
- [x] `frontend/src/services/dashboardService.ts` -- Update `ChildDashboardData` interface with `daily_recommendation` -- Ensure TypeScript type safety
- [x] `frontend/src/views/parent/Dashboard.vue` -- Display single daily reinforcement activity card prominently -- Provide parents with clear daily action

**Acceptance Criteria:**
- Given FR-22 requires exactly one recommendation per day, when dashboard is requested, then exactly one recommendation card is returned per child per day
- Given a child has a recorded failed competency, when daily recommendation is generated, then the activity is selected from a template library matching competency and error type
- Given the recommendation is an off-platform activity, when displayed to the parent, then it explicitly describes a non-screen real-world exercise
- Given multiple requests occur on the same day for a child, when fetched, then the exact same recommendation is returned from cache until the next day

## Spec Change Log

## Review Triage Log

### 2026-08-02 — Review pass 2
- intent_gap: 0
- bad_spec: 0
- patch: 3: (high 0, medium 1, low 2)
- defer: 2: (high 0, medium 0, low 2)
- reject: 2: (high 0, medium 0, low 2)
- addressed_findings:
  - `[medium]` `[patch]` Added try/except error guard around `generate_daily_recommendation` in `get_child_dashboard_data` to prevent 500 error on dashboard endpoint.
  - `[low]` `[patch]` Added type-safe filtering for `subjects` list items (`isinstance` and key existence check) in `generate_daily_recommendation` fallback logic.
  - `[low]` `[patch]` Added optional chaining check for `daily_recommendation.title` in frontend `Dashboard.vue`.

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
- `pytest backend/tests/api/test_dashboard.py` -- expected: PASS (5/5 passed)

## Auto Run Result

Status: done

_Appended by the bmad-loop orchestrator (missing-marker repair, #224): the session finalized this spec's frontmatter without its `## Auto Run Result` marker, so the orchestrator synthesized the result from the frontmatter and appended this section._

Synthesized by the bmad-loop orchestrator from frontmatter status `done` for story `8-4-daily-reinforcement-recommendation` (session finalized the spec without appending its marker).
