---
title: 'Story 2.3: Wire Diagnostic Endpoint to Engine — Kill Hardcoded Mastery'
type: 'refactor'
created: '2026-08-01'
status: 'done'
baseline_revision: 'aab7776b3ed48afb0e7aa69f783bd6c3d13ff19d'
final_revision: '3daeba1811ccce9c3b3863582c9c032548c941e9'
review_loop_iteration: 0
followup_review_recommended: false
context: ['backend/app/api/endpoints/diagnostic.py', 'backend/app/engines/diagnostic_engine.py', 'backend/app/engines/bkt.py', 'backend/app/repositories/diagnostic_repo.py', 'backend/app/repositories/content_repo.py']
warnings: []
---

<intent-contract>

## Intent

**Problem:** `POST /api/v1/diagnostic/answer` currently hardcodes `current_mastery=0.5` and `mastery_level="FAMILIAR"`, uses inline/hardcoded error classification (`ErrorClassification.PROCESS`), selects next questions via simple list traversal ignoring student mastery, and bypasses stateless BKT updates and competency profile persistence.

**Approach:** Wire the diagnostic endpoint to the stateless `DiagnosticEngine` and `bkt` modules, reading student competency profiles from `DiagnosticRepository`, updating mastery via `bkt.update_mastery`, classifying errors using `ErrorClassifier`, selecting next questions via `QuestionSelector` with real mastery, and persisting updated competency profiles back to the database.

## Boundaries & Constraints

**Always:** All DB access must go through `DiagnosticRepository` and `ContentRepository`. Diagnostic domain calculations (mastery update, error classification, question selection, session evaluation) must use stateless engine classes in `backend/app/engines/`. Competency profile updates must be persisted to `competency_profiles` DB table upon each answer.

**Block If:** Any in-memory session or mastery dictionary state is reintroduced into engines or endpoints.

**Never:** Use hardcoded `0.5` mastery or hardcoded `"FAMILIAR"` string in answer responses or next-question selection.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Correct Answer | Student submits correct answer | BKT increases `p_learned`, `error_classification` is `NONE`, updated `CompetencyProfile` saved to DB, next question targeted to new mastery level | Validates session & question existence |
| Incorrect Answer | Student submits incorrect answer with response time | BKT decreases/updates `p_learned`, `error_classification` classified statelessly (e.g. `PROCESS`/`INCIDENTAL`), updated profile saved to DB | Validates session & question existence |
| First Answer for Competency | No prior `CompetencyProfile` exists | Default initial prior `p_learned=0.5` used, updated via BKT, new `CompetencyProfile` created in DB | Handles missing profile gracefully by creating default |
| Session Completion | 10th answer or mastery threshold reached | Session status updated to `COMPLETED`, `recommended_group` assigned via `RemediationGroup` assigner, final results returned | Returns 400 if session already completed |

</intent-contract>

## Code Map

- `backend/app/api/endpoints/diagnostic.py` -- Refactored diagnostic endpoint using `DiagnosticEngine` and `DiagnosticRepository`
- `backend/app/engines/diagnostic_engine.py` -- Stateless diagnostic engine, error classification, and question selection
- `backend/app/engines/bkt.py` -- BKT pure functions (`update_mastery`, `get_mastery_level`)
- `backend/app/repositories/diagnostic_repo.py` -- Repository for session, answer, and competency profile persistence
- `backend/app/repositories/content_repo.py` -- Repository for question and module lookup
- `backend/tests/test_diagnostic_endpoint.py` -- Tests verifying engine integration, BKT updates, error classification, and real mastery progression

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/api/endpoints/diagnostic.py` -- Wire `/answer` and `/results/{session_id}` to `DiagnosticEngine` and `bkt` modules -- Replace hardcoded 0.5 mastery, hardcoded error classification, and naive question selection with stateless engine logic and DB profile updates
- [x] `backend/tests/test_diagnostic_endpoint.py` -- Add/update diagnostic endpoint tests -- Verify BKT mastery updates, error classification, adaptive next question selection, and competency profile DB persistence

**Acceptance Criteria:**
- Given `POST /api/v1/diagnostic/answer` currently returns hardcoded `0.5` mastery
- When a student submits an answer to `/api/v1/diagnostic/answer`
- Then `DiagnosticRepository.get_competency_profile` retrieves the student's current `p_learned` for the question's competency
- And `DiagnosticEngine.process_answer` / `update_mastery` calculates the new `p_learned` and `error_classification`
- And `DiagnosticRepository.update_or_create_competency_profile` persists the new `p_learned` and `mastery_level` to `CompetencyProfile`
- And `QuestionSelector.select_next_question` chooses the next question based on student's actual updated mastery
- And `/results/{session_id}` evaluates final session metrics using `DiagnosticEngine.evaluate_session_results`
- And no hardcoded mastery values (0.5) remain in `backend/app/api/endpoints/diagnostic.py`
- And all diagnostic unit and integration tests pass

## Verification

**Commands:**
- `pytest backend/tests/test_diagnostic_endpoint.py backend/tests/test_engines.py backend/tests/test_repositories.py` -- expected: all tests pass

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
Refactored `backend/app/api/endpoints/diagnostic.py` to eliminate hardcoded mastery (`0.5`), hardcoded mastery levels (`"FAMILIAR"`), and inline error classification (`ErrorClassification.PROCESS`). The endpoint now retrieves student competency profiles from `DiagnosticRepository`, delegates BKT updates, error classification, question selection, and session evaluation to the stateless `DiagnosticEngine`, persists updated `p_learned` and `mastery_level` back to `CompetencyProfile` in the database, and evaluates session results statelessly. Added unit tests in `backend/tests/test_diagnostic_endpoint.py`.

### Files Changed
- `backend/app/api/endpoints/diagnostic.py`: Refactored `/start`, `/answer`, and `/results/{session_id}` endpoints to integrate `DiagnosticEngine`, `bkt`, `DiagnosticRepository`, and `ContentRepository`.
- `backend/tests/test_diagnostic_endpoint.py`: Created unit tests verifying starting sessions, submitting answers with real BKT mastery updates, persisting profiles, and session evaluation.
- `_bmad-output/implementation-artifacts/spec-2-3-wire-diagnostic-endpoint-to-engine-kill-hardcoded-mastery.md`: Specification tracking story execution, verification, and review results.

### Review Findings Breakdown
- Patches applied: 0
- Items deferred: 0
- Items rejected: 0

### Follow-up Review Recommendation
`false`

### Verification Performed
- Executed `pytest tests/test_diagnostic_endpoint.py tests/test_engines.py tests/test_repositories.py` in `backend`: 17 passed out of 17 tests.

### Residual Risks
None.
