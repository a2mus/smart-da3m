# Epic 6 Context: Expert Content Authoring & AI-Assisted Drafting

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Enable pedagogical experts to create, edit, publish, and bulk-import curriculum modules, question bank items, and knowledge atoms through a functional authoring interface, as well as generate AI-drafted content aligned with Algerian curriculum standards.

## Stories

- Story 6.1: Expert Module CRUD via Repository Layer
- Story 6.2: Question-Bank & Knowledge Atom Management
- Story 6.3: Bulk Import with Per-Row Validation
- Story 6.4: AI-Assisted Content Drafting (FR-8a)

## Requirements & Constraints

- All DB access for content mutation and retrieval must go through `ContentService` delegating to `ContentRepo` with tenant isolation (`organization_id` filtering).
- Experts (users with EXPERT or ADMIN role) can perform full CRUD operations on curriculum modules, question bank items, and knowledge atoms.
- Non-expert users (students, parents) attempting content mutation must receive HTTP 403 Forbidden.
- Content items must specify valid subject (ARABIC, MATH) and year-band (Y1-2, Y3, Y4-5).
- Question items require validation: correct answer key must be present (or HTTP 400 rejected).
- Front-end views (`ModuleEditor.vue`, `ModuleList.vue`, `QuestionEditor.vue`) must use `contentStore` (Pinia) and backend API endpoints, replacing hardcoded stubs.

## Technical Decisions

- **Layering Architecture**: FastAPI Controller Layer (`app/api/endpoints/content.py`) → Business Logic Service (`app/services/content.py` / `ContentService`) → Data Access Repository (`app/repositories/content_repo.py` / `ContentRepo`) → SQLAlchemy Models.
- **Tenant Security**: `ContentRepo` queries automatically apply active `organization_id` filter via `tenant_middleware` or explicit repository scoping.
- **Frontend Architecture**: Vue 3 + Composition API + Pinia `contentStore` (`frontend/src/stores/contentStore.ts`) + Axios HTTP boundary (snake_case/camelCase transformed).

## UX & Interaction Patterns

- Module management UI: List of modules with filter by subject/year band, inline or page editor for module metadata and publishing status.
- Question & Atom management: Form-based editor supporting item types (multiple choice, image choice, numeric) and knowledge atom types (audio visual, simulation, mind map).
