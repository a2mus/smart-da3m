---
title: 'Align MetricResponse and MetricsResponse schemas for mastery_speed and mastery_speed_days'
type: 'bugfix'
created: '2026-08-03'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
---

<intent-contract>

## Intent

**Problem:** Backend `MetricResponse` schema defines `mastery_speed` while frontend `MetricsResponse` interface had incomplete metrics fields (missing `mastery_speed` and `mastery_speed_days`), causing potential schema misalignment.

**Approach:** Harmonize backend `MetricResponse` Pydantic schema and frontend `MetricsResponse` TypeScript interface by ensuring both `mastery_speed` and `mastery_speed_days` are supported and aligned across API requests and responses.

## Boundaries & Constraints

**Always:** Maintain full backward compatibility for `mastery_speed` on backend and frontend while populating `mastery_speed_days` as an alias field in `MetricResponse`.

**Block If:** Backend or frontend tests fail due to unexpected field removals.

**Never:** Modify unrelated endpoints or break existing analytics store functionality.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| GET /analytics/metrics | Expert user requests metrics | Returns `MetricResponse` with both `mastery_speed` and `mastery_speed_days` | 401/403 for unauthorized users |

</intent-contract>

## Code Map

- `backend/app/schemas/analytics.py` -- `MetricResponse` schema definition with `mastery_speed` and `mastery_speed_days`
- `backend/app/api/endpoints/analytics.py` -- Endpoint returning `MetricResponse` with `mastery_speed_days` populated
- `frontend/src/services/analyticsService.ts` -- `MetricsResponse` interface with `mastery_speed` and `mastery_speed_days`
- `backend/tests/api/test_rbac_analytics.py` -- Test coverage for `/analytics/metrics` endpoint fields

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/schemas/analytics.py` -- Add `mastery_speed_days: Optional[float] = None` to `MetricResponse` -- Ensures schema contains `mastery_speed_days`
- [x] `backend/app/api/endpoints/analytics.py` -- Include `mastery_speed_days=mastery_speed` in `MetricResponse` instantiation -- Populates alias field in API responses
- [x] `frontend/src/services/analyticsService.ts` -- Update `MetricsResponse` interface to include `mastery_speed?: number` and `mastery_speed_days?: number` along with other backend metric fields -- Harmonizes frontend types with backend
- [x] `backend/tests/api/test_rbac_analytics.py` -- Add assertion verifying `mastery_speed` and `mastery_speed_days` in `/analytics/metrics` response -- Guarantees response field integrity

**Acceptance Criteria:**
- Given an authenticated expert user, when requesting `GET /analytics/metrics`, then the response JSON contains both `mastery_speed` and `mastery_speed_days` as float numbers.
- Given the frontend `analyticsService.ts`, when importing `MetricsResponse`, then TypeScript compiles without type errors for both `mastery_speed` and `mastery_speed_days`.

## Spec Change Log

## Review Triage Log

### 2026-08-03 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 0
- defer: 3: (high 0, medium 2, low 1)
- reject: 2
- addressed_findings:
  - none

## Verification

**Commands:**
- `python -m pytest tests/api/test_rbac_analytics.py` -- expected: PASS (all tests green)

## Auto Run Result

Status: done

_Appended by the bmad-loop orchestrator (missing-marker repair, #224): the session finalized this spec's frontmatter without its `## Auto Run Result` marker, so the orchestrator synthesized the result from the frontmatter and appended this section._

Synthesized by the bmad-loop orchestrator from frontmatter status `done` for story `dw-dw-metrics-response-field-alignment` (session finalized the spec without appending its marker).
