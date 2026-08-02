---
title: 'Story 9.3: Report Export (PDF/CSV) — Wire Orphaned Exporter'
type: 'feature'
created: '2026-08-03'
status: 'done'
baseline_revision: '8650778f14331c3d0f6a792a3240be24174633b4'
final_revision: 'd68eee58dd615e0af7c641d4da945e6bf15bbd8f'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-9-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** `ReportExporter` (`backend/app/services/report_exporter.py`) is an orphaned service that was instantiated directly inside `POST /api/v1/analytics/export` without tenant data isolation (`organization_id` filtering), bypassing `AnalyticsService`. Furthermore, `GET /api/v1/analytics/export` was not implemented, the frontend `analyticsService.ts` & `analyticsStore.ts` lacked export API bindings, and `CompetencyHeatmap.vue` lacked export action triggers.

**Approach:** Wire `ReportExporter` into `AnalyticsService`, enforce tenant isolation (`organization_id`) across all CSV and PDF export queries in `ReportExporter`, update `GET` and `POST` `/api/v1/analytics/export` endpoints to delegate to `AnalyticsService`, add `exportReport` API integration to `analyticsService.ts` and `analyticsStore.ts`, and add PDF/CSV export buttons to `CompetencyHeatmap.vue`.

## Boundaries & Constraints

**Always:** Strictly filter all student profiles and exports by the authenticated expert's `organization_id`. Ensure CSV exports contain stable, machine-parseable headers (`Student ID,Competency ID,Mastery Level,Probability Learned,Last Assessed`).

**Block If:** Any schema or API contract change requires breaking changes without backward compatibility.

**Never:** Bypass tenant isolation in `ReportExporter`. Never instantiate `ReportExporter` directly in endpoint functions without passing through `AnalyticsService`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH_CSV | `GET /api/v1/analytics/export?format=csv&report_type=heatmap` with valid expert auth token | `200 OK` or `FileResponse` with valid CSV containing tenant student data and headers | `400 Bad Request` if format or report_type invalid |
| HAPPY_PATH_PDF | `POST /api/v1/analytics/export` with `{ "format": "pdf", "report_type": "heatmap" }` | `200 OK` with `ExportResponse` containing valid PDF file path and generated timestamp | `500 Internal Server Error` if ReportLab fails |
| TENANT_ISOLATION | Expert from Org A requests export | Only students belonging to Org A are included in the generated CSV/PDF report | Exclude students from Org B in DB queries |
| INVALID_FORMAT | Request export with `format=xml` | `400 Bad Request` detail "Unsupported format: xml" | Return HTTP 400 |

</intent-contract>

## Code Map

- `backend/app/services/report_exporter.py` -- Implements CSV & PDF file generation with tenant isolation filtering.
- `backend/app/services/analytics_service.py` -- Business service method `export_report` coordinating tenant checks and `ReportExporter`.
- `backend/app/api/endpoints/analytics.py` -- `GET` and `POST` `/api/v1/analytics/export` endpoints delegating to `AnalyticsService`.
- `backend/app/schemas/analytics.py` -- `ExportRequest` and `ExportResponse` Pydantic schemas.
- `frontend/src/services/analyticsService.ts` -- Frontend API client method `exportReport`.
- `frontend/src/stores/analyticsStore.ts` -- Pinia store action `exportReport` triggering file download.
- `frontend/src/components/expert/CompetencyHeatmap.vue` -- UI component adding PDF and CSV export buttons.

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/services/report_exporter.py` -- Add `organization_id` filter to all CSV/PDF student and profile queries in `ReportExporter`.
- [x] `backend/app/services/analytics_service.py` -- Add `export_report` method to `AnalyticsService` delegating to `ReportExporter` with tenant isolation.
- [x] `backend/app/api/endpoints/analytics.py` -- Add `GET /api/v1/analytics/export` and update `POST /api/v1/analytics/export` to delegate to `AnalyticsService`.
- [x] `frontend/src/services/analyticsService.ts` -- Add `exportReport` method supporting CSV/PDF report downloads.
- [x] `frontend/src/stores/analyticsStore.ts` -- Add `exportReport` action to handle report generation and trigger client file downloads.
- [x] `frontend/src/components/expert/CompetencyHeatmap.vue` -- Add PDF and CSV export buttons in the toolbar.
- [x] `backend/tests/api/test_analytics_export.py` -- Add test suite for export endpoints and tenant isolation.

**Acceptance Criteria:**
- Given an authenticated expert, when calling `GET /api/v1/analytics/export?format=csv` or `POST /api/v1/analytics/export`, then request delegates through `AnalyticsService` to `ReportExporter`.
- Given an exported CSV report, then headers match `Student ID,Competency ID,Mastery Level,Probability Learned,Last Assessed` and data is isolated to the expert's organization.
- Given the frontend heatmap interface, when clicking Export PDF or Export CSV buttons, then export request is executed and file download is triggered.

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

## Design Notes

Report export functionality delegates through `AnalyticsService.export_report`, enforcing tenant context via `set_active_organization_id` and filtering database queries by `organization_id` (using `OrganizationMember` user associations). Endpoints support both `GET` (direct file download response) and `POST` (JSON response with file path). The frontend `CompetencyHeatmap.vue` provides UI triggers for PDF and CSV export via `analyticsStore.exportReport`.

## Verification

**Commands:**
- `pytest backend/tests/api/test_analytics_export.py backend/tests/api/test_analytics_auto_group.py` -- expected: 8 passed

## Auto Run Result

### Implementation Summary
- Enforced multi-tenant data isolation (`organization_id`) in `ReportExporter` (`backend/app/services/report_exporter.py`) for all CSV and PDF queries.
- Added `export_report` method to `AnalyticsService` (`backend/app/services/analytics_service.py`), establishing `AnalyticsService` -> `ReportExporter` layering.
- Added `GET /api/v1/analytics/export` (returning `FileResponse`) and updated `POST /api/v1/analytics/export` in `backend/app/api/endpoints/analytics.py`.
- Added `exportReport` method in `frontend/src/services/analyticsService.ts` and Pinia store action in `frontend/src/stores/analyticsStore.ts`.
- Added PDF and CSV export action buttons to `CompetencyHeatmap.vue` toolbar with i18n support (`t('analytics.exportPdf')`, `t('analytics.exportCsv')`).
- Added full unit and integration test suite in `backend/tests/api/test_analytics_export.py`.

### Changed Files
- `backend/app/services/report_exporter.py`: Added `organization_id` filtering and `OrganizationMember` join.
- `backend/app/services/analytics_service.py`: Implemented `export_report` coordination method.
- `backend/app/api/endpoints/analytics.py`: Added GET endpoint and updated POST endpoint to delegate to `AnalyticsService`.
- `frontend/src/services/analyticsService.ts`: Added `exportReport` API service method.
- `frontend/src/stores/analyticsStore.ts`: Added `exportReport` action with browser download trigger.
- `frontend/src/components/expert/CompetencyHeatmap.vue`: Added PDF and CSV export buttons to control toolbar.
- `backend/tests/api/test_analytics_export.py`: Added comprehensive unit and integration tests.

### Review Findings Breakdown
- Patches applied: 0
- Items deferred: 0
- Items rejected: 0

### Verification
- Executed `pytest backend/tests/api/test_analytics_export.py backend/tests/api/test_analytics_auto_group.py` -> 8 passed in 0.22s.
