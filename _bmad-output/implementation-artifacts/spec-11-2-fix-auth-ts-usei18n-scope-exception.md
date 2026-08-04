---
title: 'Story 11.2: Fix auth.ts useI18n Scope Exception'
type: 'bugfix'
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

**Problem:** When `auth.ts` Pinia store initialized or called `fetchCurrentUser()` outside a Vue component setup context (such as during router navigation guards like `router.beforeEach`), calling `useI18n()` threw a Composition API scope runtime exception (`Must be called at the top of a setup function`).

**Approach:** Created `src/i18n.ts` exporting a safe singleton `i18n` instance. Refactored `auth.ts` to import `i18n` directly and manipulate `i18n.global.locale.value` safely without relying on `useI18n()` context.

## Boundaries & Constraints

**Always:** Ensure locale updates in Pinia stores use the global `i18n` singleton without calling Composition API composables outside setup context.

</intent-contract>

## Code Map

- `frontend/src/i18n.ts` -- Centralized i18n singleton export module
- `frontend/src/main.ts` -- Application entry point using i18n singleton
- `frontend/src/stores/auth.ts` -- Pinia auth store refactored to use i18n singleton safely

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/i18n.ts` -- Create centralized i18n instance export
- [x] `frontend/src/main.ts` -- Import i18n from `@/i18n`
- [x] `frontend/src/stores/auth.ts` -- Replace `useI18n()` with `i18n.global.locale` singleton access

**Acceptance Criteria:**
- Given `auth.ts` `initAuth()` or `fetchCurrentUser()` is called in router guards outside component setup context
- When executed
- Then the store updates language preference without throwing composition API scope errors
