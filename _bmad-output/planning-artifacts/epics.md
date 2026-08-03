---
title: Ihsane Platform — Epics & Stories
project: Ihsane Platform
created: 2026-07-15
updated: 2026-07-15
status: draft
stepsCompleted: []
sources:
  - prds/prd-moody-bird-2026-07-09/prd.md
  - architecture/ARCHITECTURE-SPINE.md
  - specs/spec-ihsane-platform/SPEC.md
  - specs/spec-ihsane-platform/functional-requirements.md
---

# Epics & Stories — Ihsane Platform

## Overview

**Project:** Ihsane Platform — Adaptive learning platform for Algerian primary education.

**Context:** This is a brownfield refactoring effort. The MVP was built via SpecKit (11 feature branches merged), but an implementation audit against the ratified Architecture Spine (AD-1 through AD-7, status: **final**) revealed that 5 of 7 architecture decisions are violated by the current codebase. This document organizes all remediation and feature-completion work into user-value-focused epics with a hybrid structure: structural foundation epics first, then domain-loop epics on top.

**Epic Strategy:** Hybrid — structural foundation epics (Wave 1) establish the architecture integrity required for all subsequent work. Core loop epics (Wave 2) deliver the functional pilot loop end-to-end. Feature completion epics (Wave 3) close remaining gaps.

**Critical Path (functional pilot loop):** Epic 1 → Epic 2 → Epic 3 → Epic 6.

## Requirements Inventory

### Functional Requirements (30 FRs)

| FR | Description | Status |
|----|-------------|--------|
| FR-1 | Student PIN login | Built — needs multi-tenant org context |
| FR-2 | Parent/Expert email-password login | Built — needs multi-tenant org context |
| FR-3 | Token refresh & session expiry | Built |
| FR-4 | Role-based access control | Built — broken for analytics endpoint (enum case mismatch) |
| FR-5 | Manage modules | Built — endpoints fat, no repository layer |
| FR-6 | Manage question-bank items | Built — endpoints fat |
| FR-7 | Manage knowledge atoms | Built — endpoints fat |
| FR-8 | Bulk import content | Built — per-row validation needs verification |
| FR-8a | AI-assisted content drafting | **NOT BUILT** — pilot-blocking |
| FR-8b | Audio read-aloud of question text | **NOT BUILT** — pilot-blocking |
| FR-8c | Image-choice item type | **NOT BUILT** — pilot-blocking |
| FR-9 | Start/resume diagnostic session | Built — bypasses engine |
| FR-10 | Adaptive question selection (BKT) | Built in engine, **bypassed by endpoint** (hardcoded mastery=0.5) |
| FR-11 | Dynamic difficulty adjustment | Built in engine, **bypassed by endpoint** |
| FR-12 | Error classification | Built in engine, **bypassed by endpoint** |
| FR-13 | Capture response time | Built |
| FR-14 | Generate remediation pathway | Partial — no AI proposal, no expert validation |
| FR-15 | Deliver knowledge atoms (concrete→abstract) | Partial — pathway exists but state machine wrong |
| FR-16 | Spaced re-surfacing of errors | **NOT IMPLEMENTED** (OQ-10 resolved: confirmed absent) |
| FR-17 | Track mastery level per competency | Partial — BKT exists but bypassed; hardcoded values |
| FR-18 | Passport competency task | Built — component orphaned, not wired |
| FR-19 | Award competency badge | Built — needs state machine integration |
| FR-20 | Subject-strength radar | Mock — dashboardService returns hardcoded data |
| FR-21 | Smart insight messages (non-numeric) | Mock |
| FR-22 | Daily reinforcement recommendation | Mock |
| FR-23 | Competency heatmap | Mock — analyticsService returns hardcoded data |
| FR-24 | Auto-grouping into remediation groups | Built in engine, partially bypassed |
| FR-25 | Export reports (PDF/CSV) | Built (report_exporter) — **orphaned, never wired** |
| FR-26 | Printable remediation cards | **NOT BUILT** |
| FR-27 | Generate pedagogical alerts | Built (AlertManager) — **orphaned, never called in production** |
| FR-28 | Instant AR/FR language switch | Core works — hardcoded strings leak, missing keys |
| FR-29 | Local content cache | Dexie schema exists — caching never invoked |
| FR-30 | Background sync of analytics | **NOT FUNCTIONAL** — sync queue dead code |

### Non-Functional Requirements

| NFR | Description | Status |
|-----|-------------|--------|
| NFR-PERF | < 3s FCP on 3G, < 200ms API P95, < 200KB bundle | Unverified (OQ-8) |
| NFR-SEC | JWT auth, bcrypt, RBAC, rate limiting, CORS, CSP | Partial — RBAC broken for analytics, no rate limiting |
| NFR-RELIABILITY | Health check, pilot-level availability | Health check exists |
| NFR-OBSERVABILITY | Structured JSON logging with org_id, user_id, request_id | **Missing** — no structured logging |
| NFR-A11Y | WCAG 2.1 AA, 0 violations | Audited (6 routes), needs re-verification after changes |
| NFR-I18N | AR (RTL primary) / FR (LTR), logical CSS only | Partial — hardcoded strings |
| NFR-MIGRATION | Alembic migrations for all 11 tables | **Critical gap** — only 1/11 tables migrated |

### Architecture Decision Gaps

| AD | Description | Audit Verdict |
|----|-------------|---------------|
| AD-1 | DB source of truth, stateless engines | **FAIL** — engines hold in-memory dicts |
| AD-2 | Remediation state machine (7 states) | **FAIL** — only 3 states, missing DIAGNOSED/PROPOSED/VALIDATED |
| AD-3 | Hybrid AI (Celery + LiteLLM + expert gate) | **COMPLETE FAIL** — no tasks, no LiteLLM, no AI |
| AD-4 | Multi-tenant (Schools + Households) | **COMPLETE FAIL** — no models, no middleware |
| AD-5 | SSE via Redis Pub/Sub | **FAIL** — no sse-starlette, no endpoint |
| AD-6 | Offline-first (Dexie write-behind) | **PARTIAL** — schema only, no write-behind, no sync |
| AD-7 | Core domain loop | **PARTIAL** — PROPOSE/VALIDATE missing, alerts orphaned |

## FR Coverage Map

