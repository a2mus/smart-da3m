---
title: 'Story 3.5: Spaced Re-Surfacing of Failed Items (FR-16)'
type: 'feature'
created: '2026-08-01'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
---

<intent-contract>

## Intent

**Problem:** Previously-failed diagnostic questions are not systematically re-surfaced over time, missing the opportunity for long-term memory retention and spaced learning transfer (FR-16).

**Approach:** Implement a SpacedRepetition model, interval calculation engine (default 1d -> 3d -> 7d), diagnostic repository methods, and integrate due review questions tagged with `is_review=True` into the adaptive QuestionSelector candidate pool.

## Boundaries & Constraints

**Always:** Tenant isolation (`organization_id`) must be strictly enforced on all spaced repetition records.

**Block If:** Human intervention outside repository is required (None required for this feature).

**Never:** Do not alter existing BKT probability formulas or break existing diagnostic session flows.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Failed Answer | Student answers question incorrectly | SpacedRepetition record created/updated with next_review_date = now + 1 day, interval_days = 1 | Handle duplicate gracefully |
| Due Review Selection | Next review date <= current time | QuestionSelector prioritizes or includes review items with is_review = True tag | Fall back to standard pool if empty |
| Correct Review Answer | Student answers review item correctly | Interval advances (1 -> 3 -> 7 -> int(7 * ease_factor)), next_review_date updated | No error expected |
| Incorrect Review Answer | Student answers review item incorrectly | Interval resets to 1 day, next_review_date set to now + 1 day | No error expected |

</intent-contract>

## Code Map

- `backend/app/models/spaced_repetition.py` -- SpacedRepetition SQLAlchemy model tracking question_id, student_id, next_review_date, interval_days, ease_factor
- `backend/app/models/__init__.py` -- Export SpacedRepetition model
- `backend/app/engines/spaced_repetition.py` -- Pure stateless spaced repetition interval engine
- `backend/app/repositories/diagnostic_repo.py` -- Repository DB access for spaced repetition records
- `backend/app/engines/diagnostic_engine.py` -- QuestionSelector candidate pool handling with is_review tagging
- `backend/tests/test_spaced_repetition.py` -- Comprehensive Pytest unit tests for spaced repetition logic and integration

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/models/spaced_repetition.py` -- Create SpacedRepetition model -- Data persistence for FR-16
- [x] `backend/app/models/__init__.py` -- Export SpacedRepetition model -- Package exposure
- [x] `backend/app/engines/spaced_repetition.py` -- Create spaced repetition calculation engine -- Pure domain logic for interval calculation
- [x] `backend/app/repositories/diagnostic_repo.py` -- Add repository methods for spaced repetition records -- DB operations with tenant isolation
- [x] `backend/app/engines/diagnostic_engine.py` -- Update QuestionSelector to support review item candidate scoring and is_review tagging -- Core loop integration
- [x] `backend/tests/test_spaced_repetition.py` -- Add test suite -- Test coverage for FR-16

**Acceptance Criteria:**
- Given a student failed an item during a diagnostic session, when processed, a SpacedRepetition record tracks question_id, student_id, next_review_date, interval_days, ease_factor
- Given due spaced repetition items exist, when next question selection occurs, due items are included in candidate pool and tagged as review items
- Given a correct answer on a re-surfaced item, the interval increases (1 -> 3 -> 7 -> interval * ease)
- Given an incorrect answer on a re-surfaced item, the interval resets to 1 day

## Spec Change Log

None.

## Review Triage Log

None.

## Verification

**Commands:**
- `pytest backend/tests/test_spaced_repetition.py` -- expected: All tests pass

## Auto Run Result

- **Status:** done
- **Summary:** Implemented Story 3.5 (FR-16) Spaced Re-Surfacing of Failed Items. Created the `SpacedRepetition` database model with multi-tenant isolation, pure stateless interval calculation engine (`SpacedRepetitionScheduler`), diagnostic repository methods, and integrated review item scoring and `is_review` candidate tagging in `QuestionSelector`. Added full Pytest test suite covering interval progression (1d -> 3d -> 7d -> interval * ease) and reset on failure.
- **Files Changed:**
  - `_bmad-output/implementation-artifacts/spec-3-5-spaced-re-surfacing-of-failed-items-fr-16.md` -- Spec file for Story 3.5
  - `backend/app/models/spaced_repetition.py` -- SQLAlchemy model for spaced repetition
  - `backend/app/models/__init__.py` -- Export SpacedRepetition model
  - `backend/app/engines/spaced_repetition.py` -- Pure stateless spaced repetition engine
  - `backend/app/repositories/diagnostic_repo.py` -- Repository DB operations for spaced repetition
  - `backend/app/engines/diagnostic_engine.py` -- Integrated candidate review selection and `is_review` tagging in QuestionSelector
  - `backend/tests/test_spaced_repetition.py` -- Unit tests for spaced repetition
- **Review Findings:** 0 patches needed, 0 deferred, 0 rejected.
- **Follow-up Review Recommended:** false
- **Verification Performed:** Executed `pytest backend/tests/test_spaced_repetition.py` (5/5 passed).
- **Residual Risks:** None.
