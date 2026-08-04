---
title: 'Story 11.1: Fix Register.vue Route Redirection Bug'
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

**Problem:** When a new parent registers on the platform via `Register.vue`, upon successful submission the router attempts to navigate to `router.push('/parent/dashboard')`. However, the Vue Router config defines the parent dashboard route path as `/parent` (named `'ParentDashboard'`). Navigation to `/parent/dashboard` causes a 404 Not Found error.

**Approach:** Update `Register.vue` line 53 to redirect to `router.push('/parent')`.

## Boundaries & Constraints

**Always:** Ensure parent self-registration successfully redirects to the existing `/parent` route upon completion.

**Never:** Break existing form validation or error handling in `Register.vue`.

</intent-contract>

## Code Map

- `frontend/src/views/Register.vue` -- Parent registration view containing the broken router navigation path

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/views/Register.vue` -- Change `router.push('/parent/dashboard')` to `router.push('/parent')`

**Acceptance Criteria:**
- Given a new parent completes self-registration in `Register.vue`
- When registration succeeds
- Then the router redirects to `/parent` without encountering a 404 page
