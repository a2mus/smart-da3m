---
title: 'Story 6.2: Question-Bank & Knowledge Atom Management'
type: 'feature'
created: '2026-08-02'
status: 'done'
baseline_revision: 'ece44ea270f0942a01770a9ce514f46eea3ca681'
final_revision: '579a3a6b1091002dc0b282f3c39f126f7f631298'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-6-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** Backend question validation permits questions with missing or empty correct answer keys, while `ContentService` and `ContentRepository` lack full CRUD and update operations for `KnowledgeAtom`, `contentStore.ts` does not manage questions or knowledge atoms, `contentService.ts` is missing atom update/delete calls, and `QuestionEditor.vue` only partially supports `multiple_choice` without proper UI or handling for `image_choice` and `numeric` item types.

**Approach:** Add Pydantic validation to `QuestionContent` schema to reject items lacking a valid correct answer key (HTTP 422/400 validation error). Extend `ContentRepository`, `ContentService`, and FastAPI endpoints (`content.py`) for complete tenant-filtered CRUD over Questions and Knowledge Atoms. Update Pinia `contentStore.ts` and `contentService.ts` frontend boundaries to manage questions and knowledge atoms, and enhance `QuestionEditor.vue` to support `multiple_choice`, `image_choice`, and `numeric` item types with proper validation.

## Boundaries & Constraints

**Always:**
- Ensure all DB queries for Questions and Knowledge Atoms in `ContentService` / `ContentRepository` apply active `organization_id` tenant filters.
- Reject question creation or update attempts if `correct_answer` is missing, empty, or invalid (HTTP 422/400).
- Restrict Question and Knowledge Atom mutation endpoints to users with expert/admin permissions (`get_current_expert_user`), returning 403 for non-experts.
- Maintain WCAG compliance and logical CSS tokens in `QuestionEditor.vue`.

**Block If:**
- Schema changes require breaking existing database migrations or column removals.

**Never:**
- Allow direct DB access in controllers bypassing `ContentService` or `ContentRepository`.
- Allow unauthenticated or non-expert users to create or modify assessment items or knowledge atoms.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Create Question (Valid) | Valid `QuestionCreate` with `correct_answer` present | 201 Created with question data | 400/422 Bad Request on validation error |
| Create Question (Missing Correct Answer) | `QuestionCreate` with empty or null `correct_answer` | Rejected validation error | 422 Unprocessable Entity / 400 Bad Request |
| Create Knowledge Atom (Expert) | Valid `KnowledgeAtomCreate` with expert token | 201 Created with atom data | 400 Bad Request on invalid type/competency |
| Non-Expert Question/Atom Mutation | Mutation payload with student/parent token | 403 Forbidden | HTTP 403 response |
| Update Knowledge Atom | Valid `KnowledgeAtomUpdate` payload | 200 OK with updated atom | 404 Not Found if atom_id invalid |
| Delete Question / Atom | Existing `question_id` or `atom_id` | 204 No Content | 404 Not Found if missing |

</intent-contract>

## Code Map

