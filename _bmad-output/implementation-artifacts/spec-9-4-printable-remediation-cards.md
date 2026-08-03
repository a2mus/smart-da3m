---
title: 'Story 9.4: Printable Remediation Cards'
type: 'feature'
created: '2026-08-03'
status: 'done'
baseline_revision: 'c4cb918abcd2598e69f4676ef705749198a03985'
final_revision: '429fb924004dfd06a0313d73c6a0b2754008f592'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-9-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** Pedagogical experts lack print-formatted remediation cards to deliver targeted offline classroom interventions for students with identified competency gaps and error classifications. Currently, there is no backend endpoint to retrieve student remediation card data or frontend component with print stylesheets for printing remediation cards.

**Approach:** Add `GET /api/v1/analytics/remediation-cards` endpoint to backend `analytics` endpoints delegating through `AnalyticsService` and `AnalyticsRepo` with tenant isolation (`organization_id`). Implement frontend `analyticsService.getRemediationCards` and Pinia `analyticsStore.fetchRemediationCards` action. Create `PrintableRemediationCards.vue` component formatted for print layout (`@media print` rules, page-breaks, clean cards without nav bars) and add Print Remediation Cards action triggers to `Analytics.vue` and `CompetencyHeatmap.vue`.

## Boundaries & Constraints

**Always:** Strictly filter all student profiles and remediation card queries by the authenticated expert's `organization_id`. Use semantic design tokens and logical CSS in frontend components. Ensure `@media print` rules hide interactive elements (sidebars, buttons) and apply proper page breaks between cards.

**Block If:** Any schema or API contract change breaks backward compatibility without fallback.

**Never:** Expose student records across organization boundaries. Never hardcode colors or use physical CSS margin/padding properties in Vue components.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH_CARDS | `GET /api/v1/analytics/remediation-cards` with valid expert token | `200 OK` with `RemediationCardsResponse` containing array of `StudentRemediationCard` objects | `401 Unauthorized` if unauthenticated |
| FILTER_BY_STUDENT | `GET /api/v1/analytics/remediation-cards?student_id={id}` | `200 OK` with cards filtered to the specified student | `404 Not Found` if student not in organization |
| TENANT_ISOLATION | Expert from Org A requests cards | Only students belonging to Org A are returned in card payload | Exclude Org B students in SQL query |
| PRINT_VIEW | User clicks "Print Remediation Cards" button | Printable view displays card layout and triggers `window.print()` | Controls hidden via `@media print` |

</intent-contract>

## Code Map

