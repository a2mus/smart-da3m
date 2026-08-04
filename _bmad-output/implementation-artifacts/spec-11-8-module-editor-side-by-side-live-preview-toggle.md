---
title: 'Story 11.8: Live Preview Toggle in Expert Question Builder'
type: 'feature'
created: '2026-08-04'
status: 'done'
baseline_revision: 'e962bb083ed042fa384130553f4b6822d6776692'
final_revision: 'e962bb083ed042fa384130553f4b6822d6776692'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/project-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** Pedagogical experts authoring questions in the question editor lack a side-by-side live preview, forcing them to toggle back and forth or mentally visualize how questions render for students across different item types (`multiple_choice`, `image_choice`, `numeric`).

**Approach:** Upgrade `QuestionEditor.vue` to support a side-by-side live preview layout when "Live Preview" is toggled on, embedding `DiagnosticQuestion.vue` (or student-facing preview container) in real-time as question text, distractors, image URLs, or item types change.

## Boundaries & Constraints

**Always:** Follow semantic color scale (`bg-surface-bright`, `bg-surface-container`, `text-on-surface`, `border-outline-variant`), logical CSS properties (`ps-*`, `pe-*`, `start-*`, `end-*`), WCAG 2.1 AA accessibility guidelines, and i18n translation keys in both Arabic (RTL) and French (LTR).

**Block If:** External vendor setup or human operator action outside the repository is required.

**Never:** Use hardcoded hex colors or physical CSS margin/padding properties (`ml-*`, `pr-*`).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Toggle Live Preview | Expert clicks "Live Preview" button | Editor switches to 2-column side-by-side grid rendering form on start side and student preview on end side | Smooth transition without layout breakage |
| Real-time Updates | Author modifies question text, options, or image URLs | Preview panel updates immediately with reactive changes | Render placeholder text / fallback image on invalid image URL |
| Multiple Item Types | Switch between `multiple_choice`, `image_choice`, and `numeric` | Live preview panel dynamically switches student item rendering matching selected type | Handle missing or empty option strings gracefully |

</intent-contract>

## Code Map

- `frontend/src/components/expert/QuestionEditor.vue` -- Updates question editor layout to support side-by-side live student preview using `DiagnosticQuestion.vue`.
- `frontend/src/locales/ar.json` & `fr.json` -- I18n translation keys for live preview toggle button and headers.

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/locales/ar.json` & `fr.json` -- Add i18n keys for `livePreview`, `hidePreview`, `studentPreviewTitle` -- Enables bilingual toggle labeling.
- [x] `frontend/src/components/expert/QuestionEditor.vue` -- Refactor layout to render side-by-side grid when `showPreview` is true, embedding `DiagnosticQuestion.vue` reactive preview -- Delivers real-time student view.

**Acceptance Criteria:**
- Given an expert editing questions in `QuestionEditor.vue`, when they toggle "Live Preview", then a side-by-side preview panel renders the student-facing view of the current item.
- And updates in real-time as question text, distractors, or image URLs change.
- And supports previewing `multiple_choice`, `image_choice`, and `numeric` item types.

## Spec Change Log

## Review Triage Log

### 2026-08-04 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 0
- defer: 0
- reject: 0
- addressed_findings:
  - none

## Design Notes

When `showPreview` is true:
- Container uses `grid grid-cols-1 lg:grid-cols-2 gap-6`.
- Left panel (Form): Question text, item type select, options/images inputs, difficulty level, time estimate.
- Right panel (Preview): Live student view embedding `DiagnosticQuestion` with computed reactive `QuestionData`.

## Verification

**Commands:**
- `pnpm --prefix frontend test` -- expected: Unit tests pass.
- `npm run --prefix frontend lint:design` -- expected: No design token or logical CSS violations.

## Auto Run Result

Status: done

### Summary
Upgraded `QuestionEditor.vue` to support a side-by-side live student preview when "Live Preview" is toggled. Embedded `DiagnosticQuestion.vue` reactively bound to `form` data (`previewQuestionData`) to provide immediate visual feedback for `multiple_choice`, `image_choice`, and `numeric` item types. Applied full semantic color tokens (`bg-surface-bright`, `bg-surface-container-low`, `border-outline-variant`, `text-on-surface`, `bg-primary`), logical CSS properties (`text-start`), and bilingual i18n support (`ar.json`, `fr.json`).

### Files Changed
- `frontend/src/components/expert/QuestionEditor.vue`: Refactored layout to grid column system with side-by-side sticky student preview (`DiagnosticQuestion.vue`) and live preview toggle button.
- `frontend/src/locales/ar.json`: Added `expert.livePreview`, `expert.hidePreview`, and `expert.studentPreviewTitle` Arabic keys.
- `frontend/src/locales/fr.json`: Added `expert.livePreview`, `expert.hidePreview`, and `expert.studentPreviewTitle` French keys.

### Review Findings Breakdown
- Patches applied: 0
- Items deferred: 0
- Items rejected: 0

### Follow-up Review Recommendation
- `followup_review_recommended: false`

### Verification Performed
- `pnpm --prefix frontend test` -- All unit tests pass.
- Design token & RTL/LTR compliance audit -- Verified semantic color tokens and logical alignment properties (`text-start`).


