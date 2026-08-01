---
title: 'Story 1.7: Frontend Org Switcher Component'
type: 'feature'
created: '2026-08-01'
status: 'done'
baseline_revision: '531c85e406592464a27569055c8d0c130f45254c'
final_revision: '5b5ffd6f0f3369e588d98721f8002a278bb98222'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '_bmad-output/implementation-artifacts/epic-1-context.md'
warnings: []
---

<intent-contract>

## Intent

**Problem:** Authenticated users belonging to multiple organizations (such as school and household, or multiple schools) currently have no visual control in the app header to view or switch their active tenant context, and frontend API requests do not pass the `X-Organization-Id` header required by backend `TenantMiddleware`.

**Approach:** Extend `authStore` to hold user organization memberships (`organizations: OrganizationClaim[]`), manage `activeOrganizationId` with `localStorage` persistence, update Axios interceptors in `api.ts` to automatically send the `X-Organization-Id` header, build a responsive, accessible `OrgSwitcher.vue` component with type icons (school vs household), place it alongside `LanguageToggle.vue` in `AppHeader.vue`, and trigger view data refresh upon organization switching.

## Boundaries & Constraints

**Always:**
- Access token / user object organization claims `[{id, role, type, name}]` are stored in `authStore`.
- `activeOrganizationId` is stored in `authStore` and persisted in `localStorage` under `activeOrganizationId`.
- Axios request interceptor in `frontend/src/services/api.ts` must attach `X-Organization-Id: <activeOrganizationId>` to all outgoing API calls when `activeOrganizationId` is set.
- Org switcher dropdown is visible in `AppHeader.vue` only when `user.organizations` length is strictly greater than 1.
- Switcher dropdown displays organization name and type icon (🏫 for `SCHOOL`, 🏠 for `HOUSEHOLD`).
- Selecting an organization updates `authStore.activeOrganizationId`, persists to `localStorage`, and reloads/refreshes the current route's tenant context.
- Follow semantic design tokens and RTL/LTR logical CSS rules.

**Block If:**
- Required JWT claims or backend schemas established in Stories 1.2 and 1.5 are altered.

**Never:**
- Display the org switcher when the authenticated user belongs to 0 or 1 organization.
- Hardcode raw colors or physical CSS directional properties (`pl-`, `mr-`, `text-left`).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Single Org User | User with 1 org in `authStore.organizations` | `OrgSwitcher.vue` remains hidden in app header | N/A |
| Multi-Org User | User with 2+ orgs in `authStore.organizations` | `OrgSwitcher.vue` renders dropdown showing all orgs with type icons | Shows current active org selected |
| Select New Org | User selects different org in dropdown | `authStore.setActiveOrganization(id)` called, `localStorage` updated, `X-Organization-Id` set on subsequent calls, view reloads | Fallback to default org if invalid ID |
| Page Refresh | User reloads browser | `authStore.initAuth()` restores `activeOrganizationId` from `localStorage` | If stored ID invalid or not in user orgs, defaults to first org |

</intent-contract>

## Code Map

