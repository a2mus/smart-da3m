---
title: 'Story 11.4: Global Language Toggle in App Header'
type: 'feature'
created: '2026-08-04'
status: 'review'
baseline_revision: '87d4f7ce4b8e69574d797fc58ae7adbc15632cdf'
final_revision: '87d4f7ce4b8e69574d797fc58ae7adbc15632cdf'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/planning-artifacts/epics.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** Users need an accessible, permanent language toggle switch in the top header to switch between Arabic (RTL) and French (LTR) instantly from anywhere in the application.

**Approach:** Integrated `AppHeader.vue` containing `LanguageToggle.vue` globally in `App.vue`, ensuring logical CSS compliance (`ps-*`, `pe-*`, `ms-*`, `me-*`, `start-*`, `end-*`) and reactive `dir` attribute updates (`rtl` ↔ `ltr`) persisted to `localStorage`.

## Boundaries & Constraints

**Always:** Ensure `LanguageToggle.vue` uses logical CSS properties exclusively and updates `dir` instantly without page reload.

</intent-contract>

## Code Map

- `frontend/src/App.vue` -- Root view mounting `AppHeader.vue` globally
- `frontend/src/components/common/AppHeader.vue` -- Top header component with brand, tenant switcher, and language toggle
- `frontend/src/components/common/LanguageToggle.vue` -- Language toggle component executing instant `ar` ↔ `fr` locale and RTL ↔ LTR direction switching

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/components/common/LanguageToggle.vue` -- Update component styling to use logical CSS properties and display explicit language/RTL/LTR indicators
- [x] `frontend/src/App.vue` -- Mount `AppHeader.vue` globally at top of main layout

**Acceptance Criteria:**
- Given a user on any route in the application
- When they view the header
- Then the language toggle is visible and permits instant switching between Arabic (`ar`, RTL) and French (`fr`, LTR)
- And the document direction (`dir`) attribute flips reactively without requiring a page reload
- And the selection is persisted in `localStorage`
