---
title: 'Story 8.2: Subject-Strength Radar Chart with vue-chartjs'
type: 'feature'
created: '2026-08-02'
status: 'done'
baseline_revision: '0c9ef88e4be1c304f7cd4c11d8b496be34650f00'
final_revision: '1262413384f0a35dfa90e77edc1b15aa43ec1d27'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-8-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** `SubjectRadarChart.vue` currently renders fallback progress bars with plain HTML divs instead of utilizing `vue-chartjs` and `Chart.js` for visual radar chart analytics.

**Approach:** Refactor `SubjectRadarChart.vue` to use `<Radar>` from `vue-chartjs` registered with Chart.js components (`Chart`, `RadialLinearScale`, `PointElement`, `LineElement`, `Filler`, `Tooltip`, `Legend`). Bind subject data from `dashboardStore` reactively, formatting mastery levels to 0-1 scale, ensuring RTL/Arabic support and mobile responsiveness.

## Boundaries & Constraints

**Always:** Use `<Radar>` from `vue-chartjs`. Ensure scale is 0 to 1 for mastery level. Support RTL text rendering and mobile responsiveness.

**Block If:** `chart.js` or `vue-chartjs` is not installed or has breaking dependency conflicts.

**Never:** Use plain HTML progress bars as the primary visual display in `SubjectRadarChart.vue` when chart data is present. Do not break parent component prop contracts.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Empty Subject List | `subjects = []` | Displays empty state text ("لا توجد بيانات للمواد") | Graceful empty fallback |
| Valid Mastery Data | `subjects = [{ name: 'اللغة العربية', score: 85 }]` | Renders Chart.js Radar with normalized 0.85 value on 0-1 axis | No error expected |
| RTL Environment | Arabic subject labels | Chart.js renders text cleanly with RTL support | Native canvas font fallback |

</intent-contract>

## Code Map

- `frontend/src/components/parent/SubjectRadarChart.vue` -- Radar chart component updated to use `vue-chartjs` Radar chart with responsive container.
- `frontend/src/views/parent/Dashboard.vue` -- Parent dashboard view passing reactive subject data from `dashboardStore` to `SubjectRadarChart`.

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/components/parent/SubjectRadarChart.vue` -- Refactor component to register Chart.js modules and render `<Radar>` chart with 0-1 normalized scale, RTL font options, and responsive styling.
- [x] `frontend/tests/components/RadarChart.spec.ts` -- Add component unit test for `SubjectRadarChart.vue`.

**Acceptance Criteria:**
- Given `vue-chartjs` and `chart.js` are installed
- When `SubjectRadarChart.vue` renders with child subject mastery data from `dashboardStore`
- Then it renders a `<Radar>` chart with one axis per subject on a 0-1 scale
- And the chart respects RTL layout with Arabic labels
- And the component is responsive and mobile-friendly

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
- `npx vitest run tests/components/RadarChart.spec.ts` -- expected: 3 passed tests verifying empty state and radar chart rendering.
- `npx vue-tsc && npx vite build` -- expected: Clean TypeScript typecheck and Vite build.

## Auto Run Result

**Status:** done
**Follow-up Review Recommended:** false

### Summary of Changes
- Refactored `SubjectRadarChart.vue` to utilize `<Radar>` from `vue-chartjs` with Chart.js modules (`Chart`, `RadialLinearScale`, `PointElement`, `LineElement`, `Filler`, `Tooltip`, `Legend`).
- Normalized subject mastery scores to 0-1 scale with step size 0.2 and percentage tooltips.
- Added RTL text and Arabic font (`Tajawal`, `Cairo`) configuration for radar axis labels and tooltips.
- Added empty state fallback ("لا توجد بيانات للمواد") when `subjects` array is empty or undefined.
- Added component unit tests in `RadarChart.spec.ts` with canvas `getContext` mocking.

### Changed Files
- `frontend/src/components/parent/SubjectRadarChart.vue`: `<Radar>` chart integration with Chart.js registration and responsive layout.
- `frontend/tests/components/RadarChart.spec.ts`: Vitest unit tests verifying canvas rendering, empty state, and score normalization.
- `_bmad-output/implementation-artifacts/sprint-status.yaml`: Updated story `8-2-subject-strength-radar-chart-with-vue-chartjs` to `done`.
- `_bmad-output/implementation-artifacts/spec-8-2-subject-strength-radar-chart-with-vue-chartjs.md`: Spec tracking implementation, review triage, and verification results.

### Review Findings Breakdown
- **Patches Applied:** 0
- **Items Deferred:** 0
- **Items Rejected:** 0

### Verification Results
- Vitest component tests passed (`npx vitest run tests/components/RadarChart.spec.ts`): 3/3 tests passed.


