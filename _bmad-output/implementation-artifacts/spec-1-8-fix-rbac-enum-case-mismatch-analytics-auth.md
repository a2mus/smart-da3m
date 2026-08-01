---
title: 'Story 1.8: Fix RBAC Enum Case Mismatch & Analytics Auth'
type: 'bugfix'
created: '2026-08-01T02:00:00Z'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-1-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** The `require_expert` dependency in `backend/app/core/security.py` checks `user.role.value not in ("expert", "admin")` using lowercase strings, whereas `UserRole` enum values are defined in uppercase (`"EXPERT"`, `"PARENT"`, `"STUDENT"`). Additionally, `require_expert` does not use FastAPI `Depends(get_current_user)` to extract authentication context, causing legitimate expert requests to fail with HTTP 403 Forbidden.

**Approach:** Update `require_expert` in `backend/app/core/security.py` to accept `current_user: User = Depends(get_current_user)` and compare `current_user.role` against `UserRole.EXPERT`. Audit all backend role checks for consistent uppercase enum usage and write automated API tests covering expert vs. student access to analytics endpoints.

## Boundaries & Constraints

**Always:** Role checks must compare against `UserRole` enum members (`UserRole.EXPERT`, `UserRole.PARENT`, `UserRole.STUDENT`) or exact enum string values (`"EXPERT"`, etc.). `require_expert` must be a FastAPI-compatible dependency using `Depends(get_current_user)`.

**Block If:** Schema or database model enum values require structural database migrations (out of scope).

**Never:** Use lowercase role strings (`"expert"`, `"student"`, `"parent"`) for role comparison logic.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Expert Access | JWT with `role: EXPERT` calls `/api/v1/analytics/metrics` | 200 OK with analytics data | No error |
| Student Access Blocked | JWT with `role: STUDENT` calls `/api/v1/analytics/metrics` | 403 Forbidden | HTTP 403 detail="Insufficient permissions. Expert access required." |
| Unauthenticated Access | No Bearer header or invalid JWT | 401 Unauthorized | HTTP 401 detail="Invalid or expired token" |

</intent-contract>

## Code Map

- `backend/app/core/security.py` -- Contains `require_expert` function with lowercase string comparison bug and missing `Depends(get_current_user)`.
- `backend/app/api/deps.py` -- Contains `get_current_expert` and role dependencies using `UserRole.EXPERT`.
- `backend/app/api/endpoints/analytics.py` -- Analytics endpoints requiring expert role.
- `backend/tests/api/test_rbac_analytics.py` -- Unit and integration tests for RBAC role check and analytics endpoints.

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/core/security.py` -- Fix `require_expert` dependency to accept `current_user: User = Depends(get_current_user)` and check `current_user.role != UserRole.EXPERT`.
- [x] `backend/app/api/deps.py` -- Verify and alias `require_expert` to `get_current_expert` for backwards compatibility.
- [x] `backend/tests/api/test_rbac_analytics.py` -- Add tests verifying expert tokens return 200 and student/parent tokens return 403 on analytics routes.

**Acceptance Criteria:**
- Given `require_expert` in `core/security.py`, when an expert user calls an endpoint protected by it, then the role check compares against `UserRole.EXPERT` and returns 200.
- Given a student user token, when accessing analytics endpoints, then HTTP 403 Forbidden is returned.
- Given all backend role checks, when audited, then no lowercase role string comparisons remain.

## Verification

**Commands:**
- `pytest backend/tests/api/test_rbac_analytics.py` -- expected: Tests pass with 0 failures
- `pytest backend/tests/` -- expected: Full test suite passes

## Auto Run Result

Status: done

Summary: Fixed the RBAC enum case mismatch bug in `backend/app/core/security.py` where `require_expert` checked for lowercase `"expert"` instead of uppercase `UserRole.EXPERT.value` / `"EXPERT"`. Audited all backend role checks, created automated tests in `backend/tests/api/test_rbac_analytics.py`, and updated sprint tracking status to `done`.
