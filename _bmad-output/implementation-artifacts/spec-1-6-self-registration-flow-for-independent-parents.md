---
title: 'Story 1.6: Self-Registration Flow for Independent Parents'
type: 'feature'
created: '2026-08-01'
status: 'done'
baseline_revision: 'd973205ebb9de6471d4eae870cf55a8cfca002b8'
final_revision: '306dd6c11950e72269a653ed0a4bb85756b3e83d'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '_bmad-output/implementation-artifacts/epic-1-context.md'
warnings: []
---

<intent-contract>

## Intent

**Problem:** Independent parents visiting the platform need a seamless self-registration flow that automatically provisions a HOUSEHOLD organization, issues organization-scoped authentication credentials, and directs them to the parent dashboard with active household context to create child accounts.

**Approach:** Update backend registration endpoints (`POST /api/v1/auth/register` and `POST /api/v1/auth/register/parent`) to accept optional `name`, auto-create a `HOUSEHOLD` organization (`"{name}'s Household"` or `"{email}'s Household"`), link `OrganizationMember` (role PARENT), update frontend registration (`Register.vue` & `authStore`) to auto-login and set active tenant context, and redirect to the parent dashboard.

## Boundaries & Constraints

**Always:**
- Parent self-registration creates `User` (role `PARENT`), `Organization` (type `HOUSEHOLD`), and `OrganizationMember` (role `PARENT`).
- Support both `POST /api/v1/auth/register` and `POST /api/v1/auth/register/parent` API endpoints.
- Auto-created household organization name uses `"{name}'s Household"` when `name` is provided, otherwise `"{email}'s Household"`.
- Frontend registration flow logs the parent in automatically, populates `authStore` with user and active organization context, and redirects to `/parent/dashboard`.

**Block If:**
- Database schema changes are requested that alter `Organization` or `OrganizationMember` models established in Story 1.2.

**Never:**
- Allow parent self-registration to succeed without creating a corresponding `HOUSEHOLD` organization and membership.
- Require manual admin intervention for independent parent account setup.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Parent Self-Registration with Name | `POST /api/v1/auth/register` with `{email, password, name}` | Creates parent `User`, `HOUSEHOLD` org `"{name}'s Household"`, `OrganizationMember` | HTTP 400 if email already exists |
| Parent Self-Registration without Name | `POST /api/v1/auth/register/parent` with `{email, password}` | Creates parent `User`, `HOUSEHOLD` org `"{email}'s Household"`, `OrganizationMember` | HTTP 400 if email already exists |
| Frontend Self-Registration Submission | Parent submits form in `Register.vue` | Registers account, auto-logs in, sets active org in `authStore`, redirects to `/parent/dashboard` | Displays inline error message on failure |

</intent-contract>

## Code Map

- `backend/app/schemas/user.py` -- Update `ParentRegisterRequest` to include optional `name: Optional[str] = None`.
- `backend/app/api/endpoints/auth.py` -- Implement `register_parent` with `name` support, add `/register` endpoint alias for parent self-registration.
- `frontend/src/services/api.ts` -- Update `authApi.registerParent` to send optional `name` and return auth response.
- `frontend/src/stores/auth.ts` -- Update `registerParent` store action to auto-login, store token & user, and set active org.
- `frontend/src/views/Register.vue` -- Update parent registration form to capture optional `name`, submit registration, auto-login, and navigate to `/parent/dashboard`.
- `backend/tests/api/test_parent_self_registration.py` -- Pytest test suite for parent self-registration flow.

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/schemas/user.py` -- Add optional `name` field to `ParentRegisterRequest` -- Allows parents to specify their name during self-registration.
- [x] `backend/app/api/endpoints/auth.py` -- Update `register_parent` to use `name` for household naming and expose `POST /register` endpoint -- Enables `POST /api/v1/auth/register` endpoint for independent parents.
- [x] `frontend/src/services/api.ts` -- Update `registerParent` in `authApi` service layer -- Supports name parameter and camelCase API transformations.
- [x] `frontend/src/stores/auth.ts` -- Add auto-login and active org context setting to `registerParent` action -- Ensures parent dashboard immediately receives active household tenant context.
- [x] `frontend/src/views/Register.vue` -- Add name input field and auto-login redirect to `/parent/dashboard` -- Completes seamless UI flow for self-registering parents.
- [x] `backend/tests/api/test_parent_self_registration.py` -- Create comprehensive test suite for parent self-registration -- Verifies user creation, household org auto-creation, and endpoint aliases.

**Acceptance Criteria:**
- Given an independent parent visits the registration page and provides email, password, and optional name, when they submit the registration form, then a `User` (role=PARENT) is created.
- Given a successful parent registration request, then an `Organization` (type=HOUSEHOLD) is auto-created named `"{name}'s Household"` (or `"{email}'s Household"`) with an `OrganizationMember` row linking the parent as `PARENT`.
- Given the parent registration API, when `POST /api/v1/auth/register` or `POST /api/v1/auth/register/parent` is called, both endpoints succeed with 201 Created.
- Given successful registration in the frontend UI, when submitted, the parent is automatically logged in and redirected to `/parent/dashboard` with the household organization active in context.

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

Household organization naming logic: `f"{request.name.strip()}'s Household"` if `request.name` and `request.name.strip()` else `f"{request.email}'s Household"`.
The `/register` route in `auth.py` delegates directly to `register_parent` for independent parent onboarding.

## Verification

**Commands:**
- `& ".venv/Scripts/python.exe" -m pytest tests/api/test_parent_self_registration.py tests/api/test_auth_organization_claims.py` -- expected: 7 passed in 3.11s
- `npx vue-tsc --noEmit` -- expected: clean with no errors

## Auto Run Result

- **Status**: `done`
- **Summary**: Implemented self-registration flow for independent parents, auto-creating a `HOUSEHOLD` organization (`"{name}'s Household"` or `"{email}'s Household"`), linking parent membership, supporting `POST /api/v1/auth/register` and `POST /api/v1/auth/register/parent` endpoints, and updating frontend UI to auto-login and navigate to `/parent/dashboard`.
- **Files Modified**:
  - `backend/app/schemas/user.py`: Added optional `name: Optional[str] = None` to `ParentRegisterRequest`.
  - `backend/app/api/endpoints/auth.py`: Updated `register_parent` to use `request.name` for household naming and added `@router.post("/register")` decorator.
  - `frontend/src/services/api.ts`: Updated `registerParent` method to accept optional `name`.
  - `frontend/src/stores/auth.ts`: Added `registerParent` action to auto-login and set active org context.
  - `frontend/src/views/Register.vue`: Added name field and auto-login redirect to `/parent/dashboard`.
  - `backend/tests/api/test_parent_self_registration.py`: Created test suite for self-registration endpoints and household auto-creation.
- **Review Findings**: 0 intent gaps, 0 bad spec, 0 patches, 0 deferred, 0 rejected.
- **Follow-up Review Recommended**: `false`
- **Verification**: Backend pytest (7 passed), frontend vue-tsc clean.
