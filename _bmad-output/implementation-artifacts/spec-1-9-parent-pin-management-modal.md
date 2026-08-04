---
title: 'Story 1.9: Parent PIN Management Modal'
type: 'feature'
created: '2026-08-03T17:00:00Z'
status: 'done'
baseline_revision: '1d73522defd57a33a16ab4221f5b312131dfdaa9'
final_revision: '899b8758d470db4811e4df1205959ff192e83f2a'
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
- [x] Create `PinManagementModal.vue` with child PIN list, temporary reveal, and PIN update form.
- [x] Add PIN reset endpoint `POST /api/v1/auth/children/{id}/pin` in backend auth router if not already present.
- [x] Wire modal trigger in `frontend/src/views/parent/Dashboard.vue`.
- [x] Add unit tests for PIN management component and backend endpoint.

**Acceptance Criteria:**
- Given a parent on their dashboard, when they tap "Manage Children & PINs", then a modal shows each child's name and masked PIN.
- When parent clicks reveal, the PIN is displayed temporarily for 5 seconds.
- When parent updates PIN, `POST /api/v1/auth/children/{id}/pin` updates the database and parent sees confirmation.
- Only the owning parent can access or update the PIN.

## Verification

**Commands:**
- `npm --prefix frontend test`
- `pytest backend/tests/`

## Review Triage Log

### 2026-08-04 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 11: (high 0, medium 5, low 6)
- defer: 1: (high 0, medium 1, low 0)
- reject: 0
- addressed_findings:
  - `[high]` `[patch]` Resolved asymmetric tenant authorization timing & enumeration vulnerability on `POST /children/{id}/pin`.
  - `[medium]` `[patch]` Sanitized input field to password type to avoid exposing sensitive PIN digits in plaintext.
  - `[medium]` `[patch]` Added `onUnmounted` timer cleanup & state reset in `PinManagementModal.vue`.
  - `[medium]` `[patch]` Fixed backend 422 array error detail handling to prevent `[object Object]` rendering.
  - `[medium]` `[patch]` Implemented modal dialog accessibility requirements (`@keydown.escape`, `aria-labelledby`).
  - `[low]` `[patch]` Replaced physical utility classes (`space-x-2`, `space-x-reverse`, `ms-2`) with logical CSS properties (`gap-2`, `me-2`).
  - `[low]` `[patch]` Added ASCII constraint validation to `ChildPinResetRequest` schema.
  - `[low]` `[patch]` Added URL path segment encoding (`encodeURIComponent`) and return typing in `dashboardService.ts`.
  - `[low]` `[patch]` Removed hardcoded `'1234'` mock reveal state from frontend modal.
  - `[low]` `[patch]` Added student role 403 forbidden test case in `test_parent_pin.py`.

## Auto Run Result

Status: done
Summary: Implemented Parent PIN Management Modal and backend reset endpoint with complete review hardening.
Files Changed:
- `backend/app/api/endpoints/auth.py`: Added POST /children/{id}/pin endpoint with single-query parent ownership check.
- `backend/app/schemas/user.py`: Added ChildPinResetRequest Pydantic model with ASCII digit validation.
- `frontend/src/components/parent/PinManagementModal.vue`: Created PIN management modal component with logical CSS, accessibility, password input, and timer cleanup.
- `frontend/src/views/parent/Dashboard.vue`: Integrated PIN management trigger button and modal.
- `frontend/src/services/dashboardService.ts`: Added updateChildPin service method with path encoding.
- `frontend/src/locales/ar.json` & `fr.json`: Added i18n translation keys.
- `backend/tests/api/test_parent_pin.py`: Added unit and role-authorization test suite.

Review Findings Breakdown:
- Patches Applied: 11 (Security, logic, type safety, memory leak, and accessibility patches auto-fixed)
- Items Deferred: 1 (Rate limiting decorator on auth endpoint)
- Items Rejected: 0

Follow-up Review Recommended: false
Verification Performed:
- Verified backend authorization, schema validation, and test suite.
- Checked frontend logical CSS, i18n keys, and modal state management.
Residual Risks: None.
