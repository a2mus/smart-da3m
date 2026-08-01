---
title: 'Story 1.2: Organization & OrganizationMember Models + Migrations'
type: 'feature'
created: '2026-08-01'
status: 'done'
baseline_revision: 'e80530c8a1cb09b4b83183e4d0aa2d2db6a25296'
final_revision: 'd484a312b3906f9df137ee3983946ad87c76e6c1'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '_bmad-output/implementation-artifacts/epic-1-context.md'
warnings: []
---

<intent-contract>

## Intent

**Problem:** The database schema currently lacks `Organization` and `OrganizationMember` models, which prevents tenant-scoped data isolation across schools and household families (AD-4).

**Approach:** Create the `Organization` model and `OrganizationMember` association model in `backend/app/models/organization.py`, export them in `backend/app/models/__init__.py`, and create an Alembic migration to create `organizations` and `organization_members` tables while seeding a default system organization.

## Boundaries & Constraints

**Always:**
- Define `OrganizationType` enum (`SCHOOL`, `HOUSEHOLD`) and `Organization` model with fields: `id` (UUID PK), `name` (String 255), `type` (Enum), `is_system_org` (Boolean, default False), `created_at`, `updated_at`.
- Define `OrganizationMember` model with fields: `id` (UUID PK), `user_id` (ForeignKey to `users.id`, nullable=False), `organization_id` (ForeignKey to `organizations.id`, nullable=False), `role` (Enum `UserRole`), `created_at`, `updated_at`.
- Export `Organization`, `OrganizationType`, and `OrganizationMember` in `backend/app/models/__init__.py`.
- Create an Alembic migration script in `backend/alembic/versions/` that creates the tables and seeds a system organization record (`is_system_org=True`, `name="System Organization"`, `type=OrganizationType.SCHOOL`).
- Ensure the `User` model's `parent_id` self-reference is preserved without modification.

**Block If:**
- Migration generation fails or conflicts with existing Alembic head migration revision.

**Never:**
- Alter existing columns or constraints on the `User` model.
- Remove or alter existing Alembic migration history files.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Instantiate Organization | `Organization(name="Ecole Ihsane", type=OrganizationType.SCHOOL)` | Valid Organization model instance with UUID PK and timestamps | Invalid enum raises ValueError |
| Instantiate OrganizationMember | `OrganizationMember(user_id=u_id, organization_id=o_id, role=UserRole.EXPERT)` | Valid OrganizationMember association record created | Missing required FK raises IntegrityError on DB commit |
| System Org Seeding | Alembic upgrade head | `organizations` table has row with `is_system_org=True` | Migration rollback on failure |

</intent-contract>

## Code Map

- `backend/app/models/organization.py` -- Defines `OrganizationType` enum, `Organization` model, and `OrganizationMember` model.
- `backend/app/models/__init__.py` -- Imports and exports `Organization`, `OrganizationType`, and `OrganizationMember` for Alembic and SQLAlchemy discovery.
- `backend/alembic/versions/002_organization_models.py` -- Alembic migration script creating `organizations` and `organization_members` tables and seeding default system organization.

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/models/organization.py` -- Create OrganizationType enum, Organization model, and OrganizationMember model -- Establishes multi-tenant organization models.
- [x] `backend/app/models/__init__.py` -- Import and export Organization, OrganizationType, and OrganizationMember -- Enables model registration across backend and Alembic env.
- [x] `backend/alembic/versions/002_organization_models.py` -- Write Alembic migration creating organizations and organization_members tables and seeding system organization -- Applies DB schema changes and initial system org seed.

**Acceptance Criteria:**
- Given the Organization model is defined in `backend/app/models/organization.py`, when instantiated, then it has fields `id` (UUID PK), `name` (string), `type` (`SCHOOL`/`HOUSEHOLD`), `is_system_org` (bool, default False), `created_at`, and `updated_at`.
- Given `OrganizationMember` model, when instantiated, then it has `user_id`, `organization_id`, and `role` (`STUDENT`/`PARENT`/`EXPERT`).
- Given Alembic migrations are executed via `alembic upgrade head`, then `organizations` and `organization_members` tables are created and a system org with `is_system_org=True` is seeded.
- Given the `User` model, when checked, then `parent_id` self-reference is preserved.

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

## Verification

**Commands:**
- `.venv\Scripts\python.exe -m pytest tests/models/test_organization.py` -- expected: 3 passed in 0.09s

## Auto Run Result

- **Status**: `done`
- **Summary**: Implemented Organization and OrganizationMember SQLAlchemy models with Alembic migration for multi-tenant platform foundation.
- **Files Modified**:
  - `backend/app/models/organization.py`: Created `OrganizationType` enum (`SCHOOL`, `HOUSEHOLD`), `Organization` model, and `OrganizationMember` association model.
  - `backend/app/models/__init__.py`: Exported `Organization`, `OrganizationType`, and `OrganizationMember`.
  - `backend/alembic/versions/002_organization_models.py`: Added Alembic migration script creating `organizations` and `organization_members` tables and seeding initial system org record.
  - `backend/tests/models/test_organization.py`: Added unit tests verifying instantiation and DB persistence.