- `backend/app/schemas/content.py` -- Pydantic schemas for Question and KnowledgeAtom with validation
- `backend/app/repositories/content_repo.py` -- Data access repository for Question and KnowledgeAtom CRUD
- `backend/app/services/content_service.py` -- Business logic layer delegating Question/Atom operations to `ContentRepo`
- `backend/app/api/endpoints/content.py` -- FastAPI router exposing Question and KnowledgeAtom endpoints
- `frontend/src/services/contentService.ts` -- Axios API client for Question and KnowledgeAtom endpoints
- `frontend/src/stores/contentStore.ts` -- Pinia store for Question and KnowledgeAtom state management
- `frontend/src/components/expert/QuestionEditor.vue` -- Form component supporting `multiple_choice`, `image_choice`, and `numeric` item types
- `backend/tests/api/test_content.py` -- Integration tests for Question and KnowledgeAtom endpoints

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/schemas/content.py` -- Add model validator to `QuestionContent` requiring `correct_answer` -- Reject questions without correct answer key
- [x] `backend/app/repositories/content_repo.py` -- Add update and delete methods for `KnowledgeAtom` and `Question` with tenant scoping -- Complete DB repository layer
- [x] `backend/app/services/content_service.py` -- Delegate all Question and KnowledgeAtom CRUD to `ContentRepository` -- Maintain layered architecture
- [x] `backend/app/api/endpoints/content.py` -- Verify RBAC and endpoints for Question and KnowledgeAtom CRUD -- Ensure 403 for non-experts
- [x] `frontend/src/services/contentService.ts` -- Add missing `getKnowledgeAtom`, `updateKnowledgeAtom`, `deleteKnowledgeAtom` methods and update `QuestionContent` types -- Full API client coverage
- [x] `frontend/src/stores/contentStore.ts` -- Add state and actions for fetching, creating, updating, and deleting Questions and Knowledge Atoms -- Centralized store management
- [x] `frontend/src/components/expert/QuestionEditor.vue` -- Implement options and correct answer editing for `multiple_choice`, `image_choice`, and `numeric` types -- Complete item type authoring UI
- [x] `backend/tests/api/test_content.py` -- Add test cases for missing correct answer validation and KnowledgeAtom CRUD -- Verify backend behavior

**Acceptance Criteria:**
- Given `ContentService`, when creating a question, if `correct_answer` is missing or empty, then validation fails with HTTP 422/400.
- Given an expert user, when creating a knowledge atom with valid competency and `AUDIO_VISUAL`/`SIMULATION`/`MIND_MAP` type, then a 201 response is returned with tenant scoping.
- Given a student or parent user, when calling question/atom mutation endpoints, then HTTP 403 Forbidden is returned.
- Given `QuestionEditor.vue`, when selecting `multiple_choice`, `image_choice`, or `numeric`, then appropriate form inputs for options and correct answer selection render correctly.

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

- Question Content Schema: Added `@model_validator(mode="after")` to `QuestionContent` requiring `correct_answer` to be non-empty string for valid items.
- Item Types: Supported item types in frontend and backend are `multiple_choice`, `image_choice`, `numeric`, `text`, `interactive`.

## Verification

**Commands:**
- `pytest backend/tests/api/test_content.py` -- expected: All content API tests pass
- `cd frontend && npm run build` -- expected: TypeScript compilation and Vite build succeed

## Auto Run Result

### Summary
Successfully implemented Story 6.2 (Question-Bank & Knowledge Atom Management). Enforced backend validation on `QuestionContent` to reject items missing `correct_answer` with HTTP 422/400. Completed full tenant-scoped CRUD operations for `Question` and `KnowledgeAtom` across `ContentRepository`, `ContentService`, and FastAPI endpoints in `content.py`. Extended frontend API client `contentService.ts` and Pinia `contentStore.ts` to manage question and knowledge atom states. Enhanced `QuestionEditor.vue` component to support `multiple_choice`, `image_choice`, and `numeric` item types with option input and validation.

### Files Changed
- `backend/app/schemas/content.py`: Added `validate_correct_answer` model validator to `QuestionContent`.
- `backend/app/repositories/content_repo.py`: Added `update_question`, `delete_question`, `update_knowledge_atom`, `delete_knowledge_atom`.
- `backend/app/services/content_service.py`: Delegated all question and atom update/delete operations to `ContentRepository`.
- `frontend/src/services/contentService.ts`: Added `getKnowledgeAtom`, `updateKnowledgeAtom`, `deleteKnowledgeAtom`, and expanded `QuestionContent` item types.
- `frontend/src/stores/contentStore.ts`: Added `questions`, `knowledgeAtoms` state and complete CRUD actions.
- `frontend/src/components/expert/QuestionEditor.vue`: Updated form to handle `multiple_choice`, `image_choice`, and `numeric` item types with options and validation.
- `backend/tests/api/test_content.py`: Added integration tests for invalid question validation and KnowledgeAtom CRUD operations.
- `_bmad-output/implementation-artifacts/spec-6-2-question-bank-knowledge-atom-management.md`: Created and updated implementation spec artifact.

### Verification Performed
- `& "backend/venv/Scripts/pytest" backend/tests/api/test_content.py`: All 15 tests passed cleanly.
- `cd frontend && npm run build`: Vue 3 compiler + Vite production build succeeded cleanly with 0 type errors.

### Residual Risks
None.
