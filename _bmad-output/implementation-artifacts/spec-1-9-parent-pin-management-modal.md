---
title: 'Story 1.9: Parent PIN Management Modal'
type: 'feature'
created: '2026-08-03T17:00:00Z'
status: 'ready-for-dev'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-1-context.md', '_bmad-output/planning-artifacts/sprint-change-proposal-2026-08-03.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** Parents currently have no way to view or reset their child's 4-digit PIN directly from the dashboard if the child forgets it.

**Approach:** Build a Parent PIN Management Modal accessible from the parent dashboard header/child selector that lists all children in the household org, shows their masked PIN with a 5-second reveal toggle, and allows generating/updating a new PIN via `POST /api/v1/auth/children/{id}/pin`.

## Boundaries & Constraints

**Always:** Enforce parent ownership (`parent_id` check and RBAC). Use i18n keys for all labels.
**Never:** Expose unmasked PINs permanently in the UI.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| View PINs | Parent opens modal | Lists children with masked PINs | Handle 403 if unauthorized |
| Reveal PIN | Parent clicks reveal | Shows PIN for 5 seconds then auto-masks | N/A |
| Reset PIN | Parent submits new PIN | Sends request, updates state, shows success toast | API error notification |

</intent-contract>

## Code Map

- `frontend/src/views/parent/Dashboard.vue` -- Trigger button and PIN modal integration.
- `frontend/src/components/parent/PinManagementModal.vue` -- Modal component for PIN view/reset.
- `frontend/src/stores/auth.ts` or `frontend/src/services/dashboardService.ts` -- Service method to trigger PIN reset endpoint.
- `backend/app/api/endpoints/auth.py` -- Endpoint `POST /api/v1/auth/children/{id}/pin` for PIN updating.

## Tasks & Acceptance

**Execution:**
- [ ] Create `PinManagementModal.vue` with child PIN list, temporary reveal, and PIN update form.
- [ ] Add PIN reset endpoint `POST /api/v1/auth/children/{id}/pin` in backend auth router if not already present.
- [ ] Wire modal trigger in `frontend/src/views/parent/Dashboard.vue`.
- [ ] Add unit tests for PIN management component and backend endpoint.

**Acceptance Criteria:**
- Given a parent on their dashboard, when they tap "Manage Children & PINs", then a modal shows each child's name and masked PIN.
- When parent clicks reveal, the PIN is displayed temporarily for 5 seconds.
- When parent updates PIN, `POST /api/v1/auth/children/{id}/pin` updates the database and parent sees confirmation.
- Only the owning parent can access or update the PIN.

## Verification

**Commands:**
- `npm --prefix frontend test`
- `pytest backend/tests/`
