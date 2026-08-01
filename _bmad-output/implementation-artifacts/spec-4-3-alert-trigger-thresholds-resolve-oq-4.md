---
title: 'Story 4.3: Alert Trigger Thresholds (Resolve OQ-4)'
type: 'feature'
created: '2026-08-01'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: false
context: ['backend/app/core/config.py', 'backend/app/services/alert_manager.py', 'backend/app/models/alert.py']
warnings: []
---

<intent-contract>

## Intent

**Problem:** Alert trigger thresholds and severity mappings (OQ-4) are hardcoded or partially incomplete in `AlertManager`. The system needs configurable thresholds for raising INFO, WARNING, and CRITICAL pedagogical alerts based on failure frequency within a 7-day window, passport failures, and abandonment, alongside duplicate-prevention with a configurable cooldown window.

**Approach:** Make alert thresholds configurable in `backend/app/core/config.py` (Settings). Refactor `AlertManager` and its detectors/generators to evaluate failure history over a 7-day window against configurable thresholds (INFO on 1st fail, WARNING on 2+ fails or 1 passport fail, CRITICAL on 3+ fails or 2 passport fails or abandonment). Implement a duplicate-prevention cooldown window mechanism using configurable settings.

## Boundaries & Constraints

**Always:** Thresholds must be configurable via `Settings` in `app/core/config.py` rather than hardcoded; duplicate prevention must prevent re-raising the same alert within the cooldown window; severity mapping must adhere strictly to OQ-4 spec rules; tenant isolation (`organization_id`) must be preserved.

**Block If:** Required actions only a human can perform outside the repository (vendor console, domain purchase, etc.).

**Never:** Never hardcode failure thresholds or cooldown windows in service files; never bypass duplicate prevention; never raise unhandled exceptions during alert evaluation.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| FIRST_FAILURE_INFO | Student fails a competency exercise for 1st time | Generates INFO severity alert | Log and handle gracefully |
| REPEATED_FAILURE_WARNING | Student fails same competency 2 times within 7 days | Generates WARNING severity alert | Log and handle gracefully |
| REPEATED_FAILURE_CRITICAL | Student fails same competency 3+ times within 7 days | Generates CRITICAL severity alert | Log and handle gracefully |
| PASSPORT_FAIL_WARNING | Student fails passport assessment 1st time | Generates WARNING severity alert | Log and handle gracefully |
| PASSPORT_FAIL_CRITICAL | Student fails passport assessment 2nd time on same competency | Generates CRITICAL severity alert | Log and handle gracefully |
| COOLDOWN_DUPLICATE_PREVENT | Alert triggered within cooldown window of previous identical alert | Alert generation suppressed (returns None) | Return None without error |

</intent-contract>

## Code Map

- `backend/app/core/config.py` -- Add configurable alert settings (thresholds, window days, cooldown hours)
- `backend/app/services/alert_manager.py` -- Implement configurable threshold evaluation, 7-day window failure history checks, passport failure counter, and cooldown duplicate prevention
- `backend/app/models/alert.py` -- Verify severity & trigger types
- `backend/tests/services/test_alert_thresholds.py` -- Comprehensive test suite for configurable trigger thresholds and cooldown duplicate prevention

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/core/config.py` -- Add alert threshold & cooldown settings -- Enables environment configurable thresholds
- [x] `backend/app/services/alert_manager.py` -- Update detectors & generator to use configurable thresholds and cooldown window -- Evaluates INFO/WARNING/CRITICAL rules and suppresses duplicates within cooldown
- [x] `backend/tests/services/test_alert_thresholds.py` -- Unit tests for threshold evaluation and duplicate prevention -- Validates all OQ-4 rules

**Acceptance Criteria:**
- Given configurable alert settings in `config.py`, when alert detectors run, then they read thresholds from settings.
- Given a 1st failure on a competency, when evaluated, then an INFO severity alert is generated.
- Given 2 failures on the same competency within 7 days, or 1 passport failure, then a WARNING severity alert is generated.
- Given 3+ failures on the same competency within 7 days, or 2 passport failures on the same competency, or session abandonment, then a CRITICAL severity alert is generated.
- Given an alert raised within the cooldown window for the same student & trigger, then duplicate alert generation is suppressed.

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

**Status:** done

**Summary:**
Implemented configurable alert trigger thresholds and duplicate prevention for Story 4.3 (OQ-4). Updated `app/core/config.py` Settings with configurable thresholds (`ALERT_WARNING_FAILURE_THRESHOLD`, `ALERT_CRITICAL_FAILURE_THRESHOLD`, `ALERT_FAILURE_WINDOW_DAYS`, `ALERT_CRITICAL_PASSPORT_FAILS`, `ALERT_COOLDOWN_HOURS`). Refactored `ConsecutiveFailureDetector`, `ResponsePatternDetector`, `AlertGenerator`, and `AlertManager` to evaluate 7-day window failure counts, passport failure counts, session abandonment, and duplicate-prevention within the cooldown window. Created comprehensive unit test suite `tests/services/test_alert_thresholds.py`.

**Files Changed:**
- `backend/app/core/config.py`: Added alert threshold settings
- `backend/app/services/alert_manager.py`: Implemented OQ-4 threshold evaluation, 7-day window checks, passport fail counts, abandonment critical severity, and cooldown duplicate prevention
- `backend/tests/services/test_alert_thresholds.py`: Added unit tests for threshold rules and cooldown duplicate prevention
- `backend/tests/services/test_alert_manager.py`: Updated test suite to align with OQ-4 threshold severity rules

**Review Findings:**
- Patches applied: 0
- Items deferred: 0
- Items rejected: 0
- Follow-up review recommendation: false

**Verification Performed:**
- `pytest tests/services/test_alert_thresholds.py tests/services/test_alert_manager.py` -> 23/23 passed

## Verification

**Commands:**
- `pytest tests/services/test_alert_thresholds.py` -- expected: All threshold & cooldown tests pass
- `ruff check app/core/config.py app/services/alert_manager.py` -- expected: 0 errors
