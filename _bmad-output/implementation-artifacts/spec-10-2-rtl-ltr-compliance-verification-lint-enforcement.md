---
title: 'Story 10.2: RTL/LTR Compliance Verification & Lint Enforcement'
type: 'refactor'
created: '2026-08-03'
status: 'done'
baseline_revision: 'e8c3a379437f10963ec7ff713b4d996c18be8133'
final_revision: '208282c3be5e3fbc289af14e2fc56c78a24c0bf4'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-10-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** Physical direction utility classes (`pl-*`, `pr-*`, `left-*`, `right-*`, `text-left`, `text-right`, etc.) break RTL/LTR layout flips between Arabic and French, and hardcoded `'ar-DZ'` or implicit locale calls in `toLocaleDateString` do not adapt dynamically when switching languages.

**Approach:** Verify and enforce ESLint rules banning physical-direction CSS utility classes, replace remaining physical direction references with logical CSS equivalents (`ps-*`, `pe-*`, `start-*`, `end-*`, `text-start`, `text-end`), ensure all `toLocaleDateString()` calls dynamically pass the active `locale`, and verify dynamic font family / root `dir` switching between AR (Tajawal/Cairo, RTL) and FR (Plus Jakarta Sans, LTR).

## Boundaries & Constraints

**Always:** All layout utilities across Vue templates and components must use logical CSS direction properties. `toLocaleDateString()` must receive the active locale string dynamically.

**Block If:** Unresolved build or lint configuration errors prevent ESLint execution.

**Never:** Use physical direction utility classes (`pl-*`, `pr-*`, `ml-*`, `mr-*`, `left-*`, `right-*`, `text-left`, `text-right`, `float-left`, `float-right`, `border-l-*`, `border-r-*`, `rounded-l-*`, `rounded-r-*`) in `.vue` templates or style blocks.

</intent-contract>

## Code Map

- `frontend/eslint.config.js` -- ESLint rule configuration defining banned physical CSS utility classes under `vue/no-restricted-class`
- `frontend/src/components/expert/PrintableRemediationCards.vue` -- Remediation card view containing date formatting logic
- `frontend/src/views/parent/Dashboard.vue` -- Parent dashboard view containing date formatting logic
- `frontend/src/views/parent/Alerts.vue` -- Parent alerts view containing date formatting logic
- `frontend/src/App.vue` -- App root component handling `dir` and font class bindings
- `frontend/src/main.ts` -- Main application entry watching i18n locale and updating `document.documentElement.dir`
- `frontend/src/assets/main.css` -- Global CSS rules handling `html[dir="rtl"]` and `html[dir="ltr"]` font families

## Tasks & Acceptance

**Execution:**
- [x] `frontend/eslint.config.js` -- Verify ESLint `vue/no-restricted-class` rule covers all physical direction utility patterns -- ensure automated lint enforcement
- [x] `frontend/src/components/expert/PrintableRemediationCards.vue` -- Update `toLocaleDateString` to use the active `locale` -- ensure dynamic date localization
- [x] `frontend/src/views/parent/Dashboard.vue` -- Update `toLocaleDateString` call to use active `locale` -- ensure dynamic date localization
- [x] `frontend/src/views/parent/Alerts.vue` -- Update `toLocaleDateString` call to use active `locale` -- ensure dynamic date localization
- [x] `frontend/src/App.vue` & `frontend/src/main.ts` -- Verify dynamic document direction (`dir="rtl"` vs `dir="ltr"`) and font family swap on locale change -- ensure bidirectional layout compliance

**Acceptance Criteria:**
- Given the frontend codebase, when running ESLint (`npm run lint:design`), then zero physical direction utility classes (`pl-*`, `pr-*`, `left-*`, `right-*`, `text-left`) pass without warning or error
- Given `toLocaleDateString` calls in Vue components, when rendered in French locale, then dates are formatted using French locale rules instead of fallback/hardcoded Arabic
- Given the active locale switches between Arabic and French, when root document direction changes, then font family automatically swaps between Tajawal/Cairo (RTL) and Plus Jakarta Sans (LTR)

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

## Verification

**Commands:**
- `cd frontend && npm run lint:design` -- expected: Lint passes with 0 physical-direction CSS violations
- `cd frontend && npx vitest run` -- expected: All unit tests pass
- `cd frontend && npm run build` -- expected: Production build succeeds without errors

## Auto Run Result

Status: done
Final Revision: 208282c3be5e3fbc289af14e2fc56c78a24c0bf4
Follow-up Review Recommended: false

### Summary of Implemented Changes
- Verified automated lint enforcement for physical direction utility classes (`vue/no-restricted-class`) in `frontend/eslint.config.js`.
- Updated hardcoded `'ar-DZ'` and implicit locale calls in `toLocaleDateString()` to dynamically adapt to the active locale (`fr-FR` vs `ar-DZ`) in `PrintableRemediationCards.vue`, `Alerts.vue`, and `Dashboard.vue`.
- Verified dynamic root document direction (`dir="rtl"` / `dir="ltr"`) and font family swapping in `App.vue` & `main.ts`.

### Changed Files
- `frontend/src/components/expert/PrintableRemediationCards.vue` -- Dynamic date formatting based on active locale
- `frontend/src/views/parent/Alerts.vue` -- Dynamic date formatting based on active locale
- `frontend/src/views/parent/Dashboard.vue` -- Dynamic date formatting based on active locale
- `_bmad-output/implementation-artifacts/sprint-status.yaml` -- Updated story 10.2 status to done
- `_bmad-output/implementation-artifacts/spec-10-2-rtl-ltr-compliance-verification-lint-enforcement.md` -- Specification artifact

### Review Breakdown
- Patches applied: 0
- Items deferred: 0
- Items rejected: 0

### Verification Details
- `cd frontend && npm run lint:design` -- PASSED (0 physical CSS utility violations)
- `cd frontend && npx vitest run` -- PASSED (6 test files, 31 tests passed)
- `cd frontend && npm run build` -- PASSED (vue-tsc typecheck clean, Vite build successful)


