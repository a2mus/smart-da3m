---
title: 'Story 1.5: JWT Organization Claims & Auth Flow Update'
type: 'feature'
created: '2026-08-01'
status: 'done'
baseline_revision: 'c8b66bff38ef476eed6f847df605fc40e9cff53a'
final_revision: '1c57fb35b756e29a597f24fd74df801366ca6d82'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '_bmad-output/implementation-artifacts/epic-1-context.md'
warnings: []
---

<intent-contract>

## Intent

**Problem:** Authentication JWT access tokens do not include user organization memberships `(organization_id, role, type)`, preventing `TenantMiddleware` and context switchers from scoping API requests to user tenant organizations. Self-registering parents lack default household organizations.

**Approach:** Update authentication endpoints (`login/email`, `login/pin`, `refresh`, `register/parent`, `register/student`) to automatically resolve or provision organization memberships (`HOUSEHOLD` org for parents/students without an org), including `organizations: [{id, role, type}]` in the JWT access token payload.

## Boundaries & Constraints

**Always:**
- Access token JWT payloads must contain an `organizations` claim formatted as a list of dicts: `[{"id": str(org_id), "role": str(role), "type": str(type)}]`.
- Auto-create a `HOUSEHOLD` organization and `OrganizationMember` row (role `PARENT`) during parent registration (`/register/parent`) or on email login if no membership exists.
- Automatically assign new students (`/register/student`) to their parent's household organization with role `STUDENT`.
- On PIN login (`/login/pin`), resolve student organization memberships (falling back to parent's household org if student membership record is missing) and embed `organizations` claim in token.
- Refresh token flow (`/refresh`) must re-query user organization memberships and embed updated `organizations` claim in the newly issued access token.

**Block If:**
- Database schema changes are requested that violate the `Organization` and `OrganizationMember` models established in Story 1.2.

**Never:**
- Allow JWT access tokens to be issued without valid `organizations` claims for authenticated users.
- Expose password or PIN hashes in responses or logs.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Email Login | `POST /login/email` with valid credentials for parent with 1+ orgs | JWT access token issued containing `organizations: [{id, role, type}]` | HTTP 401 on invalid credentials |
| Parent Self-Registration | `POST /register/parent` with email and password | Creates `User`, auto-creates `HOUSEHOLD` org `"{email}'s Household"`, creates `OrganizationMember` (role PARENT) | HTTP 400 if email exists |
| Student Creation | `POST /register/student` with parent_id and PIN | Creates student `User`, auto-creates `OrganizationMember` (role STUDENT) in parent's household org | HTTP 400 if parent not found |
| PIN Login | `POST /login/pin` with valid PIN code | JWT access token issued containing student `organizations: [{id, role, type}]` | HTTP 401 on invalid PIN |
| Token Refresh | `POST /refresh` with valid refresh token | New JWT access token issued with updated `organizations: [{id, role, type}]` claim | HTTP 401 on invalid/expired token |
| Legacy User Login | Email login for user with 0 org memberships | Auto-creates `HOUSEHOLD` org and membership, returns JWT with newly created org | None |

</intent-contract>

## Code Map

- `backend/app/schemas/user.py` -- Update `TokenPayload` schema to include `organizations: Optional[list[dict]]`.
- `backend/app/api/endpoints/auth.py` -- Implement `get_user_organizations_claims()` helper, update `login_with_email`, `login_with_pin`, `refresh_token`, `register_parent`, and `register_student` endpoints.
- `backend/tests/api/test_auth_organization_claims.py` -- Comprehensive test suite covering JWT org claims, parent registration household auto-creation, student registration, PIN login org claims, and refresh token org claims.

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/schemas/user.py` -- Add `organizations` claim field to `TokenPayload` schema -- Enables Pydantic validation of JWT payload organization claims.
- [x] `backend/app/api/endpoints/auth.py` -- Implement org claims helper and update login, refresh, and registration endpoints -- Ensures JWT tokens carry `{id, role, type}` org claims and household org auto-creation.
- [x] `backend/tests/api/test_auth_organization_claims.py` -- Create test suite verifying JWT organization claims across all auth flows -- Validates multi-tenant JWT claims.

**Acceptance Criteria:**
- Given a parent or expert authenticating via `POST /api/v1/auth/login/email`, when credentials are valid, then the JWT access token contains `organizations: [{id, role, type}]` for all user organizations.
- Given a new parent registering via `POST /api/v1/auth/register/parent`, when registration succeeds, then a `HOUSEHOLD` organization and `OrganizationMember` (role `PARENT`) are created automatically.
- Given a student logging in via `POST /api/v1/auth/login/pin`, when PIN is valid, then the JWT access token contains `organizations: [{id, role, type}]` resolving the student's household or school orgs.
- Given a valid refresh token sent to `POST /api/v1/auth/refresh`, when processed, then the new access token preserves/updates the `organizations` claim list.

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

Helper `get_user_organizations_claims(user, db)` queries `OrganizationMember` with `selectinload(OrganizationMember.organization)` for `user.id` using `execution_options(skip_tenant_filter=True)` so auth requests without active tenant header can inspect memberships. If no memberships exist:
- For `PARENT`: creates `Organization(name=f"{user.email}'s Household", type=OrganizationType.HOUSEHOLD)` and `OrganizationMember(user_id=user.id, organization_id=household.id, role=UserRole.PARENT)`.
- For `STUDENT`: looks up parent's household org (creating one for parent if needed) and adds `OrganizationMember(user_id=user.id, organization_id=parent_org.id, role=UserRole.STUDENT)`.

## Verification

**Commands:**
- `& ".venv/Scripts/python.exe" -m pytest tests/api/test_auth_organization_claims.py tests/core/test_tenant_middleware.py` -- expected: 9 passed in 2.09s

## Auto Run Result

- **Status**: `done`
- **Summary**: Implemented organization membership claims in JWT access tokens across all authentication endpoints (`login/email`, `login/pin`, `refresh`), automatic household organization creation upon parent registration (`register/parent`), and automatic student membership assignment to parent household org upon student creation (`register/student`).
- **Files Modified**:
  - `backend/app/schemas/user.py`: Added `organizations: Optional[list[dict]] = None` field to `TokenPayload`.
  - `backend/app/api/endpoints/auth.py`: Implemented `get_user_organizations_claims()` helper function and updated `login_with_email`, `login_with_pin`, `refresh_token`, `register_parent`, and `register_student` endpoints.
  - `backend/tests/api/test_auth_organization_claims.py`: Created comprehensive test suite verifying organization claims across registration, login, PIN authentication, token refresh, and legacy user fallback.
- **Review Findings**: 0 intent gaps, 0 bad spec, 0 patches, 0 deferred, 0 rejected.
- **Follow-up Review Recommended**: `false`
- **Verification**: Executed `pytest tests/api/test_auth_organization_claims.py tests/core/test_tenant_middleware.py` with 9 passed (100% pass rate).
