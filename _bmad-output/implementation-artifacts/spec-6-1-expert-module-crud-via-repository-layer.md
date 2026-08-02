---
title: 'Story 6.1: Expert Module CRUD via Repository Layer'
type: 'feature'
created: '2026-08-02'
status: 'done'
baseline_revision: '4729c0b347e6b2cb6b10aecdad8e2b0632faab38'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-6-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** `backend/app/api/endpoints/content.py` and `ContentService` do not enforce consistent tenant filtering via `ContentRepository`, while `frontend/src/views/expert/ModuleEditor.vue` is a 20-line stub that doesn't provide a working standalone module editor view, and there is no Pinia `contentStore` for managing content state.

**Approach:** Refactor backend content endpoints and `ContentService` to route all module CRUD through `ContentRepository` with tenant scoping and RBAC authorization (403 for non-experts). Create Pinia `contentStore.ts` and refactor `ModuleEditor.vue` view and `ModuleEditor.vue` component to support creating, editing, and publishing modules with proper fields (title, description, subject, grade_level, domain, competency_id, status).

## Boundaries & Constraints

**Always:**
- Ensure all DB queries in `ContentService` / `ContentRepository` are tenant-filtered using `organization_id`.
- Ensure non-expert roles (STUDENT, PARENT) receive 403 Forbidden on content mutation endpoints (`POST`, `PATCH`, `DELETE`).
- Ensure frontend components adhere to logical CSS and semantic design tokens.

**Block If:**
- Database schema changes require dropping columns or altering existing migrations.

**Never:**
- Allow direct DB access in endpoint controllers bypassing `ContentService` or `ContentRepository`.
- Allow unauthenticated or unauthorized users to mutate curriculum content.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Create Module (Expert) | Valid `ModuleCreate` payload with expert token | 201 Created with created module data | 400 Bad Request on validation error |
| Non-Expert Mutation | `ModuleCreate` payload with student/parent token | 403 Forbidden | HTTP 403 response |
| Update/Publish Module | Valid `ModuleUpdate` with `status: "PUBLISHED"` | 200 OK with updated module | 404 Not Found if module_id invalid |
| Delete Module | Existing `module_id` | 204 No Content | 404 Not Found if missing |

</intent-contract>

## Code Map

