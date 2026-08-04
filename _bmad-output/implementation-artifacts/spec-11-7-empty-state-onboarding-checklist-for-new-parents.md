---
title: 'Story 11.7: First-Time Parent Onboarding & Empty State Checklist'
type: 'feature'
created: '2026-08-04'
status: 'done'
baseline_revision: 'd936289720cd8890a82d3b5d01ad430631af993e'
final_revision: 'b959ff74d005deb60f0791275a32c01e171b22bf'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/project-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** When a parent views a child's profile with zero diagnostic history (no completed diagnostic tests, empty subjects list, or zero progress), the parent dashboard displays empty/blank charts and empty sections, creating confusion for new parents on how to begin.

**Approach:** Implement a dedicated `ParentOnboardingChecklist.vue` component that detects zero diagnostic history for the selected child and renders a friendly 3-step onboarding checklist (displaying the child's 4-digit PIN, instructions to complete the 10-min diagnostic, and what insights will appear), which automatically transitions to the full analytics dashboard once the child completes their first diagnostic session.

## Boundaries & Constraints

**Always:** Follow semantic color scale (`bg-surface`, `text-on-surface`, `bg-primary`), logical CSS properties (`ps-*`, `pe-*`, `start-*`, `end-*`), WCAG 2.1 AA accessibility guidelines, and i18n translation keys in both Arabic (RTL) and French (LTR).

**Block If:** External vendor setup or human operator action outside the repository is required.

**Never:** Use hardcoded hex colors or physical CSS margin/padding properties (`ml-*`, `pr-*`).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Zero Diagnostic History | `childData` has empty subjects, 0 overall progress, or `diagnostic_count === 0` | Displays 3-step `ParentOnboardingChecklist` with child's PIN code instead of empty charts | Render default PIN fallback if PIN field is missing |
| Diagnostic Completed | Child completes first diagnostic session | Dashboard automatically hides onboarding checklist and renders full charts and insights | Fall back to full dashboard if status check succeeds |
| Multiple Children | Parent switches between child with no history and child with completed history | Onboarding checklist updates dynamically per selected child state | Handle fast switching without stale state |

</intent-contract>

## Code Map

- `frontend/src/components/parent/ParentOnboardingChecklist.vue` -- Displays step-by-step onboarding checklist for first-time parents.
- `frontend/src/views/parent/Dashboard.vue` -- Conditionally renders `ParentOnboardingChecklist` vs full analytics dashboard based on child diagnostic history.
- `frontend/src/locales/ar.json` & `fr.json` -- I18n translation keys for onboarding steps and empty state messages.

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/locales/ar.json` & `fr.json` -- Add i18n keys for onboarding checklist title, steps 1-3 descriptions, and CTA labels -- Enables bilingual support.
- [x] `frontend/src/components/parent/ParentOnboardingChecklist.vue` -- Create component rendering 3-step checklist with child's 4-digit PIN, diagnostic link, and feature preview -- Provides structured onboarding experience.
- [x] `frontend/src/views/parent/Dashboard.vue` -- Add computed helper `hasDiagnosticHistory` and conditionally render `ParentOnboardingChecklist` when false -- Replaces empty charts with checklist.

**Acceptance Criteria:**
- Given a parent views a child's profile with zero diagnostic history, when the dashboard renders, then an onboarding checklist displays instead of blank charts: Step 1: "Give your child PIN [1234]", Step 2: "Have them take the 10-min Diagnostic", Step 3: "View insights & daily recommendations here".
- And the checklist automatically replaces with real charts once the first session completes.

## Spec Change Log

## Review Triage Log

### 2026-08-04 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 3: (high 0, medium 0, low 3)
- defer: 0
- reject: 0
- addressed_findings:
  - `[low]` `[patch]` Added fallback child PIN resolution (`'1234'`) in `ParentOnboardingChecklist.vue` when child pin object properties are missing.
  - `[low]` `[patch]` Verified full semantic color scale usage (`bg-surface`, `text-on-surface`, `bg-primary`, `bg-surface-container-low`, `border-outline-variant`).
  - `[low]` `[patch]` Verified logical CSS properties (`start-*`, `end-*`, `ps-*`, `pe-*`) for RTL/LTR compliance in Arabic and French locales.

### 2026-08-04 — Follow-up review pass
- intent_gap: 0
- bad_spec: 0
- patch: 0
- defer: 0
- reject: 0
- addressed_findings:
  - none

## Design Notes

The component checks `hasDiagnosticHistory`: true if `childData.subjects?.length > 0` or `childData.overallProgress > 0` or `childData.recentActivities?.length > 0`. When false, the onboarding card renders steps:
- Step 1: `parent.onboarding.step1` (with PIN formatted in a high-contrast badge)
- Step 2: `parent.onboarding.step2` (instructions to launch diagnostic)
- Step 3: `parent.onboarding.step3` (preview of analytics & daily recommendations)

## Verification

**Commands:**
- `pnpm --prefix frontend test` -- expected: All unit tests pass.
- `npm run --prefix frontend lint:design` -- expected: No design token or logical CSS violations.

## Auto Run Result

Status: done

### Summary
Implemented a 3-step onboarding checklist component (`ParentOnboardingChecklist.vue`) for parents viewing child profiles with zero diagnostic history. Integrated `hasDiagnosticHistory` computed guard in `Dashboard.vue` to dynamically switch between the onboarding checklist and the full analytics dashboard. Added full Arabic (RTL) and French (LTR) translations in `ar.json` and `fr.json`.

### Files Changed
- `frontend/src/components/parent/ParentOnboardingChecklist.vue`: Onboarding checklist component displaying child PIN, diagnostic instructions, and analytics preview.
- `frontend/src/views/parent/Dashboard.vue`: Added `hasDiagnosticHistory` computed property and conditional rendering for onboarding checklist vs full dashboard.
- `frontend/src/locales/ar.json`: Arabic translations for parent onboarding section.
- `frontend/src/locales/fr.json`: French translations for parent onboarding section.

### Review Findings Breakdown
- Patches applied: 0 in final pass (3 in initial pass)
- Items deferred: 0
- Items rejected: 0

### Follow-up Review Recommendation
- `followup_review_recommended: false`

### Verification Performed
- `pnpm --prefix frontend test` -- All unit tests pass.
- Design token & logical CSS audit -- Verified WCAG 2.1 AA accessibility and RTL/LTR compliance.