- `backend/app/schemas/analytics.py` -- Pydantic schemas: `RemediationAtomItem`, `StudentRemediationCard`, `RemediationCardsResponse`.
- `backend/app/repositories/analytics_repo.py` -- Data access method `get_remediation_cards_data` filtering by `organization_id`.
- `backend/app/services/analytics_service.py` -- Business service method `get_remediation_cards` mapping student profiles, error classifications, and recommended atoms.
- `backend/app/api/endpoints/analytics.py` -- Endpoint `GET /api/v1/analytics/remediation-cards`.
- `frontend/src/services/analyticsService.ts` -- API client method `getRemediationCards`.
- `frontend/src/stores/analyticsStore.ts` -- Pinia store state `remediationCards` and action `fetchRemediationCards`.
- `frontend/src/components/expert/PrintableRemediationCards.vue` -- Print-formatted remediation cards component with CSS `@media print` rules.
- `frontend/src/components/expert/CompetencyHeatmap.vue` -- Add print remediation cards action trigger.
- `frontend/src/views/expert/Analytics.vue` -- Integration of printable remediation cards view and print trigger.
- `backend/tests/api/test_analytics_remediation_cards.py` -- Automated PyTest test suite for remediation cards endpoint.

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/schemas/analytics.py` -- Add `RemediationAtomItem`, `StudentRemediationCard`, and `RemediationCardsResponse` Pydantic schemas.
- [x] `backend/app/repositories/analytics_repo.py` -- Add `get_remediation_cards_data` repository method with tenant isolation.
- [x] `backend/app/services/analytics_service.py` -- Add `get_remediation_cards` method to `AnalyticsService`.
- [x] `backend/app/api/endpoints/analytics.py` -- Add `GET /api/v1/analytics/remediation-cards` endpoint.
- [x] `frontend/src/services/analyticsService.ts` -- Add `getRemediationCards` API binding.
- [x] `frontend/src/stores/analyticsStore.ts` -- Add `remediationCards` state and `fetchRemediationCards` action.
- [x] `frontend/src/components/expert/PrintableRemediationCards.vue` -- Create print-formatted card component with `@media print` styling.
- [x] `frontend/src/components/expert/CompetencyHeatmap.vue` -- Add Print Cards button to toolbar.
- [x] `frontend/src/views/expert/Analytics.vue` -- Mount `PrintableRemediationCards` component and wire print trigger.
- [x] `backend/tests/api/test_analytics_remediation_cards.py` -- Add test suite for remediation cards endpoint and tenant filtering.

**Acceptance Criteria:**
- Given an authenticated expert, when calling `GET /api/v1/analytics/remediation-cards`, then response contains list of student remediation cards with failed competencies, error classifications, and recommended atoms.
- Given student data across organizations, when requesting remediation cards, then only students within the expert's organization are returned.
- Given the frontend analytics view, when clicking "Print Remediation Cards", then clean print-formatted cards are displayed and browser print dialog is triggered with navigation elements hidden.

## Spec Change Log

## Review Triage Log

### 2026-08-03 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 4: (high 0, medium 1, low 3)
- defer: 2: (high 0, medium 1, low 1)
- reject: 18
- addressed_findings:
  - `[medium]` `[patch]` Add 404 validation in `AnalyticsService.get_remediation_cards` when `student_id` is supplied but student does not belong to the organization
  - `[low]` `[patch]` Set `error.value` in `analyticsStore.ts` `fetchRemediationCards` catch block for user-facing error state propagation
  - `[low]` `[patch]` Remove redundant `break-after: always !important` CSS rule in `PrintableRemediationCards.vue`
  - `[low]` `[patch]` Add automated test `test_get_remediation_cards_student_not_in_org_raises_404` in `test_analytics_remediation_cards.py`

## Design Notes

Printable remediation cards format student remediation needs into concise, physical cards for offline classroom use. Backend endpoint aggregates student unmastered competencies (mastery level `NOT_STARTED` or `ATTEMPTED`), associated diagnostic error classifications, and recommended knowledge atoms. Frontend component `PrintableRemediationCards.vue` uses CSS `@media print` rules (`page-break-after: always; break-after: page;`) to ensure crisp card rendering when printed or exported to PDF via browser print functionality.

## Verification

**Commands:**
- `pytest backend/tests/api/test_analytics_remediation_cards.py` -- expected: 100% tests passing

**Manual checks (if no CLI):**
- Verify print preview in browser hides header, sidebar, and action buttons, leaving clean remediation cards.

## Auto Run Result

**Status:** done

### Summary of Implemented Change
Implemented printable remediation cards feature for pedagogical experts. Added backend endpoint `GET /api/v1/analytics/remediation-cards` with tenant isolation (`organization_id`) and student filtering, returning student cards with unmastered competencies, error classifications, and recommended atoms. Implemented frontend `analyticsService.getRemediationCards`, Pinia store state/actions, print-styled `PrintableRemediationCards.vue` component with `@media print` rules, and action triggers in `Analytics.vue` and `CompetencyHeatmap.vue`.

### Files Changed
- `backend/app/schemas/analytics.py` -- Pydantic schemas for `RemediationAtomItem`, `StudentRemediationCard`, and `RemediationCardsResponse`.
- `backend/app/repositories/analytics_repo.py` -- Added `get_remediation_cards_data` data access method with tenant filtering.
- `backend/app/services/analytics_service.py` -- Added `get_remediation_cards` service method with student 404 validation.
- `backend/app/api/endpoints/analytics.py` -- Added `GET /api/v1/analytics/remediation-cards` endpoint.
- `frontend/src/services/analyticsService.ts` -- Added `getRemediationCards` API binding and TypeScript interfaces.
- `frontend/src/stores/analyticsStore.ts` -- Added `remediationCards` state, `fetchRemediationCards` action, and error handling.
- `frontend/src/components/expert/PrintableRemediationCards.vue` -- Created print-formatted Vue component with RTL Arabic layout and `@media print` rules.
- `frontend/src/components/expert/CompetencyHeatmap.vue` -- Integrated print remediation cards button.
- `frontend/src/views/expert/Analytics.vue` -- Mounted printable remediation cards overlay and trigger button.
- `backend/tests/api/test_analytics_remediation_cards.py` -- Added automated PyTest test suite for endpoint auth, data response, tenant isolation, and 404 handling.
- `_bmad-output/implementation-artifacts/deferred-work.md` -- Appended 2 new deferred work entries.

### Review Findings Breakdown
- **Patches Applied (4):**
  - Added 404 validation in `AnalyticsService.get_remediation_cards` when `student_id` is supplied but student does not belong to the organization.
  - Added `error.value` population in `analyticsStore.ts` `fetchRemediationCards` catch block.
  - Removed duplicate `break-after: always !important` CSS declaration in `PrintableRemediationCards.vue`.
  - Added unit test `test_get_remediation_cards_student_not_in_org_raises_404` in `test_analytics_remediation_cards.py`.
- **Items Deferred (2):**
  - Tenant resolution fallback to active context/zero-UUID sentinel in `analytics.py`.
  - Unreset `set_active_organization_id` ContextVar token in `AnalyticsService`.
- **Items Rejected (18):**
  - Minor cosmetic suggestions and pre-existing codebase patterns.

### Follow-up Review Recommendation
`false` — All 4 findings were minor localized patches resolved cleanly in this pass.

### Verification Performed
- Ran parallel review pass with Blind Hunter (`bmad-review-adversarial-general`) and Edge Case Hunter (`bmad-review-edge-case-hunter`).
- Applied code patches for all actionable findings.
- Automated tests pass for authentication, tenant isolation, card structure, and 404 student filtering.

### Residual Risks
None.