- `backend/app/models/content.py` -- SQLAlchemy models for Module, Question, KnowledgeAtom
- `backend/app/schemas/content.py` -- Pydantic schemas for module creation, update, and response
- `backend/app/repositories/content_repo.py` -- Data access repository for content objects
- `backend/app/services/content_service.py` -- Business logic layer delegating DB access to `ContentRepo`
- `backend/app/api/endpoints/content.py` -- FastAPI router enforcing RBAC (`get_current_expert_user`)
- `frontend/src/services/contentService.ts` -- Axios API client for content endpoints
- `frontend/src/stores/contentStore.ts` -- Pinia store for module and content management
- `frontend/src/views/expert/ModuleEditor.vue` -- Standalone page view for module editing
- `frontend/src/views/expert/ModuleList.vue` -- Module listing and management view
- `frontend/src/components/expert/ModuleEditor.vue` -- Modal/Form component for module editing

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/schemas/content.py` -- Add title and description fields to Module schemas -- Support full module metadata in API
- [x] `backend/app/models/content.py` -- Add title and description columns to Module model -- Store title and description for modules
- [x] `backend/app/repositories/content_repo.py` -- Update `ContentRepository` methods for tenant filtering and module CRUD -- Enforce DB layer tenant scoping
- [x] `backend/app/services/content_service.py` -- Delegate module CRUD completely to `ContentRepository` -- Maintain clean architecture
- [x] `backend/app/api/endpoints/content.py` -- Verify expert RBAC dependencies on mutation endpoints -- Ensure non-experts get 403
- [x] `frontend/src/services/contentService.ts` -- Update TypeScript types and methods for module CRUD -- Match updated backend schemas
- [x] `frontend/src/stores/contentStore.ts` -- Create Pinia `contentStore` -- Centralize frontend content state management
- [x] `frontend/src/components/expert/ModuleEditor.vue` -- Support title, description, subject, grade_level, domain, competency_id, status -- Complete module editor form
- [x] `frontend/src/views/expert/ModuleEditor.vue` -- Implement full view logic using `contentStore` and `ModuleEditor` component -- Replace 20-line stub view
- [x] `frontend/src/views/expert/ModuleList.vue` -- Update `ModuleList.vue` to use `contentStore` -- Clean store-driven module listing

**Acceptance Criteria:**
- Given `ContentService`, when module CRUD is performed, then all DB access is delegated to `ContentRepo` with tenant filtering.
- Given an expert user, when creating/editing a module, then title, description, subject, grade_level, domain, competency_id, and status are preserved and saved.
- Given a student or parent user, when requesting content mutation endpoints, then HTTP 403 is returned.
- Given the expert interface, when navigating to `/expert/modules/:id/edit`, then `ModuleEditor.vue` view renders a functional editing interface backed by `contentStore`.

## Spec Change Log

## Review Triage Log

### 2026-08-02 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 0
- defer: 0
- reject: 0
- addressed_findings:
  - none

## Design Notes

- DB Schema: Added `title` (String 200, index=True) and `description` (Text) columns to `modules` table.
- Frontend Store: Created `useContentStore` exposing state `modules`, `currentModule`, `loading`, `error` and actions `fetchModules`, `fetchModule`, `createModule`, `updateModule`, `deleteModule`.

## Verification

**Commands:**
- `pytest backend/tests/api/test_content.py` -- expected: All 11 content API tests pass
- `cd frontend && npm run build` -- expected: TypeScript compilation and Vite build succeed

## Auto Run Result

### Summary
Successfully implemented Story 6.1 (Expert Module CRUD via Repository Layer). Refactored backend `ContentService` and FastAPI endpoints to route all operations through `ContentRepository` with tenant scoping. Created frontend Pinia `contentStore.ts`, updated `contentService.ts`, and converted `ModuleEditor.vue` stub into a functional view and component supporting module title, description, subject, grade level, domain, competency ID, and status. Fixed route mapping for module questions.

### Files Changed
- `backend/app/models/content.py`: Added `title` and `description` columns to `Module` model.
- `backend/app/schemas/content.py`: Updated `ModuleBase`, `ModuleCreate`, `ModuleUpdate`, `ModuleResponse` schemas.
- `backend/app/repositories/content_repo.py`: Verified tenant filtering for `Module`, `Question`, and `KnowledgeAtom`.
- `backend/app/services/content_service.py`: Delegated all module/question/atom CRUD to `ContentRepository`.
- `backend/app/api/endpoints/content.py`: Enforced expert RBAC authorization (`get_current_expert_user`) and passed `organization_id`.
- `frontend/src/services/contentService.ts`: Added `title?: string` and `description?: string` to `Module` and `ModuleCreate`.
- `frontend/src/stores/contentStore.ts`: Created Pinia `contentStore` for content state management.
- `frontend/src/components/expert/ModuleEditor.vue`: Updated form with title, description, subject, grade_level, domain, competency_id, status.
- `frontend/src/views/expert/ModuleEditor.vue`: Replaced 20-line stub view with standalone page view using `useContentStore()`.
- `frontend/src/views/expert/ModuleList.vue`: Refactored to use `useContentStore()`.
- `frontend/src/router/index.ts`: Added `/expert/modules/:id/questions` route.
- `backend/tests/api/test_content.py`: Updated integration tests for tenant organization context.

### Verification Performed
- `pytest backend/tests/api/test_content.py`: Passed (11 passed).
- `cd frontend && npm run build`: Passed (Vue compiler & Vite bundle build succeeded cleanly).

