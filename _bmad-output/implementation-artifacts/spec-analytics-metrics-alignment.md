---
title: 'Align platform metrics backend response values, frontend TypeScript interfaces, and API test coverage'
type: 'bugfix'
created: '2026-08-04'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
---

<intent-contract>

## Intent

Align platform metrics backend response values, frontend TypeScript interfaces, and API test coverage. Update `get_platform_metrics` empty profiles path to include `mastery_speed_days=0.0`, remove legacy unreturned properties `overall_mastery_rate` and `at_risk_students_count` from `MetricsResponse`, add runtime fallback handling for `total_assessments`, and add an HTTP endpoint test asserting `mastery_speed_days` in the JSON response.

## Ledger Entries

- DW-14: Analytics endpoint get_platform_metrics empty profiles path returns mastery_speed_days as null while populated profiles path returns float.
- DW-15: Frontend MetricsResponse interface retains legacy fields overall_mastery_rate and at_risk_students_count not returned by backend MetricResponse schema.
- DW-16: Lack of HTTP integration test for mastery_speed_days response field on GET /analytics/metrics endpoint.
- DW-17: Frontend MetricsResponse total_assessments field required contract lacks runtime fallback guard if backend payload omits field.

</intent-contract>

## Code Map

- `backend/app/api/endpoints/analytics.py` -- Endpoint initialization of `MetricResponse` in empty profile path
- `frontend/src/services/analyticsService.ts` -- `MetricsResponse` interface and `getMetrics()` runtime fallback
- `backend/tests/api/test_rbac_analytics.py` -- HTTP integration test asserting `mastery_speed_days` payload

## Tasks & Acceptance

- [x] `backend/app/api/endpoints/analytics.py` -- Update `get_platform_metrics` empty profiles path to include `mastery_speed_days=0.0`
- [x] `frontend/src/services/analyticsService.ts` -- Remove `overall_mastery_rate` and `at_risk_students_count` from `MetricsResponse`
- [x] `frontend/src/services/analyticsService.ts` -- Add runtime fallback `total_assessments: response.data?.total_assessments ?? 0` in `getMetrics()`
- [x] `backend/tests/api/test_rbac_analytics.py` -- Add `test_get_platform_metrics_http_response_mastery_speed_days` HTTP test

## Verification

- `pytest backend/tests/api/test_rbac_analytics.py` -- 6 passed in 0.18s

## Review Triage Log

### 2026-08-04 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 0
- defer: 0
- reject: 0
- addressed_findings:
  - none

## Auto Run Result

Status: done
Summary: Successfully aligned backend platform metrics empty profile responses, cleaned frontend TypeScript interface contracts, added runtime fallback guards, and added HTTP integration test assertion for mastery_speed_days.

Files Changed:
- `backend/app/api/endpoints/analytics.py`: Added default `mastery_speed_days=0.0` in empty profile path.
- `frontend/src/services/analyticsService.ts`: Removed obsolete `overall_mastery_rate` and `at_risk_students_count` fields from `MetricsResponse` interface, added `total_assessments` fallback guard.
- `backend/tests/api/test_rbac_analytics.py`: Added `test_get_platform_metrics_http_response_mastery_speed_days` integration test.

Review Findings Breakdown:
- Patches Applied: 0
- Items Deferred: 0
- Items Rejected: 0

Follow-up Review Recommended: false
Verification: 6 passed in `pytest tests/api/test_rbac_analytics.py` (0.18s)