```
FR-1:  Epic 1 (multi-tenant org context on PIN login)
FR-2:  Epic 1 (multi-tenant org context on email login)
FR-3:  Epic 1 (JWT carries org pairs)
FR-4:  Epic 1 (RBAC + tenant-aware role checks)
FR-5:  Epic 6 (expert module CRUD)
FR-6:  Epic 6 (expert question-bank CRUD)
FR-7:  Epic 6 (expert knowledge-atom CRUD)
FR-8:  Epic 6 (bulk import with per-row validation)
FR-8a: Epic 6 (AI-assisted content drafting)
FR-8b: Epic 7 (audio read-aloud)
FR-8c: Epic 7 (image-choice item type)
FR-9:  Epic 2 (diagnostic session start/resume — engine-backed)
FR-10: Epic 2 (adaptive BKT question selection)
FR-11: Epic 2 (dynamic difficulty adjustment)
FR-12: Epic 2 (error classification)
FR-13: Epic 2 (response time capture)
FR-14: Epic 3 (remediation pathway generation — AI + expert)
FR-15: Epic 3 (atom delivery, concrete→abstract)
FR-16: Epic 3 (spaced re-surfacing — new build)
FR-17: Epic 3 (4-level mastery tracking)
FR-18: Epic 3 (Passport competency task — wire orphaned component)
FR-19: Epic 3 (badge awarding + state machine integration)
FR-20: Epic 8 (subject-strength radar — real data)
FR-21: Epic 8 (smart insight messages)
FR-22: Epic 8 (daily reinforcement recommendation)
FR-23: Epic 9 (competency heatmap — real data)
FR-24: Epic 9 (auto-grouping)
FR-25: Epic 9 (report export — wire orphaned exporter)
FR-26: Epic 9 (printable remediation cards)
FR-27: Epic 4 (pedagogical alerts — wire orphaned AlertManager + SSE push)
FR-28: Epic 10 (bilingual completeness)
FR-29: Epic 5 (local content cache — make functional)
FR-30: Epic 5 (background sync — make functional)
```

## Epic List

### Wave 1 — Structural Foundations

#### Epic 1: Multi-Tenant Platform Foundation
The platform can safely host multiple school organizations and independent household families on the same deployment, with complete data isolation. An independent parent can self-register, get an auto-created household org, create child accounts, and select a curriculum level. Every query is automatically tenant-filtered. The JWT carries organization context.
**ADs satisfied:** AD-4 (complete)
**FRs covered:** FR-1, FR-2, FR-3, FR-4 (cross-cutting tenant context applied to auth)

#### Epic 2: Diagnostic Engine Reliability & Architecture Integrity
Students receive accurate adaptive diagnostics powered by a stateless BKT engine that reads mastery from the database (not hardcoded values). The engine layer is separated from services, repositories handle all DB access, and all 11 tables have Alembic migrations. The engine survives restarts without losing state.
**ADs satisfied:** AD-1 (complete), AD-7 (stages 2-3)
**FRs covered:** FR-9, FR-10, FR-11, FR-12, FR-13

### Wave 2 — Core Loop & Infrastructure

#### Epic 3: Remediation Lifecycle, AI Pipeline & Mastery Loop
Students receive AI-generated remediation pathways (deterministic selection + LLM augmentation via Celery/LiteLLM), validated by experts before delivery. The full state machine cycles: DIAGNOSED → PROPOSED → VALIDATED → IN_PROGRESS → COMPLETED → PASSPORT_TESTING → MASTERED. Spaced re-surfacing re-introduces failed items. Passport verifies mastery; badges are awarded on pass, alerts triggered on fail.
**ADs satisfied:** AD-2 (complete), AD-3 (complete), AD-7 (stages 4-8)
**FRs covered:** FR-14, FR-15, FR-16, FR-17, FR-18, FR-19

#### Epic 4: Real-Time Pedagogical Alerts & Notifications
The system detects persistent difficulty and raises severity-tiered alerts (INFO/WARNING/CRITICAL), pushed in real time to parents and experts via SSE. Parents receive simplified messages; experts receive detailed pedagogical context. The orphaned AlertManager is wired into production code paths.
**ADs satisfied:** AD-5 (complete), AD-7 (alert stage)
**FRs covered:** FR-27

#### Epic 5: Offline-Resilient Student Experience
Students continue diagnostic and remediation work during connectivity drops. Answers and atom completions are written to a Dexie write-behind buffer immediately, then synced to the backend when connectivity returns. Questions are pre-fetched into IndexedDB. No work is lost.
**ADs satisfied:** AD-6 (complete)
**FRs covered:** FR-29, FR-30

### Wave 3 — Feature Completion

#### Epic 6: Expert Content Authoring & AI-Assisted Drafting
Experts can create, edit, and bulk-import curriculum content (modules, questions, knowledge atoms) through a fully functional authoring interface. They can request AI-drafted batches of items from a stated Algerian-curriculum reference, review/edit them, and publish. All AI-drafted content is marked DRAFT until expert-approved.
**FRs covered:** FR-5, FR-6, FR-7, FR-8, FR-8a

