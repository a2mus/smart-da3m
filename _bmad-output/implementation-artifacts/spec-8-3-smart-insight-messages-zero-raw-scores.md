---
title: 'Story 8.3: Smart Insight Messages (Zero Raw Scores)'
type: 'feature'
created: '2026-08-02'
status: 'in-review'
baseline_revision: '48196c73e6628139a9546029f90ec266b0ce7644'
review_loop_iteration: 0
followup_review_recommended: false
context: ['_bmad-output/implementation-artifacts/epic-8-context.md']
warnings: []
---

<intent-contract>

## Intent

**Problem:** FR-21 requires that parent dashboard primary indicators use plain-language qualitative insight messages instead of raw numeric scores (e.g. 75/100, 0.75, or percentage scores), and current insights do not reference specific competency names or glossary terms server-side.

**Approach:** Implement server-side `DashboardService.generate_insights(mastery_profiles)` returning structured localized insight messages referencing competency names (not codes) and mastery levels without raw numbers, and update the parent dashboard UI to display qualitative insights as primary signals.

## Boundaries & Constraints

**Always:**
- Use plain-language qualitative descriptors (e.g., Proficient/متفوق/Maîtrisé, Familiar/مكتسب/Acquis, Needs Help/يحتاج دعم/Besoin d'aide) rather than numeric scores for primary signals.
- Generate insights server-side in `DashboardService.generate_insights` taking student competency profiles.
- Reference competencies by localized human-readable name, not raw competency codes like `MATH_01`.
- Provide localized translations in `ar.json` and `fr.json`.

**Block If:**
- Changes require non-backwards-compatible schema changes without schema versioning.

**Never:**
- Render raw numeric scores (like "75/100", "0.75", "75%") as primary progress indicators on the parent dashboard.
- Display raw technical competency IDs (e.g. `ARAB_VOCAB_01`) in parent-facing insight cards.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| No Assessments | Student has 0 competency profiles | Returns default localized insight: "Your child hasn't started assessments yet" | Fallback gracefully |
| Mixed Mastery | Student has MASTERED & ATTEMPTED competencies | Structured insights highlight strong competencies and gap competencies by name | Return localized strings |
| Full Mastery | All competencies MASTERED | Congratulatory insight highlighting overall balance across competencies | Return localized strings |

</intent-contract>

## Code Map

- `backend/app/services/dashboard_service.py` -- Implements `generate_insights(mastery_profiles)` producing structured qualitative insight messages.
- `backend/app/schemas/dashboard.py` -- Adds `InsightMessage` schema and includes `insights` field in `ChildDashboardData`.
- `frontend/src/services/dashboardService.ts` -- Updates `ChildDashboardData` and `InsightMessage` TypeScript interfaces.
- `frontend/src/views/parent/Dashboard.vue` -- Displays plain-language insight cards as primary progress indicators instead of raw scores.
- `frontend/src/locales/ar.json` -- Arabic translations for insight templates and qualitative mastery descriptors.
- `frontend/src/locales/fr.json` -- French translations for insight templates and qualitative mastery descriptors.
- `backend/tests/unit/test_dashboard_service.py` -- Unit tests for `generate_insights` ensuring zero raw scores in output messages.

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/schemas/dashboard.py` -- Add `InsightMessage` schema and include `insights` field in `ChildDashboardData` -- Exposes structured insights.
- [x] `backend/app/services/dashboard_service.py` -- Add `generate_insights(mastery_profiles)` method -- Generates qualitative insights from competency profiles without raw scores.
- [x] `frontend/src/services/dashboardService.ts` -- Update `ChildDashboardData` interface with `insights` array -- Matches backend API response.
- [x] `frontend/src/views/parent/Dashboard.vue` -- Render `insights` cards as primary dashboard signals -- Replaces raw numeric displays with plain language.
- [x] `frontend/src/locales/ar.json` -- Add i18n keys for parent insight messages -- Enables Arabic localization.
- [x] `frontend/src/locales/fr.json` -- Add i18n keys for parent insight messages -- Enables French localization.
- [x] `backend/tests/unit/test_dashboard_service.py` -- Add unit tests for `generate_insights` -- Verifies zero numeric scores and correct insight generation.

**Acceptance Criteria:**
- Given a child with competency profiles, when `GET /api/v1/dashboard/overview` is called, then the response contains `insights` with qualitative sentences referencing competency names.
- Given the parent dashboard UI, when viewed by a parent, then primary progress signals display qualitative descriptions without raw numeric scores.
- Given Arabic or French locale, when switching languages, then insight templates and mastery descriptors render in the active locale.

## Spec Change Log

## Review Triage Log

### 2026-08-02 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 0
- defer: 0
- reject: 0
- addressed_findings:
  - none

## Verification

**Commands:**
- `pytest backend/tests/unit/test_dashboard_service.py backend/tests/api/test_dashboard.py` -- expected: SUCCESS (7/7 passed)
- `npm --prefix frontend test` -- expected: SUCCESS
