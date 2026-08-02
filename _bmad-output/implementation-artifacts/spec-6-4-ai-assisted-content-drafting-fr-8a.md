---
title: 'Story 6.4: AI-Assisted Content Drafting (FR-8a)'
type: 'feature'
created: '2026-08-02'
status: 'in-progress'
baseline_revision: '1ea96ba119131eb5127cae99480eb88c4fefae6f'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-6-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** The platform lacks an AI-assisted authoring endpoint and workflow for pedagogical experts, requiring all curriculum modules, questions, and knowledge atoms to be drafted manually without LLM acceleration, prompt guardrails, or version diffing before publication.

**Approach:** Implement `POST /api/v1/content/ai-draft` in `backend/app/api/endpoints/content.py` requiring expert role authorization, accepting `{subject, year_band, competency, curriculum_reference}` and enqueuing a Celery task. Create a Celery task `draft_content_with_ai` in `backend/app/tasks/ai_draft.py` that invokes LiteLLM with strict prompt guardrails (Algerian curriculum alignment, no hallucinated competencies, bilingual AR/FR support per OQ-9). Persist generated items in `DRAFT` status assigned to the user's `organization_id`. Add task status endpoint `GET /api/v1/content/ai-draft/status/{task_id}`. Update `frontend/src/services/contentService.ts` and `frontend/src/views/ModuleEditor.vue` to allow experts to request AI drafts, monitor completion, view diffs between AI-drafted and edited versions, and publish or discard drafts.

## Boundaries & Constraints

**Always:**
- Mark all AI-drafted items with `DRAFT` status upon creation (never auto-publish).
- Scope all generated content to `current_user.organization_id`.
- Require EXPERT or ADMIN role for accessing AI drafting endpoints (reject non-experts with HTTP 403 Forbidden).
- Enforce system prompt guardrails: align with Algerian curriculum standards, forbid hallucinated competencies, and support bilingual AR/FR content generation.
- Provide diff visibility in the expert editor UI comparing original AI draft content against modified versions before publication.

**Block If:**
- Core schema modifications require breaking existing database tables or relationships.

**Never:**
- Auto-publish content without explicit expert review and status transition to `PUBLISHED`.
- Allow non-expert roles (STUDENT, PARENT) to trigger AI drafting endpoints.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Enqueue AI Draft | Expert user, `{subject: "MATH", year_band: "Y4-5", competency: "COMP-01", curriculum_reference: "Text..."}` | 202 Accepted, `{task_id: "...", status: "PENDING"}` | Return 422 if required fields missing |
| Task Completion | Celery worker executes `draft_content_with_ai` using LiteLLM | Draft module and questions created in DB with `DRAFT` status and user `organization_id` | If LiteLLM fails, set task state to FAILED, log error, leave existing DB unaffected |
| Unauthorized Request | Request with Student/Parent token | 403 Forbidden | HTTP 403 Forbidden |
| Polling Task Status | Valid `task_id` for completed task | 200 OK, `{status: "SUCCESS", result: {module_id: "...", draft_count: 5}}` | Return 404 if invalid `task_id` |
| Editorial Diff View | Expert opens AI-drafted module in `ModuleEditor.vue` | UI displays original AI draft values alongside current edited values | Fallback to current values if no prior draft history exists |

</intent-contract>

## Code Map

- `backend/app/schemas/content.py` -- Add `AIDraftRequest`, `AIDraftTaskResponse`, and `AIDraftResult` Pydantic models.
- `backend/app/tasks/ai_draft.py` -- Implement `draft_content_with_ai` Celery task calling LiteLLM with Algerian curriculum guardrails and persisting `DRAFT` items.
- `backend/app/services/content_service.py` -- Add `trigger_ai_draft` method to dispatch Celery task and store draft content in DB via `ContentRepo`.
- `backend/app/api/endpoints/content.py` -- Expose `POST /api/v1/content/ai-draft` and `GET /api/v1/content/ai-draft/status/{task_id}` endpoints with expert RBAC.
- `frontend/src/services/contentService.ts` -- Add `requestAIDraft` and `getAIDraftStatus` API client methods.
- `frontend/src/components/AIDraftModal.vue` -- Create modal component for inputting curriculum reference, selecting target competency, and initiating AI draft.
- `frontend/src/views/ModuleEditor.vue` -- Integrate AI draft triggering, polling, diff view component, and publish/discard controls.
- `backend/tests/test_ai_content_drafting.py` -- Integration and unit tests for AI content drafting endpoints, task enqueuing, and RBAC rules.

## Tasks & Acceptance

**Execution:**
- [ ] `backend/app/schemas/content.py` -- Add `AIDraftRequest`, `AIDraftTaskResponse`, `AIDraftResult` schemas -- model AI draft request parameters and task responses.
- [ ] `backend/app/tasks/ai_draft.py` -- Implement `draft_content_with_ai` Celery task -- invoke LiteLLM with Algerian curriculum guardrails, parse generated questions/atoms, store with `DRAFT` status.
- [ ] `backend/app/services/content_service.py` -- Add AI draft orchestration logic in `ContentService` -- dispatch task and manage draft item persistence.
- [ ] `backend/app/api/endpoints/content.py` -- Add `POST /api/v1/content/ai-draft` and `GET /api/v1/content/ai-draft/status/{task_id}` endpoints -- enforce expert authorization.
- [ ] `frontend/src/services/contentService.ts` -- Add `requestAIDraft` and `getAIDraftStatus` methods -- handle API communication with backend.
- [ ] `frontend/src/components/AIDraftModal.vue` -- Build modal component -- allow experts to submit curriculum references and competencies.
- [ ] `frontend/src/views/ModuleEditor.vue` -- Add AI draft trigger, status polling, diff view comparison between AI draft and edited content, and publish/discard actions -- complete expert review interface.
- [ ] `backend/tests/test_ai_content_drafting.py` -- Create Pytest test suite -- verify API endpoints, task enqueuing, and RBAC permissions.

**Acceptance Criteria:**
- Given FR-8a is requested, when `POST /api/v1/content/ai-draft` accepts `{subject, year_band, competency, curriculum_reference}`, a Celery task is enqueued that calls LiteLLM using prompt guardrails (aligning with Algerian curriculum, avoiding hallucinated competencies, supporting bilingual AR/FR per OQ-9), all generated content is saved with `DRAFT` status (never auto-published), and the expert can view a diff between AI-drafted and edited versions before publishing or discarding.

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `pytest backend/tests/test_ai_content_drafting.py` -- expected: all tests pass
- `pytest backend/tests/api/test_content.py` -- expected: 15 passed
