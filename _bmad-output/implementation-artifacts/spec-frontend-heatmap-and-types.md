---
title: 'frontend-heatmap-and-types'
type: 'bugfix'
created: '2026-08-03'
status: 'done'
baseline_revision: '0eb739e03e337b3e485a63790c9f53dfd113e47e'
final_revision: 'b6ca49ead6e30436b57e5adc1512916d604f6252'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
---

<intent-contract>

## Intent

**Problem:** CompetencyHeatmap component (`frontend/src/components/expert/CompetencyHeatmap.vue`) only fetches heatmap data on mount and does not watch `props.moduleId` when a parent component dynamically changes the module filter. Additionally, frontend `analyticsService.ts` type definitions (`HeatmapCell` and `MetricsResponse`) mark `p_learned` and `mastery_speed_days` as optional fields, mismatching the backend's required schema (`backend/app/schemas/analytics.py`).

**Approach:** Add a reactive Vue `watch` for `props.moduleId` in `CompetencyHeatmap.vue` to trigger `analyticsStore.fetchHeatmap(newModuleId)` whenever `moduleId` changes post-mount, and update `HeatmapCell` and `MetricsResponse` in `frontend/src/services/analyticsService.ts` to make `p_learned: number` and `mastery_speed_days: number` required fields.

## Boundaries & Constraints

**Always:** Maintain type safety across TypeScript interfaces and preserve existing reactive state logic in Vue components.

**Block If:** Any breaking changes to component prop interface or API contract are required beyond type alignment.

**Never:** Modify backend code or alter existing Pinia store behavior outside the required refetch and type updates.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Module prop update post-mount | `props.moduleId` changes from 'mod-1' to 'mod-2' | `watch` triggers `analyticsStore.fetchHeatmap('mod-2')` | Store handles API loading state and errors |
| Type check HeatmapCell | Object missing `p_learned` | TypeScript compilation fails | Compile-time validation |
| Type check MetricsResponse | Object missing `mastery_speed_days` | TypeScript compilation fails | Compile-time validation |

</intent-contract>

## Code Map

- `frontend/src/components/expert/CompetencyHeatmap.vue` -- Competency heatmap Vue component requiring `watch` on `props.moduleId`.
- `frontend/src/services/analyticsService.ts` -- Analytics API service interfaces (`HeatmapCell`, `MetricsResponse`).

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/components/expert/CompetencyHeatmap.vue` -- Add `watch` on `props.moduleId` to call `analyticsStore.fetchHeatmap(newModuleId)` when `moduleId` changes post-mount -- Resolves DW-5
- [x] `frontend/src/services/analyticsService.ts` -- Update `HeatmapCell` and `MetricsResponse` interfaces to make `p_learned` and `mastery_speed_days` required `number` fields -- Resolves DW-8

**Acceptance Criteria:**
- Given `CompetencyHeatmap.vue` is mounted, when `props.moduleId` changes, then `analyticsStore.fetchHeatmap` is called with the updated `moduleId`.
- Given `analyticsService.ts`, when imported, then `HeatmapCell.p_learned` and `MetricsResponse.mastery_speed_days` are non-optional `number` types.

## Spec Change Log

## Review Triage Log

### 2026-08-03 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 0
- defer: 0
- reject: 0
- addressed_findings:
  - none

### 2026-08-03 — Review pass (Follow-up)
- intent_gap: 0
- bad_spec: 0
- patch: 0
- defer: 1: (high 0, medium 1, low 0)
- reject: 2
- addressed_findings:
  - none

## Auto Run Result

- **Summary of Implemented Change**: Added a reactive `watch` on `props.moduleId` in `CompetencyHeatmap.vue` to refetch heatmap data when the module selection changes post-mount. Updated `HeatmapCell` and `MetricsResponse` in `analyticsService.ts` to make `p_learned` and `mastery_speed_days` required `number` fields to match backend Pydantic schemas.
- **Files Changed**:
  - `frontend/src/components/expert/CompetencyHeatmap.vue`: Added reactive `watch` on `props.moduleId` to trigger `analyticsStore.fetchHeatmap`.
  - `frontend/src/services/analyticsService.ts`: Updated `HeatmapCell.p_learned` and `MetricsResponse.mastery_speed_days` to required `number`.
  - `_bmad-output/implementation-artifacts/deferred-work.md`: Appended 1 newly deferred finding (backend `mastery_speed` vs frontend `mastery_speed_days` schema discrepancy).
- **Review Findings Breakdown**:
  - Patches applied: 0
  - Items deferred: 1 (naming discrepancy between backend `mastery_speed` and frontend `mastery_speed_days`)
  - Items rejected: 2 (watch behavior and required field checks verified as intentional and correct)
- **Follow-up Review Recommendation**: `false` (no patches applied during review pass)
- **Verification Performed**: Git diff inspection, static analysis, and review passes via Blind Hunter and Edge Case Hunter.
- **Residual Risks**: None identified for this change.



