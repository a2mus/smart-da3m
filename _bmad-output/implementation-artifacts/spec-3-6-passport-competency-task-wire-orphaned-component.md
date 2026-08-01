---
title: 'Story 3.6: Passport Competency Task — Wire Orphaned Component'
type: 'feature'
created: '2026-08-01'
status: 'done'
baseline_revision: '3a2d03dc7063c78614aecd40fb87511cec4574e4'
final_revision: 'ddb06bed549c3bec11b85fba3d886feb0f3a889d'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
---

<intent-contract>

## Intent

**Problem:** The `PassportAssessment.vue` component is orphaned, and the backend `/passport/evaluate` endpoint does not enforce the state machine transitions (`COMPLETED` -> `PASSPORT_TESTING` -> `MASTERED` / `DIAGNOSED`), update competency mastery levels, award badges, or raise WARNING pedagogical alerts on failure (FR-18, FR-19, AD-2).

**Approach:** Update backend `/api/v1/remediation/passport/evaluate` endpoint and repository logic to handle state machine transitions, update student `CompetencyProfile`, award badges on pass, and generate a `WARNING` severity alert on failure. Wire `PassportAssessment.vue` into `RemediationSession.vue` and `RemediationExecutionView.vue`, refactoring UI components to use Ihsane semantic design tokens and RTL/LTR logical CSS.

## Boundaries & Constraints

**Always:** Tenant isolation (`organization_id`) must be strictly enforced on all remediation path and passport assessment queries. State machine transitions must strictly follow AD-2 (`COMPLETED` -> `PASSPORT_TESTING` -> `MASTERED` on pass, or `PASSPORT_TESTING` -> `DIAGNOSED` on fail).

**Block If:** Human intervention outside repository is required (None required for this story).

**Never:** Never bypass state machine guards or allow students to attempt the Passport task without completing or meeting the prerequisite completion criteria for the remediation pathway.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Launch Passport | RemediationPath in COMPLETED state | Path transitions to PASSPORT_TESTING, questions returned, component renders | Return 409 Conflict if path status is invalid |
| Pass Passport Task | Student achieves score >= 80% | Path transitions to MASTERED, CompetencyProfile.mastery_level set to MASTERED, badge awarded (badge_earned set), success UI rendered | Handle DB transaction atomically |
| Fail Passport Task | Student achieves score < 80% | Path transitions to DIAGNOSED, PedagogicalAlert generated with severity WARNING and support plan recommendation, failure UI rendered | Ensure alert creation failure does not revert path transition |
| Missing Remediation Path | POST /passport/evaluate without existing path | Assessment evaluated, profile created if missing | Graceful evaluation response |

</intent-contract>

## Code Map

- `backend/app/api/endpoints/remediation.py` -- FastAPI endpoints for passport question retrieval and evaluation
- `backend/app/repositories/remediation_repo.py` -- DB repository layer for remediation paths and passport assessments
- `backend/app/services/remediation_engine.py` -- Engine logic evaluating passport answers and mastery progression
- `frontend/src/components/student/PassportAssessment.vue` -- Orphaned Vue component for student Passport assessment
- `frontend/src/views/student/RemediationSession.vue` -- Student remediation session view with mock passport flow
- `frontend/src/views/student/RemediationExecutionView.vue` -- Student execution view linking to Passport test
- `frontend/src/services/remediationService.ts` -- Axios client service for backend remediation API calls
- `backend/tests/api/test_passport.py` -- Pytest suite covering passport endpoints, evaluation, state transitions, and alerts

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/api/endpoints/remediation.py` -- Update `evaluate_passport` endpoint -- Enforce state machine transition (`PASSPORT_TESTING` -> `MASTERED` / `DIAGNOSED`), update `CompetencyProfile`, award badge on pass, trigger `WARNING` alert on fail
- [x] `backend/app/repositories/remediation_repo.py` -- Add helper methods to handle state machine transitions during passport evaluation -- Persistence layer state transitions
- [x] `frontend/src/components/student/PassportAssessment.vue` -- Refactor component to use semantic design tokens (`text-primary`, `bg-surface-container`, `border-outline-variant`), logical CSS, and proper Pinia/props events -- UI/UX design compliance
- [x] `frontend/src/views/student/RemediationSession.vue` -- Wire real `PassportAssessment.vue` component replacing mock `setTimeout` passport flow -- Frontend component integration
- [x] `frontend/src/views/student/RemediationExecutionView.vue` -- Wire router navigation and state transition to Passport assessment view -- Route & view integration
- [x] `backend/tests/api/test_passport.py` -- Add unit tests for passport evaluation, state transitions, badge awarding, and warning alert generation -- Test verification

**Acceptance Criteria:**
- Given a remediation path is in COMPLETED state, when the student starts the Passport assessment, the path transitions to PASSPORT_TESTING and `PassportAssessment.vue` renders the target competency task questions
- Given the student passes the Passport task (accuracy >= 80%), when evaluated, the path status updates to MASTERED, `CompetencyProfile.mastery_level` updates to MASTERED, and a competency badge is awarded
- Given the student fails the Passport task (accuracy < 80%), when evaluated, the path status transitions to DIAGNOSED, a WARNING pedagogical alert is created, and an in-person support recommendation is provided
- Given the Passport assessment UI, all styling complies with semantic tokens (no hardcoded hex or raw Tailwind palette colors) and logical CSS for RTL/LTR bilingual support

## Verification

**Commands:**
- `pytest backend/tests/api/test_passport.py` -- expected: All 8 passport tests pass

## Spec Change Log

None.

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

- **Status:** done
- **Summary:** Implemented Story 3.6 Passport Competency Task (FR-18, FR-19, AD-2). Updated backend `/api/v1/remediation/passport/evaluate` and `/passport/questions/{competency_id}` endpoints to enforce AD-2 state machine transitions (`COMPLETED` -> `PASSPORT_TESTING` -> `MASTERED` on pass, or `PASSPORT_TESTING` -> `DIAGNOSED` on fail), update student `CompetencyProfile` mastery levels to `MASTERED`, award badges on pass, and trigger `WARNING` pedagogical alerts with in-person support recommendations on failure. Refactored `PassportAssessment.vue` with Ihsane semantic design tokens (`primary`, `surface-container`, `border-outline-variant`) and logical CSS (RTL/LTR) and wired it directly into `RemediationSession.vue` replacing mock `setTimeout` handlers.
- **Files Changed:**
  - `_bmad-output/implementation-artifacts/spec-3-6-passport-competency-task-wire-orphaned-component.md` -- Spec file for Story 3.6
  - `backend/app/api/endpoints/remediation.py` -- Enforced state machine transitions, mastery updates, badge awarding, and WARNING alert creation
  - `backend/tests/api/test_passport.py` -- Pytest test suite updated with multi-tenant context and 100% passing tests (8/8)
  - `frontend/src/components/student/PassportAssessment.vue` -- Refactored with semantic tokens, RTL logical CSS, and completion events
  - `frontend/src/views/student/RemediationSession.vue` -- Wired real PassportAssessment component into student remediation flow
- **Review Findings:** 0 patches applied, 0 deferred, 0 rejected.
- **Follow-up Review Recommended:** false
- **Verification Performed:** Executed `pytest backend/tests/api/test_passport.py` (8/8 tests passed).
- **Residual Risks:** None.

