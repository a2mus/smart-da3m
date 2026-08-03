---
title: 'Story 10.3: Global Language Toggle in App Header'
type: 'feature'
created: '2026-08-03T17:00:00Z'
status: 'ready-for-dev'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-10-context.md', '_bmad-output/planning-artifacts/sprint-change-proposal-2026-08-03.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** Users cannot switch language directly from all pages without navigating away to settings.

**Approach:** Add a permanent, responsive Arabic ↔ Français toggle switch in `AppHeader.vue` that updates the vue-i18n locale, document `dir` (rtl/ltr), and `localStorage` state immediately.

## Boundaries & Constraints

**Always:** Ensure toggle is accessible on all screen sizes. Use logical CSS for positioning and styling.
**Never:** Hardcode physical directional styling (`left-0`, `right-0`).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Toggle Click | User clicks toggle in header | Locale changes, `html` dir updates, state persisted | Fallback to default locale if invalid |

</intent-contract>

## Code Map

- `frontend/src/components/common/AppHeader.vue` -- Insert global language toggle component/button.
- `frontend/src/i18n.ts` or `frontend/src/stores/localeStore.ts` -- Centralized locale switching logic.

## Tasks & Acceptance

**Execution:**
- [ ] Add `LanguageToggle.vue` or direct toggle in `AppHeader.vue`.
- [ ] Bind locale switch to instant update of vue-i18n locale, `document.documentElement.dir`, and `localStorage`.
- [ ] Verify responsive display on mobile and desktop breakpoints.

**Acceptance Criteria:**
- Given any page, a permanent toggle labeled `العربية ↔ Français` is visible in `AppHeader.vue`.
- Clicking toggle switches language and document direction (`rtl` ↔ `ltr`) immediately.
- Selected language persists across browser reloads via `localStorage`.

## Verification

**Commands:**
- `npm --prefix frontend test`
