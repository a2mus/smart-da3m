---
title: 'Story 9.4: Printable Remediation Cards'
type: 'feature'
created: '2026-08-03'
status: 'ready-for-dev'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-9-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** Pedagogical experts need to print offline remediation cards per student or per remediation group to use directly in the classroom. Currently, no `GET /api/v1/analytics/remediation-cards` endpoint exists, schemas/services for remediation card generation are missing, and the analytics UI lacks a printable remediation card view with CSS `@media print` rules.

**Approach:** Implement `GET /api/v1/analytics/remediation-cards` endpoint supporting `student_id` and `group_id` query parameters in `backend/app/api/endpoints/analytics.py`, backed by `AnalyticsService.get_remediation_cards` and `AnalyticsRepo`. Add frontend remediation card service/store methods, create a print-formatted `RemediationCardPrintView.vue` component with page-break-friendly CSS and hidden interactive controls during print, and add "Print Cards" action buttons in the analytics interface (`CompetencyHeatmap.vue`).

## Boundaries & Constraints

**Always:** Strictly filter all student data, failed competencies, and recommended atoms by the authenticated expert's `organization_id`. Ensure print styles (`@media print`) hide navigation controls and format pages cleanly for printing.

**Block If:** Any schema or API contract change breaks backward compatibility.

**Never:** Expose student records across organization boundaries.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH_SINGLE | `GET /api/v1/analytics/remediation-cards?student_id={id}` with valid expert auth | `200 OK` with `RemediationCardsResponse` containing 1 card with student name, failed competencies, recommended atoms, and error classifications | `404 Not Found` if student not found in tenant |
| HAPPY_PATH_GROUP | `GET /api/v1/analytics/remediation-cards?group_id={id}` with valid expert auth | `200 OK` with `RemediationCardsResponse` containing cards for all students in the specified group | `404 Not Found` if group not found |
| MISSING_PARAMS | `GET /api/v1/analytics/remediation-cards` without `student_id` or `group_id` | `400 Bad Request` detail "Either student_id or group_id must be provided" | Return HTTP 400 |
| PRINT_VIEW | User clicks "Print Cards" in UI | Opens printable cards view/modal and triggers `window.print()` with `@media print` CSS rules | Handle empty card data gracefully |

</intent-contract>

## Code Map

- `backend/app/schemas/analytics.py` -- Define `RemediationCardItem`, `RemediationCardData`, and `RemediationCardsResponse` Pydantic schemas.
- `backend/app/repositories/analytics_repo.py` -- DB query methods to fetch student failed competencies, error classifications, and recommended atoms.
- `backend/app/services/analytics_service.py` -- Business logic method `get_remediation_cards` returning formatted card data with tenant isolation.
- `backend/app/api/endpoints/analytics.py` -- `GET /api/v1/analytics/remediation-cards` API route handlers.
- `frontend/src/services/analyticsService.ts` -- Frontend API client method `getRemediationCards`.
- `frontend/src/stores/analyticsStore.ts` -- Pinia store state and action `fetchRemediationCards`.
- `frontend/src/components/expert/RemediationCardPrintView.vue` -- Print-formatted component for single student or group cards with `@media print` styling.
- `frontend/src/components/expert/CompetencyHeatmap.vue` -- UI component adding "Print Cards" toolbar action.
- `backend/tests/api/test_analytics_remediation_cards.py` -- Test suite verifying backend endpoint behavior and tenant isolation.

## Tasks & Acceptance

**Execution:**
- [ ] `backend/app/schemas/analytics.py` -- Add `RemediationCardItem`, `RemediationCardData`, and `RemediationCardsResponse` schemas.
- [ ] `backend/app/repositories/analytics_repo.py` -- Add `get_student_remediation_card_data` method.
- [ ] `backend/app/services/analytics_service.py` -- Add `get_remediation_cards` method constructing remediation cards.
- [ ] `backend/app/api/endpoints/analytics.py` -- Add `GET /api/v1/analytics/remediation-cards` endpoint.
- [ ] `frontend/src/services/analyticsService.ts` -- Add `getRemediationCards` method to API client.
- [ ] `frontend/src/stores/analyticsStore.ts` -- Add `remediationCards` state and `fetchRemediationCards` action.
- [ ] `frontend/src/components/expert/RemediationCardPrintView.vue` -- Create print view component with page-break CSS.
- [ ] `frontend/src/components/expert/CompetencyHeatmap.vue` -- Add "Print Cards" button to trigger card printing.
- [ ] `backend/tests/api/test_analytics_remediation_cards.py` -- Create test file verifying `GET /api/v1/analytics/remediation-cards` functionality.

**Acceptance Criteria:**
- Given `GET /api/v1/analytics/remediation-cards?student_id={id}` is called, then it returns a print-formatted data structure containing student name, failed competencies, recommended atoms, and error classifications.
- Given `GET /api/v1/analytics/remediation-cards?group_id={id}` is called, then it returns card data for all students in the remediation group.
- Given the expert is in the analytics view, when clicking "Print Cards", then a print-formatted view opens and is clean and page-break-friendly when printed (no interactive elements).

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `pytest backend/tests/api/test_analytics_remediation_cards.py` -- expected: 100% tests passing
