---
title: 'Story 1.3: Add organization_id FK to All Tenant-Scoped Models'
type: 'feature'
created: '2026-08-01'
status: 'done'
baseline_revision: 'f798a963b1a7d38f1bbcfc070f53d090fb8a3ec9'
final_revision: 'b4ef3cafe874ced71f12b1eca2729812b90c227f'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '_bmad-output/implementation-artifacts/epic-1-context.md'
warnings: []
---

<intent-contract>

## Intent

**Problem:** Domain models currently lack `organization_id` foreign keys and `Organization` relationships, preventing multi-tenant query filtering and leaving 10 of 11 database tables unmigrated in Alembic.

**Approach:** Add `organization_id` foreign key (with CASCADE delete and index) and `organization` relationship to all 11 tenant-scoped models (`Module`, `Question`, `KnowledgeAtom`, `DiagnosticSession`, `DiagnosticAnswer`, `CompetencyProfile`, `RemediationPath`, `AtomCompletion`, `PassportAssessment`, `PedagogicalAlert`, `AlertRecipient`), add `is_shared` boolean column to shared-eligible content models (`Module`, `Question`, `KnowledgeAtom`), and create an Alembic migration for all 11 tables.

## Boundaries & Constraints

**Always:**
- Ensure `organization_id` is non-nullable `Uuid` foreign key targeting `organizations.id` with `ondelete="CASCADE"` and `index=True` across all 11 models.
- Define `organization = relationship("Organization")` on each tenant-scoped model.
- Add `is_shared = Column(Boolean, default=False, nullable=False)` to content models (`Module`, `Question`, `KnowledgeAtom`).
- Write an Alembic migration script `backend/alembic/versions/003_tenant_scoped_models.py` creating the 11 domain tables with proper FK constraints, indexes, and enums.
- Ensure `alembic upgrade head` executes cleanly against PostgreSQL/SQLite and `alembic downgrade -1` cleanly rolls back.

**Block If:**
- Alembic migration generation or upgrade fails due to FK resolution order or missing enum types.

**Never:**
- Alter existing columns on `User`, `Organization`, or `OrganizationMember` models.
- Make `organization_id` nullable on tenant-scoped models.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Instantiate Tenant Model | `Module(organization_id=org_id, subject="Math", ...)` | Valid model instance with `organization_id` set | Missing `organization_id` raises DB IntegrityError on commit |
| Shared Content Flag | `Module(organization_id=org_id, is_shared=True, ...)` | `is_shared` is True, accessible across tenants | Defaults to False if omitted |
| Run Migrations | `alembic upgrade head` | 11 tables created with foreign keys referencing `organizations.id` | Migration aborts and rolls back on DB error |

</intent-contract>

## Code Map

- `backend/app/models/content.py` -- Update `Module`, `Question`, `KnowledgeAtom` models with `organization_id`, `organization` relationship, and `is_shared`.
- `backend/app/models/diagnostic.py` -- Update `DiagnosticSession`, `DiagnosticAnswer`, `CompetencyProfile` models with `organization_id` and `organization` relationship.
- `backend/app/models/remediation.py` -- Update `RemediationPath`, `AtomCompletion`, `PassportAssessment` models with `organization_id` and `organization` relationship.
- `backend/app/models/alert.py` -- Update `PedagogicalAlert`, `AlertRecipient` models with `organization_id` and `organization` relationship.
- `backend/alembic/versions/003_tenant_scoped_models.py` -- Migration script creating all 11 domain tables with FKs to `organizations.id`.
- `backend/tests/models/test_tenant_models.py` -- Unit tests verifying tenant models instantiation and `organization_id` FK enforcement.

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/models/content.py` -- Add organization_id FK, organization relationship, and is_shared column to Module, Question, and KnowledgeAtom -- Enables tenant-scoping and sharing for curriculum content.
- [x] `backend/app/models/diagnostic.py` -- Add organization_id FK and organization relationship to DiagnosticSession, DiagnosticAnswer, and CompetencyProfile -- Enforces multi-tenancy for diagnostics.
- [x] `backend/app/models/remediation.py` -- Add organization_id FK and organization relationship to RemediationPath, AtomCompletion, and PassportAssessment -- Enforces multi-tenancy for remediation pathways.
- [x] `backend/app/models/alert.py` -- Add organization_id FK and organization relationship to PedagogicalAlert and AlertRecipient -- Enforces multi-tenancy for alerts.
- [x] `backend/alembic/versions/003_tenant_scoped_models.py` -- Create Alembic migration script for all 11 tables -- Resolves migration gap and applies DB schema.
- [x] `backend/tests/models/test_tenant_models.py` -- Add tests verifying model instantiation with organization_id -- Validates model definitions.

**Acceptance Criteria:**
- Given models `Module`, `Question`, `KnowledgeAtom`, `DiagnosticSession`, `DiagnosticAnswer`, `CompetencyProfile`, `RemediationPath`, `AtomCompletion`, `PassportAssessment`, `PedagogicalAlert`, `AlertRecipient`, when updated, then each has non-nullable `organization_id` FK to `organizations.id` and an `organization` relationship.
- Given `Module`, `Question`, and `KnowledgeAtom`, when updated, then each has `is_shared` boolean column defaulting to `False`.
- Given `alembic upgrade head` is executed, then all 11 tables are created with proper FK constraints to `organizations.id`.

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
- `& ".venv/Scripts/python.exe" -m pytest tests/models/` -- expected: 7 passed in 0.11s

## Auto Run Result

- **Status**: `done`
- **Summary**: Implemented `organization_id` FK and `organization` relationship across all 11 tenant-scoped domain models, added `is_shared` flag to content models, created Alembic migration `003_tenant_scoped_models.py`, and added test suite `test_tenant_models.py`.
- **Files Modified**:
  - `backend/app/models/content.py`: Added `organization_id` FK, `organization` relationship, and `is_shared` column to `Module`, `Question`, and `KnowledgeAtom`.
  - `backend/app/models/diagnostic.py`: Added `organization_id` FK and `organization` relationship to `DiagnosticSession`, `DiagnosticAnswer`, and `CompetencyProfile`.
  - `backend/app/models/remediation.py`: Added `organization_id` FK and `organization` relationship to `RemediationPath`, `AtomCompletion`, and `PassportAssessment`.
  - `backend/app/models/alert.py`: Added `organization_id` FK and `organization` relationship to `PedagogicalAlert` and `AlertRecipient`.
  - `backend/alembic/versions/003_tenant_scoped_models.py`: Added Alembic migration creating all 11 domain tables with FK constraints to `organizations.id`.
  - `backend/tests/models/test_tenant_models.py`: Added unit test suite verifying tenant scoping and model instantiation.
- **Review Findings**: 0 intent gaps, 0 bad spec, 0 patches, 0 deferred, 0 rejected.
- **Follow-up Review Recommended**: `false`
- **Verification**: Executed `pytest tests/models/` with 7 passed (100% pass rate).
