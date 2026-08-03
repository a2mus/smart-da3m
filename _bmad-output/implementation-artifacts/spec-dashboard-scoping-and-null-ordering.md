---
title: 'Dashboard Scoping and Null Ordering'
type: 'refactor'
created: '2026-08-03'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: ['multiple-goals']
---

<intent-contract>

## Intent

**Problem:** `DashboardAggregator` instance-level `_daily_cache` is initialized per-request and discarded at the end of each HTTP request, rendering the transient daily recommendation cache ineffective across requests. Additionally, `get_latest_failed_competency` in `DashboardRepo` orders by `CompetencyProfile.last_assessed.desc()` without explicit `NULL` handling, which can cause unassessed competencies with `last_assessed IS NULL` to take precedence over evaluated ones in PostgreSQL.

**Approach:** Make `_daily_cache` a class-level dictionary on `DashboardAggregator` so cached recommendations persist across HTTP requests within the process runtime, and add explicit `.nulls_last()` to the `last_assessed.desc()` ordering in `get_latest_failed_competency`.

## Boundaries & Constraints

**Always:** Preserve all existing parameters, typing, and returned dictionary structures for `generate_daily_recommendation` and `get_latest_failed_competency`.

**Block If:** Any changes require database schema migrations or break existing public method signatures.

**Never:** Modify the deferred-work ledger directly (the orchestrator records resolution).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Cache Hit Across Requests | Subsequent HTTP request for same student on same UTC day | Returns cached recommendation from `DashboardAggregator._daily_cache` without re-querying | Fallback template on error |
| Null `last_assessed` Ordering | CompetencyProfile records with `last_assessed = None` alongside assessed ones | `get_latest_failed_competency` returns the record with the most recent timestamp first, putting NULLs last | Returns `None` if no matching record |

</intent-contract>

## Code Map

- `backend/app/services/dashboard_service.py` -- `DashboardAggregator` class-level `_daily_cache` definition and cache operations
- `backend/app/repositories/dashboard_repo.py` -- `get_latest_failed_competency` query explicit `nulls_last()` ordering

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/services/dashboard_service.py` -- Define `_daily_cache` as class attribute on `DashboardAggregator` and update cache checks to use class attribute -- DW-1: Persist transient cache across HTTP requests in process runtime
- [x] `backend/app/repositories/dashboard_repo.py` -- Add `.nulls_last()` to `CompetencyProfile.last_assessed.desc()` order clause in `get_latest_failed_competency` -- DW-2: Ensure NULL timestamps sort last in PostgreSQL

**Acceptance Criteria:**
- Given multiple requests for `generate_daily_recommendation` for a student on the same day, when called across distinct `DashboardAggregator` instances, then the cached recommendation from `DashboardAggregator._daily_cache` is returned.
- Given competency profiles with `NULL` and non-`NULL` `last_assessed` timestamps, when `get_latest_failed_competency` is executed, then the non-`NULL` assessed records are ordered ahead of `NULL` records.

## Spec Change Log

## Review Triage Log

### 2026-08-03 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 0
- defer: 0
- reject: 0
- addressed_findings:
  - none

## Auto Run Result

- **Status**: done
- **Followup Review Recommended**: false
- **Verification**: Verified class-level `_daily_cache` scoping and `clear_daily_cache()` in `DashboardAggregator` (`backend/app/services/dashboard_service.py`) and `.nulls_last()` ordering in `DashboardRepo.get_latest_failed_competency` (`backend/app/repositories/dashboard_repo.py`), along with unit test coverage in `backend/tests/unit/test_dashboard_service.py`.
- **Deferred Work Ledger Update**: 0 new deferred findings added. No existing deferred-work ledger entries modified or re-opened.

## Verification

**Commands:**
- `pytest backend/tests/unit/test_dashboard_service.py` -- expected: All unit tests pass
- `pytest backend/tests/` -- expected: All backend tests pass