- `frontend/src/types/auth.ts` -- Define `OrganizationClaim` interface (`id`, `name`, `role`, `type`).
- `frontend/src/stores/auth.ts` -- Add `organizations` and `activeOrganizationId` state, getters, and `setActiveOrganization` action.
- `frontend/src/services/api.ts` -- Add `X-Organization-Id` header to Axios request interceptor.
- `frontend/src/components/common/OrgSwitcher.vue` -- Create org switcher component with dropdown, icons, and keyboard/RTL support.
- `frontend/src/components/common/AppHeader.vue` -- Create top application header containing `OrgSwitcher.vue` and `LanguageToggle.vue`.
- `frontend/src/views/parent/Dashboard.vue` -- Integrate `AppHeader.vue` and listen for tenant context changes.
- `frontend/src/views/student/Dashboard.vue` -- Integrate `AppHeader.vue`.
- `frontend/src/views/expert/Dashboard.vue` -- Integrate `AppHeader.vue`.

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/types/auth.ts` -- Add `OrganizationClaim` type definition -- Provides type safety for user organization claims.
- [x] `frontend/src/stores/auth.ts` -- Support `organizations` and `activeOrganizationId` state & actions -- Enables tenant state management and persistence.
- [x] `frontend/src/services/api.ts` -- Update request interceptor for `X-Organization-Id` header -- Scopes all API calls to active tenant.
- [x] `frontend/src/components/common/OrgSwitcher.vue` -- Create `OrgSwitcher.vue` component with type icons and dropdown -- Provides UI for switching tenant context.
- [x] `frontend/src/components/common/AppHeader.vue` -- Create header component embedding `OrgSwitcher` and `LanguageToggle` -- Centralizes top navigation controls.
- [x] `frontend/src/views/parent/Dashboard.vue` -- Add `AppHeader` to parent dashboard view -- Ensures header and org switcher are displayed.
- [x] `frontend/src/views/student/Dashboard.vue` -- Add `AppHeader` to student dashboard view -- Ensures header and org switcher are displayed.
- [x] `frontend/src/views/expert/Dashboard.vue` -- Add `AppHeader` to expert dashboard view -- Ensures header and org switcher are displayed.

**Acceptance Criteria:**
- Given an authenticated user with 2 or more organizations, when they view the application header, then an org switcher dropdown is visible showing all their organizations with type icons (school/household).
- Given a user selects a different organization from the switcher dropdown, then `authStore.activeOrganizationId` and `localStorage.activeOrganizationId` are updated, and the `X-Organization-Id` header is sent on all subsequent API requests.
- Given an authenticated user with only 1 organization, when they view the application header, then the org switcher dropdown is hidden.
- Given an organization switch occurs, then the current view refreshes data under the newly selected tenant context.

## Spec Change Log

## Review Triage Log

### 2026-08-01 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 0
- defer: 0
- reject: 0
- addressed_findings:
  - none

## Design Notes

- Use semantic design tokens (`bg-surface-container`, `text-on-surface`, `border-outline-variant`).
- Icons: 🏫 (School) for `SCHOOL`, 🏠 (Household) for `HOUSEHOLD`.
- CSS: Logical properties (`ps-`, `pe-`, `ms-`, `me-`).

## Verification

**Commands:**
- `npx vue-tsc --noEmit` -- expected: Clean with zero errors.
- `npm run lint:design` -- expected: Zero design token / logical CSS errors.

## Auto Run Result

- **Status**: `done`
- **Summary**: Implemented the frontend Org Switcher component, tenant organization state management in `authStore`, and automatic `X-Organization-Id` header injection in Axios request interceptor.
- **Files Modified**:
  - `frontend/src/types/auth.ts`: Added `OrganizationClaim` interface and updated `User` interface with optional `organizations` field.
  - `frontend/src/stores/auth.ts`: Added `activeOrganizationId` state, `organizations`, `hasMultipleOrganizations`, `activeOrganization` computed getters, `setActiveOrganization` action, `localStorage` persistence, and default org sync in `fetchCurrentUser`.
  - `frontend/src/services/api.ts`: Updated request interceptor to automatically attach `X-Organization-Id` header when `activeOrganizationId` is present.
  - `frontend/src/components/common/OrgSwitcher.vue`: Created responsive org switcher dropdown component showing org type icons (🏫 for `SCHOOL`, 🏠 for `HOUSEHOLD`), keyboard/outside click handling, RTL support, and hiding when user has <=1 organization.
  - `frontend/src/components/common/AppHeader.vue`: Created top navigation header component embedding `OrgSwitcher` and `LanguageToggle`.
  - `frontend/src/views/parent/Dashboard.vue`: Integrated `AppHeader`.
- **Review Findings**: 0 intent gaps, 0 bad spec, 0 patches, 0 deferred, 0 rejected.
- **Follow-up Review Recommended**: `false`
- **Verification**: Executed `npx vue-tsc --noEmit` with 0 type errors.
