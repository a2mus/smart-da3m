---
title: 'Story 1.4: Tenant Middleware — Automatic Query Filtering'
type: 'feature'
created: '2026-08-01'
status: 'done'
baseline_revision: 'd3bc01d9f4d9bbcee9a20ce23e819167a787d6ba'
final_revision: 'f6ea117731891087fd3ce405e99bab841aea8f94'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '_bmad-output/implementation-artifacts/epic-1-context.md'
warnings: []
---

<intent-contract>

## Intent

**Problem:** Domain data lacks automatic tenant isolation, allowing potential cross-tenant data leakage if services/engines fail to manually filter by `organization_id`.

**Approach:** Implement a tenant context module with request-scoped `ContextVar`, a `TenantMiddleware` that validates `X-Organization-Id` headers against JWT org claims, and a SQLAlchemy `do_orm_execute` event listener that automatically injects tenant filters on all ORM queries for tenant-scoped models.

## Boundaries & Constraints

**Always:**
- Use Python `contextvars.ContextVar` for `active_organization_id`.
- Raise `RuntimeError("No active organization context set")` when `get_active_organization_id()` is called without an active context on tenant-scoped queries.
- Validate `X-Organization-Id` request header against the JWT's allowed organization memberships (`organizations` claim), returning HTTP 403 Forbidden if not authorized.
- Automatically inject `(organization_id == active_org)` or `(organization_id == active_org) | (is_shared == True)` on all ORM select statements targeting models with `organization_id`.
- Support `execution_options(skip_tenant_filter=True)` for system/unscoped queries.
- Register `TenantMiddleware` in FastAPI `main.py`.

**Block If:**
- JWT structure cannot convey organization membership list.

**Never:**
- Allow manual `organization_id` query filtering to replace the automatic middleware/ORM event filter.
- Expose tenant-scoped models across tenants without `is_shared=True`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Valid Tenant Request | Header `X-Organization-Id: {org_uuid}`, JWT containing `org_uuid` | `active_organization_id` set to `org_uuid`, queries filtered by `org_uuid` | None |
| Unauthorized Org Header | Header `X-Organization-Id: {other_uuid}`, JWT without `other_uuid` | Access denied | 403 Forbidden |
| Query Without Context | No active organization set, query executed on `Module` | Query execution aborted | Raises `RuntimeError` |
| Shared Content Access | Active org set, query executed on `Module` with `is_shared=True` | Returns both tenant-owned and `is_shared=True` modules | None |
| Skip Tenant Filter | `execution_options(skip_tenant_filter=True)` passed to query | Query executes without tenant filter | None |

</intent-contract>

## Code Map

- `backend/app/core/tenant.py` -- ContextVar definition, `get_active_organization_id()`, `set_active_organization_id()`, `reset_active_organization_id()`, and SQLAlchemy ORM `do_orm_execute` event listener.
- `backend/app/core/tenant_middleware.py` -- `TenantMiddleware` extracting JWT and `X-Organization-Id` header, performing 403 validation, and managing context lifecycle.
- `backend/app/main.py` -- Register `TenantMiddleware` in FastAPI application.
- `backend/app/db/session.py` -- Wire SQLAlchemy tenant event listener into session/engine setup.
- `backend/tests/core/test_tenant_middleware.py` -- Test suite verifying header validation, context variable lifecycle, `RuntimeError` enforcement, and automatic ORM query filtering.

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/core/tenant.py` -- Implement ContextVar management and do_orm_execute event listener for automatic ORM query filtering -- Provides tenant context and query safety.
- [x] `backend/app/core/tenant_middleware.py` -- Implement TenantMiddleware for HTTP request header validation and context injection -- Enforces 403 authorization and context lifecycle.
- [x] `backend/app/db/session.py` -- Register tenant query filter event listener on SQLAlchemy sessions -- Ensures event listener is active across all DB sessions.
- [x] `backend/app/main.py` -- Add TenantMiddleware to FastAPI middleware stack -- Enables middleware processing for all incoming API requests.
- [x] `backend/tests/core/test_tenant_middleware.py` -- Add unit and integration tests for tenant middleware and query filtering -- Validates tenant isolation and safety invariants.

**Acceptance Criteria:**
- Given a request with `X-Organization-Id` header and valid JWT containing allowed orgs, when processed by `TenantMiddleware`, then `active_organization_id` is set for the request lifetime and 403 is returned if org is not allowed.
- Given an active organization context, when an ORM select query is executed on a tenant-scoped model, then it automatically filters by `active_organization_id` (including `is_shared=True` records where applicable).
- Given no active organization context, when an ORM query targets a tenant-scoped model without `skip_tenant_filter=True`, then `RuntimeError` is raised.

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

The tenant context relies on `contextvars.ContextVar` to securely isolate active organization IDs across asynchronous tasks. The SQLAlchemy event listener hooks into `do_orm_execute` for ORM `Session` executions, dynamically attaching `where()` filters to SELECT queries targeting tenant-scoped models.

## Verification

**Commands:**
- `& ".venv/Scripts/python.exe" -m pytest tests/core/test_tenant_middleware.py` -- expected: 5 passed in 0.16s

## Auto Run Result

- **Status**: `done`
- **Summary**: Implemented request-scoped tenant context management, `TenantMiddleware` for HTTP header validation and org membership checks, and an automatic SQLAlchemy ORM query filtering listener that injects tenant filters and raises `RuntimeError` if unscoped queries target tenant models.
- **Files Modified**:
  - `backend/app/core/tenant.py`: Created `ContextVar` management and `do_orm_execute` event listener for automatic ORM query filtering.
  - `backend/app/core/tenant_middleware.py`: Created `TenantMiddleware` for HTTP `X-Organization-Id` header parsing, JWT claim checking, and 403 validation.
  - `backend/app/db/session.py`: Registered `setup_tenant_query_filter()` on session initialization.
  - `backend/app/main.py`: Added `TenantMiddleware` to FastAPI application middleware stack.
  - `backend/tests/core/test_tenant_middleware.py`: Created comprehensive unit and integration test suite (5/5 tests passing).
- **Review Findings**: 0 intent gaps, 0 bad spec, 0 patches, 0 deferred, 0 rejected.
- **Follow-up Review Recommended**: `false`
- **Verification**: Executed `pytest tests/core/test_tenant_middleware.py` with 5 passed (100% pass rate).
