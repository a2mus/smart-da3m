---
title: 'Story 3.2: Celery Tasks Infrastructure & LiteLLM Integration'
type: 'feature'
created: '2026-08-01'
status: 'awaiting-operator'
baseline_revision: '5f94588e9fec2573e004f3fd78c4d8535f874a7c'
final_revision: '87d4f7ce4b8e69574d797fc58ae7adbc15632cdf'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-3-context.md']
warnings: []
operator_actions:
  - "Configure production LLM_API_KEY and LLM_BASE_URL environment variables in the deployment console for LiteLLM provider access."
---

<intent-contract>

## Intent

**Problem:** Currently, Celery is configured in `backend/app/core/celery.py` with an incorrect `include` list (`app.services.alert_manager` instead of `app.tasks`), no Celery tasks exist for remediation pathway generation, and `litellm` is not installed or configured. This violates AD-3 (hybrid AI generation via async Celery + LiteLLM pipeline).

**Approach:** Add `litellm` to `backend/requirements.txt` and configure LLM settings (`LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`) in `backend/app/core/config.py`. Update Celery worker configuration to load `app.tasks`. Create `backend/app/tasks/__init__.py` and `backend/app/tasks/ai_proposal.py` defining `@celery_app.task generate_remediation_proposal`. The task reads diagnostic gap profile, runs `engines/remediation_engine.py` deterministic selection, calls `litellm.completion` for LLM augmentation with a clean fallback to deterministic-only if LiteLLM is unavailable or fails, persists the proposal, and transitions the path status to `PROPOSED`.

## Boundaries & Constraints

**Always:** Run LLM calls asynchronously inside Celery tasks (never synchronously in the API request path). Fall back gracefully to deterministic pathway selection if LiteLLM fails or is unconfigured. Enforce multi-tenant and zero PII logging constraints when sending prompts to LLM. Update Celery `include` configuration to `app.tasks`.

**Block If:** Operator/human actions outside the repo are strictly required for external vendor consoles or API keys (handle per operator protocol if applicable).

**Never:** Block synchronous API requests on LiteLLM API network calls. Expose student PII (names, emails) to external LLM providers.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| LiteLLM Available & Successful | Valid diagnostic result, active LiteLLM configuration | Deterministic selection + LLM pedagogical augmentation generated, path stored/updated, status transitioned to `PROPOSED` | No error expected |
| LiteLLM Unavailable / Exception | Valid diagnostic result, LiteLLM raises timeout/API error | Fallback to deterministic selection alone, path stored/updated, status transitioned to `PROPOSED` | Exception caught, warning logged, proposal proceeds deterministically |
| Celery Task Dispatch | Diagnostic session completed | Task `generate_remediation_proposal.delay(...)` enqueued asynchronously | Standard Celery task enqueue |

</intent-contract>

## Code Map

- `backend/requirements.txt` -- Add `litellm>=1.50.0` dependency
- `backend/app/core/config.py` -- Add `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` settings with defaults
- `backend/app/core/celery.py` -- Update `celery_app` `include` configuration to `["app.tasks"]`
- `backend/app/tasks/__init__.py` -- Package init exposing Celery tasks
- `backend/app/tasks/ai_proposal.py` -- Define `@celery_app.task generate_remediation_proposal` logic with LiteLLM augmentation & deterministic fallback
- `backend/app/services/remediation_service.py` -- Integrate task dispatch or proposal persistence helper methods if needed
- `backend/tests/test_ai_proposal_task.py` -- Test suite for Celery AI proposal task and LiteLLM fallback logic

## Tasks & Acceptance

**Execution:**
- [x] `backend/requirements.txt` -- Add `litellm` package requirement.
- [x] `backend/app/core/config.py` -- Add LLM configuration fields (`LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`).
- [x] `backend/app/core/celery.py` -- Change Celery worker include list from `app.services.alert_manager` to `app.tasks`.
- [x] `backend/app/tasks/__init__.py` & `backend/app/tasks/ai_proposal.py` -- Implement async `generate_remediation_proposal` Celery task with deterministic baseline + LiteLLM augmentation and exception fallback.
- [x] `backend/tests/test_ai_proposal_task.py` -- Add unit tests for `generate_remediation_proposal` task covering both LiteLLM success and fallback paths.

**Acceptance Criteria:**
- Given Celery is configured, when Celery worker starts, then `app.tasks` module is included and tasks are registered.
- Given a diagnostic gap profile, when `generate_remediation_proposal` runs, then deterministic atoms are selected via `engines/remediation_engine.py`.
- Given `LLM_MODEL` is set, when `litellm.completion` is called, then the proposal is augmented with pedagogical justification and stored with status `PROPOSED`.
- Given `litellm` fails or is unreachable, when `generate_remediation_proposal` runs, then it falls back to the deterministic proposal without raising unhandled exceptions and transitions status to `PROPOSED`.

## Design Notes

- **Hybrid AI Generation Pattern (AD-3):**
  1. Primary selection: `PathwayGenerator().generate(competency_id, student_group, available_atoms)` yields a baseline atom list.
  2. LLM Augmentation: Prompt sent to LiteLLM includes only competency IDs, gaps, and anonymized atom IDs (no student PII).
  3. Fallback: Wrap `litellm.completion` in a `try...except Exception` block. On exception, log a warning and return the baseline deterministic proposal.

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

### Summary
Successfully created the Celery background task infrastructure and LiteLLM integration for async AI proposal generation (AD-3).

### Files Changed
- `backend/requirements.txt` -- Added `litellm>=1.50.0` requirement
- `backend/app/core/config.py` -- Added `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` settings
- `backend/app/core/celery.py` -- Updated worker include list to `app.tasks`
- `backend/app/tasks/__init__.py` -- Task package initialization
- `backend/app/tasks/ai_proposal.py` -- Implemented `@celery_app.task generate_remediation_proposal` with LiteLLM augmentation and deterministic fallback
- `backend/tests/test_ai_proposal_task.py` -- Added unit test suite covering success and fallback paths

### Review Findings Breakdown
- Patches applied: 0
- Items deferred: 0
- Items rejected: 0

### Verification Performed
- `pytest tests/test_ai_proposal_task.py` passed 3/3 tests (100% pass rate).

## Verification

**Commands:**
- `cd backend && pytest tests/test_ai_proposal_task.py` -- expected: All task & LiteLLM fallback unit tests pass
