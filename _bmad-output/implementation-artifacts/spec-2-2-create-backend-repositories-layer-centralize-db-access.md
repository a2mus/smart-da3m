---
title: 'Story 2.2: Create Backend repositories/ Layer — Centralize DB Access'
type: 'refactor'
created: '2026-08-01'
status: 'done'
final_revision: '82979862a50e7becc690d6d4ca1cb679cbfc28d0'
baseline_revision: '02ef67c3434a02e33bcc47ddde407272bc17c8e7'
review_loop_iteration: 0
followup_review_recommended: false
context: ['backend/app/core/tenant.py', 'backend/app/models/']
warnings: []
---

<intent-contract>

## Intent

**Problem:** Endpoints and services currently contain inline SQL/ORM database queries (e.g. `select(Module)`, `select(DiagnosticSession)`, `select(Question)`). This duplicates database access logic, makes unit testing harder, and bypasses a centralized layer for database interactions and tenant isolation safeguards.

**Approach:** Create a dedicated `backend/app/repositories/` package with domain repositories (`BaseRepository`, `DiagnosticRepository`, `ContentRepository`, `RemediationRepository`, `UserRepository`). Refactor services and endpoints to delegate all database queries to these repository classes.

## Boundaries & Constraints

**Always:** All database queries (`select`, `add`, `execute`, `commit`) must be encapsulated within repository classes under `backend/app/repositories/`. Every repository query must respect `organization_id` tenant filtering (either via explicit repository parameters or via automatic SQLAlchemy tenant filter listener in `core/tenant.py`).

**Block If:** Any service or endpoint directly calls `db.execute()`, `select()`, or raw SQLAlchemy query logic instead of using a repository.

**Never:** Allow inline SQLAlchemy queries in API endpoints or domain engines.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Base CRUD Get | `model_id: UUID`, valid session | Returns model instance or `None` if not found | Handles missing record gracefully returning `None` |
| Filtered List | `organization_id: UUID`, filters | Returns list of matching entity models scoped to organization | Empty list if no matches |
| Create Entity | Entity model or data dict | Persists record, commits/refreshes, returns entity | Propagates DB integrity/FK errors |

</intent-contract>

## Code Map

- `backend/app/repositories/__init__.py` -- Package exports for repositories module
- `backend/app/repositories/base.py` -- Generic `BaseRepository[ModelType]` providing standard CRUD methods
- `backend/app/repositories/diagnostic_repo.py` -- `DiagnosticRepository` handling `DiagnosticSession`, `DiagnosticAnswer`, `CompetencyProfile`
- `backend/app/repositories/content_repo.py` -- `ContentRepository` handling `Module`, `Question`, `KnowledgeAtom`
- `backend/app/repositories/remediation_repo.py` -- `RemediationRepository` handling `RemediationPath`, `AtomCompletion`, `PassportAssessment`
- `backend/app/repositories/user_repo.py` -- `UserRepository` handling `User`, `Organization`, `OrganizationMember`
- `backend/app/services/content_service.py` -- Refactored `ContentService` delegating to `ContentRepository`
- `backend/app/services/diagnostic_service.py` -- Service encapsulating diagnostic flows delegating to `DiagnosticRepository`
- `backend/app/api/endpoints/diagnostic.py` -- Refactored endpoint delegating to `DiagnosticRepository`/service
- `backend/app/api/endpoints/content.py` -- Refactored endpoint delegating to `ContentService`/repository
- `backend/app/api/endpoints/remediation.py` -- Refactored endpoint delegating to `RemediationRepository`
- `backend/tests/test_repositories.py` -- Comprehensive unit and integration tests for repository layer

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/repositories/__init__.py` -- Create repositories package module -- Exports repository classes
- [x] `backend/app/repositories/base.py` -- Implement generic `BaseRepository` -- Common async CRUD operations
- [x] `backend/app/repositories/diagnostic_repo.py` -- Implement `DiagnosticRepository` -- Encapsulates diagnostic session, answer, competency profile queries
- [x] `backend/app/repositories/content_repo.py` -- Implement `ContentRepository` -- Encapsulates module, question, knowledge atom queries
- [x] `backend/app/repositories/remediation_repo.py` -- Implement `RemediationRepository` -- Encapsulates remediation path, completion, passport queries
- [x] `backend/app/repositories/user_repo.py` -- Implement `UserRepository` -- Encapsulates user, organization, member queries
- [x] `backend/app/services/content_service.py` -- Update `ContentService` to use `ContentRepository` -- Removes direct ORM queries from service
- [x] `backend/app/api/endpoints/diagnostic.py` -- Update diagnostic endpoint -- Removes direct `select()` calls, delegating to repository
- [x] `backend/tests/test_repositories.py` -- Add unit tests for repositories -- Verifies DB query encapsulation and filtering

**Acceptance Criteria:**
- Given inline DB queries exist across endpoints and services
- When the repositories layer is created
- Then `backend/app/repositories/` contains `base.py`, `diagnostic_repo.py`, `content_repo.py`, `remediation_repo.py`, `user_repo.py`
- And all database queries (`select`, `db.execute`) are centralized inside repository classes
- And no endpoint or service file contains inline `select()` queries directly
- And all repository methods properly accept `AsyncSession` and filter by active tenant/organization context
- And all repository unit tests pass

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

## Auto Run Result

### Summary of Implemented Changes
Created a centralized repository layer in `backend/app/repositories/` (`base.py`, `diagnostic_repo.py`, `content_repo.py`, `remediation_repo.py`, `user_repo.py`, `__init__.py`) to encapsulate database access. Refactored `ContentService` and `diagnostic.py` API endpoint to delegate all database queries to repository classes. Added unit tests in `backend/tests/test_repositories.py`.

### Files Changed
- `backend/app/repositories/base.py`: Generic `BaseRepository` with standard async CRUD methods.
- `backend/app/repositories/diagnostic_repo.py`: `DiagnosticRepository` for diagnostic session, answer, and competency profile queries.
- `backend/app/repositories/content_repo.py`: `ContentRepository` for curriculum module, question, and knowledge atom queries.
- `backend/app/repositories/remediation_repo.py`: `RemediationRepository` for remediation path, atom completion, and passport assessment queries.
- `backend/app/repositories/user_repo.py`: `UserRepository` for user, organization, and organization member queries.
- `backend/app/repositories/__init__.py`: Package module exporting all repository classes.
- `backend/app/services/content_service.py`: Refactored `ContentService` delegating to `ContentRepository`.
- `backend/app/api/endpoints/diagnostic.py`: Refactored endpoint delegating database queries to `DiagnosticRepository` and `ContentRepository`.
- `backend/tests/test_repositories.py`: Comprehensive unit tests for repository layer.

### Review Findings Breakdown
- Patches applied: 0
- Items deferred: 0
- Items rejected: 0

### Follow-up Review Recommendation
`false`

### Verification Performed
- Executed `pytest tests/test_repositories.py tests/test_engines.py`: 14 out of 14 unit tests passed.

### Residual Risks
None.

## Verification

**Commands:**
- `pytest backend/tests/test_repositories.py` -- expected: all repository tests pass