#### Epic 7: Pre-Literate Student Accessibility
Pre-literate Year 1-2 students can take diagnostics via audio read-aloud (question text spoken aloud in the item's language) and image-choice answer options (tapping pictures instead of reading text). The full author→render→score pipeline supports multiple_choice, image_choice, and numeric item types.
**FRs covered:** FR-8b, FR-8c

#### Epic 8: Parent Dashboard & Insights
Parents view their child's evolution through a radar chart (real mastery data, not mock), plain-language insight messages (zero raw scores as primary signals), and a daily off-platform reinforcement recommendation. The dashboard is powered by real API calls, not mock data.
**FRs covered:** FR-20, FR-21, FR-22

#### Epic 9: Expert Analytics & Classroom Tools
Experts view a competency heatmap (real student×competency data), auto-form remediation groups by shared gap profile, export reports as PDF/CSV, and print remediation cards for offline classroom use. The orphaned report exporter is wired into endpoints.
**FRs covered:** FR-23, FR-24, FR-25, FR-26

#### Epic 10: Bilingual Completeness & i18n Polish
The entire UI works seamlessly in Arabic (RTL, primary) and French (LTR) with no hardcoded strings. All missing translation key sections are populated. RTL/LTR logical CSS compliance is verified and enforced by lint.
**FRs covered:** FR-28

---

## Epic Dependencies

```
Wave 1:
  Epic 1 (Multi-Tenant) ──────┐
                               ├──── Epic 2 (Diagnostic Engine)
                               │           │
Wave 2:                        │           │
  Epic 3 (Remediation) ◄───────┘           │
    │                                      │
    ├── Epic 4 (Alerts/SSE) ◄──────────────┘
    │
    └── Epic 5 (Offline)

Wave 3:
  Epic 6 (Content Authoring) ◄── Epic 1, 2
  Epic 7 (Pre-Literate) ◄────── Epic 2, 6
  Epic 8 (Parent Dashboard) ◄── Epic 3, 4
  Epic 9 (Expert Analytics) ◄── Epic 2, 3
  Epic 10 (Bilingual) ── independent, any time
```

---

## Epic 1: Multi-Tenant Platform Foundation

**Goal:** The platform safely hosts multiple school organizations and independent household families on the same deployment, with complete data isolation. An independent parent self-registers, gets an auto-created household org, creates child accounts, and every query is tenant-filtered automatically.

**ADs satisfied:** AD-4
**FRs covered:** FR-1, FR-2, FR-3, FR-4
**Wave:** 1 (Structural Foundation — must complete first)

### Story 1.1: Axios Snake↔Camel Transform & Frontend HTTP Boundary

As a **developer**,
I want **the Axios service layer to transform snake_case API responses to camelCase and camelCase requests to snake_case automatically**,
So that **Vue components and stores never handle snake_case keys, per the architecture convention**.

**Acceptance Criteria:**

**Given** the Axios interceptor is configured in `src/services/api.ts`
**When** a response arrives with `{"access_token": "...", "organization_id": "..."}`
**Then** the interceptor transforms it to `{"accessToken": "...", "organizationId": "..."}`
**And** all subsequent service methods receive camelCase keys
**And** request payloads are transformed from camelCase to snake_case before sending
**And** the `auth.ts` store no longer manually destructures `access_token`/`refresh_token`

---

### Story 1.2: Organization & OrganizationMember Models + Migrations

As a **platform administrator**,
I want **Organization (SCHOOL/HOUSEHOLD) and OrganizationMember models with Alembic migrations**,
So that **the database schema supports multi-tenant isolation as the tenant boundary**.

**Acceptance Criteria:**

**Given** the Organization model is defined in `backend/app/models/organization.py`
**When** it is instantiated
**Then** it has fields: `id` (UUID PK), `name` (string), `type` (enum: `SCHOOL`, `HOUSEHOLD`), `is_system_org` (bool, default false), `created_at`, `updated_at`
**And** `OrganizationMember` is an association table with `user_id`, `organization_id`, `role` (enum: `STUDENT`, `PARENT`, `EXPERT`), `created_at`
**And** a system org with `is_system_org=True` is seeded via migration
**And** running `alembic upgrade head` creates the `organizations` and `organization_members` tables
**And** the User model's `parent_id` self-reference is preserved (parents still link to children directly within a household org)

---

### Story 1.3: Add organization_id FK to All Tenant-Scoped Models

As a **platform administrator**,
I want **every tenant-scoped model to carry a non-nullable `organization_id` foreign key**,
So that **all domain data is isolated per organization and tenant filtering can be enforced automatically**.

**Acceptance Criteria:**

**Given** the following models exist: `Module`, `Question`, `KnowledgeAtom`, `DiagnosticSession`, `DiagnosticAnswer`, `CompetencyProfile`, `RemediationPath`, `AtomCompletion`, `PassportAssessment`, `PedagogicalAlert`, `AlertRecipient`
**When** each model is updated
**Then** each has `organization_id: Mapped[UUID] = ForeignKey("organizations.id", nullable=False)`
**And** a relationship to `Organization` is defined
**And** shared-eligible models (`Module`, `Question`, `KnowledgeAtom`) also have `is_shared: bool = False`
**And** Alembic migrations are generated for each table (resolving the 1/11 migration gap)
**And** running `alembic upgrade head` creates all 11 tables with their FK constraints

---

### Story 1.4: Tenant Middleware — Automatic Query Filtering

As a **backend developer**,
I want **middleware that extracts `organization_id` from the JWT and injects it as a mandatory query filter on every repository query**,
So that **no service or engine ever filters by organization manually, and cross-tenant data access is impossible**.

**Acceptance Criteria:**

**Given** a request arrives with header `X-Organization-Id: {org_uuid}` and a valid JWT containing `(organization_id, role)` pairs
**When** the tenant middleware processes the request
**Then** it validates the `X-Organization-Id` header against the JWT's allowed orgs (403 if not a member)
**And** it sets a request-scoped `active_organization_id` context variable
**And** all repository queries automatically filter by this context variable (no manual `organization_id` filtering in services/engines)
**And** a query without an active organization context raises `RuntimeError`
**And** shared content (`is_shared=True`) is readable across tenants but the filter still applies

---

### Story 1.5: JWT Organization Claims & Auth Flow Update

As a **parent with children in multiple schools**,
I want **my JWT to carry all my `(organization_id, role)` pairs so I can switch contexts**,
So that **I can view each child's data scoped to their school**.

**Acceptance Criteria:**

**Given** a parent registers with email+password
**When** they authenticate via `POST /api/v1/auth/login/email`
**Then** the JWT access token contains `organizations: [{id, role, type}]` for each org they belong to
**And** a self-registering parent (no school invite) gets an auto-created `HOUSEHOLD` org where they are admin
**And** the refresh token flow preserves the org list
**And** PIN login (`POST /api/v1/auth/login/pin`) resolves the student's org from their `OrganizationMember` row

---

### Story 1.6: Self-Registration Flow for Independent Parents

As an **independent parent**,
I want **to self-register and automatically get a household organization**,
So that **I can use the platform without a school and create child accounts**.

**Acceptance Criteria:**

**Given** a parent visits the registration page and provides email + password + name
**When** they submit `POST /api/v1/auth/register`
**Then** a `User` (role=PARENT) is created
**And** an `Organization` (type=HOUSEHOLD) is auto-created with name `"{Parent Name}'s Household"`
**And** an `OrganizationMember` row links the parent to this org with role=PARENT
**And** the parent can create child accounts within this household org
**And** the parent is redirected to `/parent` (not `/parent/dashboard`) with the household org as active context (`Register.vue` Line 53 uses `router.push('/parent')`)

---

### Story 1.7: Frontend Org Switcher Component

As a **user belonging to multiple organizations**,
I want **an org switcher in the app header**,
So that **I can switch between my school view, household view, or multiple school views**.

**Acceptance Criteria:**

**Given** a user is authenticated and belongs to more than one organization
**When** they view the app header
**Then** an org switcher dropdown is visible showing all their orgs with type icons (school/household)
**And** selecting an org sets the `X-Organization-Id` header on all subsequent API calls
**And** the active org is stored in `authStore` and persisted to `localStorage`
**And** if the user belongs to only one org, the switcher is hidden
**And** switching orgs refreshes the current view's data for the new tenant context

---

### Story 1.8: Fix RBAC Enum Case Mismatch & Analytics Auth

As a **backend developer**,
I want **the RBAC role checks to use correct enum values**,
So that **expert-only endpoints actually work for experts**.

**Acceptance Criteria:**

**Given** the `require_expert` dependency in `core/security.py`
**When** an expert user accesses `/api/v1/analytics/*`
**Then** the role check compares against the correct enum value (`EXPERT`, not `expert`)
**And** the dependency is FastAPI `Depends`-compatible (extracts the JWT, resolves the user)
**And** an expert token calling an analytics endpoint returns 200, not 403
**And** a student token calling an analytics endpoint returns 403
**And** all role-checking functions across the codebase are audited for the same enum case bug
**And** the `auth.ts` store replaces `useI18n()` (which requires Vue setup context) with `i18n.global.t` for any locale-dependent string access outside components

---

### Story 1.9: Parent PIN Management Modal

As a **parent**,
I want **to view and reset my child's 4-digit PIN from my dashboard**,
So that **I can help my child log in if they forget their PIN**.

**Acceptance Criteria:**

**Given** the parent is on their dashboard
**When** they tap "Manage Children & PINs" in the header/child selector
**Then** a modal shows each child's name and current PIN (masked, with reveal toggle)
**And** the parent can generate a new random PIN per child
**And** the new PIN is persisted via `POST /api/v1/auth/children/{id}/pin`
**And** the modal uses i18n keys for all labels
**And** only the parent who "owns" the child can view/reset the PIN (enforced by RBAC + `parent_id` check)
**And** the PIN reveal uses a temporary display (auto-hides after 5 seconds)

---

## Epic 2: Diagnostic Engine Reliability & Architecture Integrity

**Goal:** Students receive accurate adaptive diagnostics powered by a stateless BKT engine that reads mastery from the database. The engine layer is separated from services, repositories handle all DB access, and all 11 tables have Alembic migrations. The engine survives restarts without losing state.

**ADs satisfied:** AD-1, AD-7 (stages 2-3)
**FRs covered:** FR-9, FR-10, FR-11, FR-12, FR-13
**Wave:** 1 (Structural Foundation)

### Story 2.1: Create Backend engines/ Layer — Extract Stateless Domain Logic

As a **backend developer**,
I want **a dedicated `engines/` directory with stateless pure functions for all domain logic**,
So that **engines never hold state between calls, per AD-1**.

**Acceptance Criteria:**

**Given** the current `services/diagnostic_engine.py` and `services/remediation_engine.py` hold in-memory state (`self.sessions`, `self.bkt_models`, `self._paths`, `self.question_stats`)
**When** the engines layer is created
**Then** `backend/app/engines/__init__.py`, `engines/bkt.py`, `engines/diagnostic_engine.py`, `engines/remediation_engine.py` exist
**And** BKT is a pure function: `update_mastery(current_p_learned: float, is_correct: bool, params: BKTParams) -> float`
**And** `DiagnosticEngine.select_next_question(mastery_estimates: dict, available_questions: list, ...) -> Question` takes all inputs as parameters, holds no `self.sessions` or `self.bkt_models`
**And** `RemediationEngine` takes pathway data as input, holds no `self._paths`
**And** `MultiArmBanditSelector` reads question stats from a repository parameter, not from `self.question_stats`
**And** all engines are instantiable without side effects and produce identical results given identical inputs

---

### Story 2.2: Create Backend repositories/ Layer — Centralize DB Access

As a **backend developer**,
I want **a `repositories/` layer that handles all database queries with automatic tenant filtering**,
So that **services never write raw SQL/ORM queries and tenant isolation is inescapable**.

**Acceptance Criteria:**

**Given** the current endpoints and services contain inline DB queries (e.g., `api/endpoints/diagnostic.py` does inline answer checking and mastery calculation)
**When** the repositories layer is created
**Then** `backend/app/repositories/__init__.py` and per-domain repository files exist (e.g., `repositories/diagnostic_repo.py`, `repositories/content_repo.py`, `repositories/remediation_repo.py`)
**And** every repository method accepts an `organization_id` parameter (injected from the tenant middleware context)
**And** every query filters by `organization_id` automatically
**And** the diagnostic endpoint no longer contains inline DB queries — it delegates to `DiagnosticService` which calls `DiagnosticRepo`
**And** the content endpoints delegate to `ContentService` → `ContentRepo`
**And** no `session.execute()` or `session.query()` call exists outside of repository files

---

### Story 2.3: Wire Diagnostic Endpoint to Engine — Kill Hardcoded Mastery

As a **student taking a diagnostic**,
I want **the system to use my actual BKT mastery estimate to select questions**,
So that **questions target my real knowledge boundary, not a hardcoded 0.5**.

**Acceptance Criteria:**

**Given** the current `api/endpoints/diagnostic.py` hardcodes `current_mastery=0.5` and `mastery_level="FAMILIAR"` (lines 192-193)
**When** the endpoint is refactored to use the engine
**Then** `POST /api/v1/diagnostic/answer` reads the student's `CompetencyProfile.p_learned` from the database
**And** passes it to `engines.bkt.update_mastery()` to get the updated mastery
**And** persists the updated mastery back to `CompetencyProfile`
**And** the next-question selector uses the real mastery estimate, not 0.5
**And** error classification uses the engine's `ErrorClassifier`, not inline logic
**And** the `DiagnosticEngine.sessions` in-memory dict is removed entirely — the session is read from DB each call
**And** the student dashboard (`student/Dashboard.vue`) checks for an active diagnostic session (`status=IN_PROGRESS`) on mount and renders a prominent, dismissible "Resume Diagnostic (Question N/M)" banner that navigates back to `DiagnosticRunner.vue`

---

### Story 2.4: Structured JSON Logging Middleware

As a **backend developer**,
I want **structured JSON logging with `organization_id`, `user_id`, and `request_id` on every log entry**,
So that **observability meets the NFR and no PII is logged**.

**Acceptance Criteria:**

**Given** the current codebase has no structured logging
**When** the logging middleware is implemented
**Then** every HTTP request generates a log entry with `request_id` (UUID), `user_id`, `organization_id`, `method`, `path`, `status_code`, `duration_ms`
**And** log entries are JSON-formatted (parseable by log aggregators)
**And** no PII appears in logs (no student names, no answers, no email addresses)
**And** a `request_id` header is added to every response for traceability
**And** errors are logged with stack traces at ERROR level

---

## Epic 3: Remediation Lifecycle, AI Pipeline & Mastery Loop

**Goal:** Students receive AI-generated remediation pathways validated by experts. The full state machine cycles through DIAGNOSED → PROPOSED → VALIDATED → IN_PROGRESS → COMPLETED → PASSPORT_TESTING → MASTERED. Spaced re-surfacing re-introduces failed items. Passport verifies mastery; badges awarded on pass.

**ADs satisfied:** AD-2, AD-3, AD-7 (stages 4-8)
**FRs covered:** FR-14, FR-15, FR-16, FR-17, FR-18, FR-19
**Wave:** 2 (Core Loop)
**Depends on:** Epic 1, Epic 2

### Story 3.1: Remediation State Machine — Add Missing States & Transition Guard

As a **backend developer**,
I want **the RemediationPath model to support all 7 states with enforced transitions**,
So that **the AD-2 state machine is correctly implemented and no path skips the expert validation gate**.

**Acceptance Criteria:**

**Given** the current `RemediationPathStatus` enum only has `IN_PROGRESS`, `COMPLETED`, `FAILED`
**When** the state machine is implemented
**Then** the enum includes: `DIAGNOSED`, `PROPOSED`, `VALIDATED`, `IN_PROGRESS`, `COMPLETED`, `ABANDONED`, `PASSPORT_TESTING`, `MASTERED`, `RETIRED`
**And** the service layer enforces valid transitions: DIAGNOSED→PROPOSED, PROPOSED→VALIDATED, PROPOSED→DIAGNOSED (reject), VALIDATED→IN_PROGRESS, IN_PROGRESS→COMPLETED, IN_PROGRESS→ABANDONED, COMPLETED→PASSPORT_TESTING, PASSPORT_TESTING→MASTERED, PASSPORT_TESTING→DIAGNOSED (fail), ABANDONED→PROPOSED, ABANDONED→RETIRED
**And** invalid transitions raise `409 Conflict` with a machine code
**And** the API layer cannot set status directly — only the service layer transitions state
**And** Alembic migration updates the enum type

---

### Story 3.2: Celery Tasks Infrastructure & LiteLLM Integration

As a **backend developer**,
I want **real Celery tasks and LiteLLM integration for async AI proposal generation**,
So that **the LLM is never in the synchronous request path and the proposal pipeline works asynchronously**.

**Acceptance Criteria:**

**Given** Celery is configured but has zero tasks, and LiteLLM is not installed
**When** the task infrastructure is built
**Then** `backend/app/tasks/__init__.py` and `tasks/ai_proposal.py` exist
**And** `litellm` is added to `requirements.txt`
**And** `tasks/ai_proposal.generate_remediation_proposal(session_id, ...)` is a `@celery_app.task` that: (1) reads the gap profile from the diagnostic result, (2) calls `engines/remediation_engine.py` for deterministic atom selection, (3) sends the gap profile + selected atoms to LiteLLM for augmentation, (4) stores the augmented proposal in the DB, (5) transitions the path to PROPOSED
**And** LiteLLM is configured via settings (`LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`) with a default model
**And** if LiteLLM is unavailable, the deterministic selection alone produces a valid proposal
**And** the Celery worker's `include` list points to `app.tasks`, not `app.services.alert_manager`

---

### Story 3.3: Expert Validation Queue & Workflow

As a **pedagogical expert**,
I want **to review AI-generated remediation proposals and approve or reject them**,
So that **no remediation path reaches a student without expert pedagogical validation**.

**Acceptance Criteria:**

**Given** a remediation path is in `PROPOSED` state
**When** the expert opens their validation queue
**Then** `GET /api/v1/remediation/validation-queue` returns all PROPOSED paths for their organization
**And** each proposal shows: student name, failed competencies, selected atoms with AI pedagogical justification, LLM-generated annotations
**And** the expert can approve (`POST /api/v1/remediation-paths/{id}/validate` → transitions to VALIDATED)
**And** the expert can reject with feedback (`POST /api/v1/remediation-paths/{id}/reject` → transitions back to DIAGNOSED, feedback is stored for the next AI generation cycle)
**And** proposal routing: SCHOOL org proposals → that school's expert queue; HOUSEHOLD org proposals → platform pedagogue pool queue
**And** a frontend validation queue view exists at `/expert/validation`

---

### Story 3.4: Student Remediation Execution — Atom Delivery & Progress Tracking

As a **student**,
I want **to follow my validated remediation pathway, consuming knowledge atoms in concrete→abstract order**,
So that **I learn the missed concept a different way and build toward mastery**.

**Acceptance Criteria:**

**Given** a remediation path is in `VALIDATED` state and the student starts it
**When** the student begins remediation
**Then** the path transitions to `IN_PROGRESS`
**And** atoms are delivered in concrete→abstract order (AUDIO_VISUAL/SIMULATION before abstract symbolic, MIND_MAP for comprehension gaps)
**And** `POST /api/v1/remediation-paths/{id}/atoms/{atom_id}/complete` records completion with timestamp
**And** `AtomCompletion` records track progress per atom
**And** when all atoms are completed, the path transitions to `COMPLETED`
**And** the student can pause/resume — progress is persisted in the DB, not in memory

---

### Story 3.5: Spaced Re-Surfacing of Failed Items (FR-16)

As a **student**,
I want **previously-failed items to reappear at spaced intervals**,
So that **my learning transfers to long-term memory instead of being immediately re-drilled**.

**Acceptance Criteria:**

**Given** a student failed an item during a diagnostic session
**When** the spaced re-surfacing scheduler runs
**Then** the item is eligible to reappear at spaced intervals (default: 1-day → 3-day → 7-day)
**And** a `SpacedRepetition` model or field tracks: `question_id`, `student_id`, `next_review_date`, `interval_days`, `ease_factor`
**And** the diagnostic engine's next-question selector includes due spaced-repetition items in its candidate pool
**And** correct answers on re-surfaced items increase the interval; incorrect answers reset it
**And** re-surfaced items are tagged so the student sees them as "review," not new content

---

### Story 3.6: Passport Competency Task — Wire Orphaned Component

As a **student who completed a remediation pathway**,
I want **to attempt the Passport competency task to verify my mastery**,
So that **I earn my competency badge and advance to the next challenge**.

**Acceptance Criteria:**

**Given** a remediation path is in `COMPLETED` state
**When** the path transitions to `PASSPORT_TESTING`
**Then** the `PassportAssessment.vue` component (currently orphaned) is rendered with the target competency's verification task
**And** `POST /api/v1/remediation-paths/{id}/passport/submit` records the outcome
**And** on pass: path → `MASTERED`, competency badge is awarded, mastery level updated to `MASTERED`, next competency unlocked
**And** on fail: path → `DIAGNOSED` (new remediation cycle), a pedagogical alert is raised at `WARNING` severity, an in-person support suggestion is surfaced to parent/expert
**And** the Passport is a single competency-scoped task, not a cumulative exam

---

### Story 3.7: Frontend remediationStore & Remediation Session Views

As a **student**,
I want **a reactive remediation session view driven by a Pinia store**,
So that **my progress through the pathway is tracked in the UI and persists across sessions**.

**Acceptance Criteria:**

**Given** the current frontend has no `remediationStore` and `RemediationSession.vue` fakes the passport with `setTimeout`
**When** the store and views are built
**Then** `src/stores/remediationStore.ts` manages: current path, current atom, atoms completed, passport state
**And** `RemediationSession.vue` renders atoms from the store, not inline state
**And** `PassportAssessment.vue` is imported and wired into the remediation flow
**And** all components call `remediationStore` methods, never `remediationService` directly
**And** the store calls `remediationService` which handles HTTP (with camelCase transform from Story 1.1)

---

## Epic 4: Real-Time Pedagogical Alerts & Notifications

**Goal:** The system detects persistent difficulty and raises severity-tiered alerts pushed in real time to parents and experts via SSE. The orphaned AlertManager is wired into production code paths.

**ADs satisfied:** AD-5
**FRs covered:** FR-27
**Wave:** 2 (Core Loop Infrastructure)
**Depends on:** Epic 1, Epic 2

### Story 4.1: SSE Endpoint & sse-starlette Integration

As a **backend developer**,
I want **an SSE endpoint backed by Redis Pub/Sub per tenant**,
So that **real-time notifications are pushed to clients without polling**.

**Acceptance Criteria:**

**Given** `sse-starlette` is not installed and no SSE endpoint exists
**When** the SSE infrastructure is built
**Then** `sse-starlette` is added to `requirements.txt`
**And** `GET /api/v1/events/stream` returns an `EventSourceResponse`
**And** the endpoint subscribes to a Redis Pub/Sub channel keyed by `organization_id`
**And** the SSE connection requires authentication (JWT validated)
**And** the tenant context (`organization_id`) determines which Pub/Sub channel to subscribe to
**And** the Caddyfile excludes `/api/v1/events/stream` from `encode gzip zstd` (compression buffers streaming)
**And** the connection auto-reconnects natively (SSE spec)

---

### Story 4.2: Wire AlertManager into Production Code Paths

As a **backend developer**,
I want **the existing AlertManager detectors to be called when diagnostic answers and passport results are submitted**,
So that **pedagogical alerts are actually generated, not just tested in isolation**.

**Acceptance Criteria:**

**Given** `AlertManager.check_session_for_alerts()` exists but is never called in production code
**When** the alert system is wired in
**Then** `DiagnosticService.submit_answer()` calls `AlertManager.check_session_for_alerts()` after each answer
**And** `RemediationService.submit_passport()` calls `AlertManager.check_passport_failure()` on passport fail
**And** generated alerts are persisted to the `PedagogicalAlert` table
**And** alerts are published to the Redis Pub/Sub channel for SSE delivery
**And** `GET /api/v1/alerts?since={timestamp}` returns alerts for the active org since the given time (for reconnect recovery)

---

### Story 4.3: Alert Trigger Thresholds (Resolve OQ-4)

As a **pedagogical expert**,
I want **alert trigger thresholds defined so the system knows when to raise INFO vs WARNING vs CRITICAL**,
So that **alerts are meaningful and not noise**.

**Acceptance Criteria:**

**Given** OQ-4 asks: how many failures over what window map to which severity
**When** thresholds are defined
**Then** `INFO` is raised on: first failure on a competency (informational, no action needed)
**And** `WARNING` is raised on: 2+ failures on the same competency within 7 days, OR passport failure
**And** `CRITICAL` is raised on: 3+ failures on the same competency within 7 days, OR 2 passport failures on the same competency, OR abandonment
**And** thresholds are configurable via settings (not hardcoded)
**And** a duplicate-prevention mechanism prevents re-raising the same alert within a cooldown window

---

### Story 4.4: Frontend useSSE Composable & alertStore

As a **parent**,
I want **to receive real-time alert notifications via SSE without polling**,
So that **I know immediately when my child needs attention**.

**Acceptance Criteria:**

**Given** the frontend has no SSE consumer and no `alertStore`
**When** the SSE composable and store are built
**Then** `src/composables/useSSE.ts` manages the `EventSource` connection, auto-reconnect, and fallback to polling
**And** `src/stores/alertStore.ts` receives SSE events and maintains a reactive list of active alerts
**And** the `PedagogicalAlertBox.vue` component reads from `alertStore`, not from `alertService` directly
**And** on SSE connection drop, the composable falls back to polling `GET /api/v1/alerts?since={last_timestamp}`
**And** on reconnect, missed events are recovered via the same endpoint
**And** parent receives simplified alert messages; expert receives detailed pedagogical context

---

## Epic 5: Offline-Resilient Student Experience

**Goal:** Students continue diagnostic and remediation work during connectivity drops. Answers and atom completions are written to a Dexie write-behind buffer, then synced on reconnect. No work is lost.

**ADs satisfied:** AD-6
**FRs covered:** FR-29, FR-30
**Wave:** 2 (Core Loop Infrastructure)
**Depends on:** Epic 1

### Story 5.1: Dexie Write-Behind Buffer for Student Answers

As a **student on an unstable connection**,
I want **my answers written to local storage immediately and synced to the backend when I reconnect**,
So that **I never lose work due to connectivity drops**.

**Acceptance Criteria:**

**Given** the current `DiagnosticRunner.vue` calls `diagnosticService.submitAnswer()` directly (HTTP), which throws on network failure
**When** the write-behind buffer is implemented
**Then** answers are written to Dexie's `pending_answers` table immediately
**And** if online, the answer is also sent to the backend immediately (write-through)
**And** if offline, the answer is queued in Dexie with `sync_status: 'PENDING'`
**And** a connectivity listener (`navigator.onLine` + `online`/`offline` events) triggers sync
**And** on reconnect, all pending answers are flushed to the backend in order
**And** the backend `POST /api/v1/diagnostic/answer` is idempotent (safe to retry)

---

### Story 5.2: Backend Sync Endpoint for Offline Sessions

As a **backend developer**,
I want **a sync endpoint that receives batched offline answers and completions**,
So that **the frontend can flush its pending queue efficiently on reconnect**.

**Acceptance Criteria:**

**Given** no `/api/v1/sync` endpoint exists
**When** the sync endpoint is built
**Then** `POST /api/v1/sync/batch` accepts `{answers: [...], completions: [...], since: timestamp}`
**And** it processes each item idempotently (duplicate detection by client-generated ID)
**And** it returns `{accepted: int, rejected: int, errors: [{id, reason}]}`
**And** conflict resolution: last-write-wins for atom completions (idempotent), server-wins for state transitions (state machine is authoritative)
**And** the endpoint is rate-limited to prevent abuse

---

### Story 5.3: Pre-Fetch Questions into Dexie & Connectivity Detection

As a **student**,
I want **diagnostic questions pre-fetched into local storage when I'm online**,
So that **I can continue my session even if connectivity drops mid-test**.

**Acceptance Criteria:**

**Given** `cacheQuestions()` exists in `offlineModule.ts` but is never called
**When** the pre-fetch logic is implemented
**Then** when a diagnostic session starts, the next N questions are pre-fetched and cached in Dexie
**And** the diagnostic runner serves questions from Dexie cache when offline
**And** `navigator.onLine` is checked before each API call, with Dexie fallback on offline
**And** a visual indicator shows online/offline status to the student
**And** `getPendingSyncSessions()` and `markSessionSynced()` are called by the sync flush logic (no longer dead code)

---

### Story 5.4: useOfflineSync Composable

As a **frontend developer**,
I want **a composable that encapsulates offline sync logic**,
So that **diagnostic and remediation views can use offline features without duplicating connectivity logic**.

**Acceptance Criteria:**

**Given** `src/composables/` does not exist
**When** the composable is created
**Then** `src/composables/useOfflineSync.ts` exposes: `isOnline`, `pendingCount`, `syncNow()`, `queueAnswer()`, `queueCompletion()`
**And** it manages the Dexie write-behind buffer, connectivity events, and sync flush
**And** `DiagnosticRunner.vue` and `RemediationSession.vue` use this composable instead of calling services directly
**And** the composable integrates with the PWA service worker for background sync

---

## Epic 6: Expert Content Authoring & AI-Assisted Drafting

**Goal:** Experts create, edit, and bulk-import curriculum content through a functional authoring interface. They can request AI-drafted items from Algerian-curriculum references, review them, and publish.

**FRs covered:** FR-5, FR-6, FR-7, FR-8, FR-8a
**Wave:** 3 (Feature Completion)
**Depends on:** Epic 1, Epic 2

### Story 6.1: Expert Module CRUD via Repository Layer

As a **pedagogical expert**,
I want **to create, edit, and publish curriculum modules**,
So that **I can build the content structure for diagnostics and remediation**.

**Acceptance Criteria:**

**Given** the current content endpoints are fat (inline DB queries) and `expert/ModuleEditor.vue` (view) is a 20-line stub
**When** the CRUD is refactored
**Then** `ContentService` delegates to `ContentRepo` for all DB access (tenant-filtered)
**And** an expert can create a module with: title, subject (Arabic/Math), year-band (Y1-2/Y3/Y4-5), description
**And** an expert can edit and publish modules
**And** a student/parent calling content-mutation endpoints gets 403
**And** the `ModuleEditor.vue` view is fully functional (not a stub), using the real `contentStore`
**And** the question builder in `ModuleEditor.vue` includes a side-by-side collapsible "Live Preview" toggle showing real-time student-facing rendering for all item types
**And** the dead route `/expert/modules/:id/questions` is fixed or removed

---

### Story 6.2: Question-Bank & Knowledge Atom Management

As a **pedagogical expert**,
I want **to create question items and knowledge atoms linked to competencies**,
So that **diagnostics can assess and remediation can target specific gaps**.

**Acceptance Criteria:**

**Given** the current question/atom CRUD exists but bypasses repositories
**When** the management is refactored
**Then** an expert can create question items with: competency link, difficulty (1-10), estimated time, correct answer, distractors, type (multiple_choice/image_choice/numeric)
**And** an expert can create knowledge atoms with: type (AUDIO_VISUAL/SIMULATION/MIND_MAP), competency link, content payload
**And** a question with no correct-answer key is rejected on validation (400)
**And** all CRUD goes through `ContentService` → `ContentRepo` (tenant-filtered)
**And** the `QuestionEditor.vue` component supports all item types

---

### Story 6.3: Bulk Import with Per-Row Validation

As a **pedagogical expert**,
I want **to bulk-import modules/items/atoms from a structured file**,
So that **I can populate pilot content efficiently without manual entry**.

**Acceptance Criteria:**

**Given** FR-8 requires bulk import
**When** the bulk import feature is implemented
**Then** `POST /api/v1/content/bulk-import` accepts a JSON or CSV payload
**And** valid rows are created; invalid rows are reported per-row with error messages
**And** the batch does not abort on a single invalid row (partial success)
**And** the response includes `{created: int, failed: int, errors: [{row, reason}]}`
**And** all created items belong to the active organization

---

### Story 6.4: AI-Assisted Content Drafting (FR-8a)

As a **pedagogical expert**,
I want **to request AI-drafted question items and knowledge atoms from a curriculum reference**,
So that **I can accelerate content authoring while maintaining full editorial control**.

**Acceptance Criteria:**

**Given** FR-8a is not built
**When** the AI drafting feature is implemented
**Then** `POST /api/v1/content/ai-draft` accepts `{subject, year_band, competency, curriculum_reference}` and enqueues a Celery task
**And** the task calls LiteLLM with the curriculum reference and produces draft items mapped to the target competency
**And** all AI-drafted content is marked `DRAFT` status (never auto-published)
**And** the expert reviews, edits, and publishes or discards the drafts
**And** guardrails: the prompt instructs the LLM to align to Algerian curriculum, avoid hallucinated competencies, and respect bilingual AR/FR (OQ-9 addressed)
**And** the expert sees a diff between AI-drafted and edited versions before publishing

---

## Epic 7: Pre-Literate Student Accessibility

**Goal:** Pre-literate Year 1-2 students take diagnostics via audio read-aloud and image-choice answer options.

**FRs covered:** FR-8b, FR-8c
**Wave:** 3 (Feature Completion)
**Depends on:** Epic 2, Epic 6

### Story 7.1: Audio Read-Aloud for Question Text (FR-8b)

As a **pre-literate Year-1 student**,
I want **the question text read aloud to me**,
So that **I can understand the item without reading**.

**Acceptance Criteria:**

**Given** FR-8b is not built
**When** the audio read-aloud feature is implemented
**Then** `DiagnosticQuestion.vue` shows a play button when the question has audio media or when the student's year-band is Y1-2
**And** tapping play uses either: (a) an audio file from `media_urls`, or (b) Web Speech API (`speechSynthesis`) as fallback
**And** the audio is spoken in the item's language (AR/FR)
**And** items for Y1-2 are flagged `requires_audio: true` and the UI prompts the child to listen first
**And** the audio auto-plays once when the question appears (with a replay button)
**And** the play control is accessible (WCAG: keyboard-focusable, ARIA label)

---

### Story 7.2: Image-Choice Item Type (FR-8c)

As a **pre-literate Year-1 student**,
I want **to answer by tapping pictures instead of reading text**,
So that **I can demonstrate knowledge without literacy barriers**.

**Acceptance Criteria:**

**Given** FR-8c is not built and `image_choice` type doesn't exist
**When** the image-choice type is implemented
**Then** the question model supports `type: "image_choice"` with options as image URLs
**And** `DiagnosticQuestion.vue` renders image buttons as options when type is `image_choice`
**And** the recorded answer maps back to correct/incorrect evaluation like any other type
**And** the `QuestionEditor.vue` supports authoring image-choice items (upload image per option)
**And** the full pipeline works: author (expert) → render (student) → score (backend)
**And** `multiple_choice`, `image_choice`, and `numeric` all work end-to-end

---

## Epic 8: Parent Dashboard & Insights

**Goal:** Parents view their child's evolution through a real radar chart, plain-language insights, and daily reinforcement recommendations — all powered by real API data.

**FRs covered:** FR-20, FR-21, FR-22
**Wave:** 3 (Feature Completion)
**Depends on:** Epic 3, Epic 4

### Story 8.1: Real Dashboard API & Replace Mock dashboardService

As a **parent**,
I want **my dashboard to show my child's real mastery data**,
So that **I see actual progress, not placeholder mock data**.

**Acceptance Criteria:**

**Given** `dashboardService.ts` returns hardcoded mock objects and `DashboardAggregator` exists but may not be wired
**When** the real dashboard is implemented
**Then** `GET /api/v1/dashboard/overview` returns real data from `DashboardService` (which calls `DashboardRepo`, tenant-filtered)
**And** the response includes: per-subject average mastery, competency breakdown, recent sessions, active alerts
**And** `dashboardService.ts` calls the real API (no more `Promise.resolve(mockChildren)`)
**And** the parent sees only their own children's data (enforced by tenant + parent_id)
**And** `src/stores/dashboardStore.ts` manages the dashboard state reactively
**And** `dashboardService.ts` normalizes API responses defensively: `(response.data.items || response.data).map(...)`
**And** when no diagnostic data exists for any child, the dashboard renders an onboarding checklist (Step 1: PIN, Step 2: Diagnostic, Step 3: View insights) instead of blank charts

---

### Story 8.2: Subject-Strength Radar Chart with vue-chartjs

As a **parent**,
I want **a radar chart showing my child's mastery balance across subjects**,
So that **I can see at a glance where my child excels and where they need help**.

**Acceptance Criteria:**

**Given** `vue-chartjs` and `chart.js` are installed but unused; `SubjectRadarChart.vue` uses plain divs
**When** the radar chart is implemented
**Then** `SubjectRadarChart.vue` uses `<Radar>` from `vue-chartjs` with real mastery data
**And** the chart renders one axis per subject with the child's average mastery level (0-1 scale)
**And** the chart respects RTL layout (Arabic labels render correctly)
**And** the chart is responsive and mobile-friendly (parent is on a phone)
**And** the component reads data from `dashboardStore`, not directly from a service

---

### Story 8.3: Smart Insight Messages (Zero Raw Scores)

As a **parent**,
I want **my child's strengths and gaps described in plain language**,
So that **I understand what to do without needing pedagogical expertise**.

**Acceptance Criteria:**

**Given** FR-21 requires zero raw numeric scores as primary signals
**When** the insight system is implemented
**Then** the dashboard shows sentence-form insights using Glossary terms (e.g., "excels in oral expression but needs help writing تاء مربوطة")
**And** no raw numeric scores (like "6/10" or "0.73") appear as primary signals anywhere on the parent dashboard
**And** insights are generated server-side by `DashboardService.generate_insights(mastery_profiles)` and returned as structured sentences
**And** insights reference specific competencies by name, not code
**And** the insight language is localized (AR/FR)

---

### Story 8.4: Daily Reinforcement Recommendation

As a **parent**,
I want **one daily off-platform reinforcement activity tied to my child's current gap**,
So that **I know exactly what to do with my child today**.

**Acceptance Criteria:**

**Given** FR-22 requires exactly one recommendation per day
**When** the recommendation system is implemented
**Then** the dashboard shows exactly one recommendation card per day per child
**And** the recommendation is keyed to the child's most-recent failed competency
**And** the recommendation is an off-platform (non-screen) activity (e.g., "Practice writing تاء مربوطة with your child for 10 minutes using sand tray")
**And** recommendations are generated from a template library keyed by competency + error type
**And** the recommendation changes daily and is cached until the next day

---

## Epic 9: Expert Analytics & Classroom Tools

**Goal:** Experts view competency heatmaps (real data), auto-form remediation groups, export reports, and print remediation cards.

**FRs covered:** FR-23, FR-24, FR-25, FR-26
**Wave:** 3 (Feature Completion)
**Depends on:** Epic 2, Epic 3

### Story 9.1: Real Competency Heatmap Data

As a **pedagogical expert**,
I want **a heatmap of my class's competency mastery with real student data**,
So that **I can see who needs help and on what**.

**Acceptance Criteria:**

**Given** `analyticsService.ts` returns hardcoded mock data and `CompetencyHeatmap.vue` exists but uses mock data
**When** the real heatmap is implemented
**Then** `GET /api/v1/analytics/heatmap?module_id={id}` returns real student×competency data from `AnalyticsService` (tenant-filtered)
**And** each cell maps mastery level to color: NOT_STARTED/ATTEMPTED → red, FAMILIAR → yellow, PROFICIENT/MASTERED → green
**And** `analyticsService.ts` calls the real API (no more mock objects)
**And** `CompetencyHeatmap.vue` renders from `analyticsStore`, not from mock data
**And** the expert sees only students in their organization

---

### Story 9.2: Auto-Grouping into Remediation Groups

As a **pedagogical expert**,
I want **to auto-form remediation groups from the heatmap**,
So that **I can plan differentiated classroom sessions**.

**Acceptance Criteria:**

**Given** the auto-grouping logic exists in the engine but the endpoint reimplements it differently
**When** the auto-grouping is wired properly
**Then** `POST /api/v1/analytics/auto-group` clusters students by shared failed competency + error type
**And** the endpoint delegates to the engine (not inline logic)
**And** the response returns groups: `[{competency, error_type, students: [...]}]`
**And** the expert can see suggested groups overlaid on the heatmap

---

### Story 9.3: Report Export (PDF/CSV) — Wire Orphaned Exporter

As a **pedagogical expert**,
I want **to export analytics reports as PDF or CSV**,
So that **I can share and archive student progress data**.

**Acceptance Criteria:**

**Given** `ReportExporter` exists in `services/report_exporter.py` but is never wired to an endpoint
**When** the export is wired
**Then** `GET /api/v1/analytics/export?format=csv` returns a CSV download with stable headers (student, competency, mastery_level, last_assessed)
**And** `GET /api/v1/analytics/export?format=pdf` returns a PDF download with the heatmap data
**And** the exporter is called by `AnalyticsService`, which delegates to `AnalyticsRepo` for data
**And** the export includes only the active organization's students
**And** CSV headers are machine-parseable and documented

---

### Story 9.4: Printable Remediation Cards

As a **pedagogical expert**,
I want **to print a remediation card per student or group**,
So that **I can use it offline in the classroom**.

**Acceptance Criteria:**

**Given** FR-26 is not built
**When** the remediation cards are implemented
**Then** `GET /api/v1/analytics/remediation-cards?student_id={id}` returns a print-formatted view
**And** the card contains: student name(s), their failed competencies, recommended atoms, error classifications
**And** the card has a print CSS stylesheet (no interactive elements, page-break-friendly)
**And** the expert can print cards for a single student or an entire remediation group
**And** the frontend has a "Print Cards" button in the analytics view

---

## Epic 10: Bilingual Completeness & i18n Polish

**Goal:** The entire UI works seamlessly in Arabic (RTL) and French (LTR) with no hardcoded strings.

**FRs covered:** FR-28
**Wave:** 3 (Feature Completion)
**Depends on:** None (can run in parallel with any epic)

### Story 10.1: Extract All Hardcoded Strings into i18n Keys

As a **developer**,
I want **all hardcoded Arabic/French strings extracted into locale files**,
So that **the UI is fully translatable and no raw text leaks into views**.

**Acceptance Criteria:**

**Given** many views contain hardcoded Arabic strings (`student/Dashboard.vue`, `expert/Dashboard.vue`, `expert/Analytics.vue`, `parent/Alerts.vue`, `RemediationSession.vue`, `Login.vue`)
**When** the strings are extracted
**Then** every user-facing string in every `.vue` file uses `$t('key.path')` or `t('key.path')`
**And** `ar.json` and `fr.json` contain all keys referenced by the codebase
**And** the missing key sections are populated: `passport.*`, `remediation.*`, `validation.*`, `grades.*`, `alerts.markRead`, `alerts.viewAll`
**And** no raw Arabic or French text appears in `.vue` template sections (verified by lint)

---

### Story 10.2: RTL/LTR Compliance Verification & Lint Enforcement

As a **developer**,
I want **physical-direction CSS utilities banned and logical equivalents enforced**,
So that **RTL layout is correct and maintainable**.

**Acceptance Criteria:**

**Given** the architecture spine bans physical-direction Tailwind utilities (`pl-*`, `pr-*`, `left-*`, `right-*`, `text-left`)
**When** the lint rule is verified and enforced
**Then** an ESLint rule (or Tailwind plugin) flags any physical-direction utility usage
**And** all existing physical-direction utilities are replaced with logical equivalents (`ps-*`, `pe-*`, `start-*`, `end-*`, `text-start`)
**And** `toLocaleDateString` calls use the active locale, not hardcoded `'ar'`
**And** the font family swap on locale change is verified for both AR and FR
**And** a visual review confirms no layout breakage in either direction

---

### Story 10.3: Global Language Toggle in App Header

As a **user on any page**,
I want **a permanent Arabic ↔ Français toggle in the app header**,
So that **I can switch language from any screen without navigating to a settings page**.

**Acceptance Criteria:**

**Given** the user is on any authenticated page
**When** they view the app header (`AppHeader.vue`)
**Then** a toggle switch labeled `العربية ↔ Français` is visible
**And** tapping it switches locale, `dir` attribute, and all UI text instantly (per FR-28)
**And** the toggle is visible on all screen sizes (including mobile)
**And** the selected language persists in `localStorage`
**And** the toggle uses logical CSS (no physical direction utilities)

---

## Summary

| Metric | Count |
|--------|-------|
| **Total Epics** | 10 |
| **Wave 1 (Structural)** | 2 epics, 13 stories |
| **Wave 2 (Core Loop)** | 3 epics, 14 stories |
| **Wave 3 (Feature Completion)** | 5 epics, 14 stories |
| **Total Stories** | 41 |
| **FRs Covered** | 30/30 (100%) |
| **ADs Addressed** | 7/7 (100%) |
| **OQs Resolved** | OQ-4 (Story 4.3), OQ-10 (Story 3.5, confirmed absent) |
| **OQs Addressed** | OQ-5 (Story 3.6 thresholds), OQ-9 (Story 6.4 guardrails) |
| **NFRs Addressed** | NFR-MIGRATION (Stories 1.2/1.3), NFR-OBSERVABILITY (Story 2.4), NFR-I18N (Epic 10), NFR-A11Y (Epic 7) |
