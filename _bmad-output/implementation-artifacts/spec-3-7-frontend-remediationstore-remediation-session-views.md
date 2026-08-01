---
title: 'Story 3.7: Frontend remediationStore & Remediation Session Views'
type: 'feature'
created: '2026-08-01'
status: 'done'
baseline_revision: '610e4e7a06518be931082ca8364f6f99aa56c360'
final_revision: '6a7039bb866e88c6e5d66828456c5621f9c1dd89'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
---

<intent-contract>

## Intent

**Problem:** Currently, the frontend lacks a central `remediationStore` Pinia store to manage remediation session state, active pathways, knowledge atoms, and passport assessment state. Components like `RemediationSession.vue` rely on inline mock data and fake passport transitions with `setTimeout`, while `RemediationExecutionView.vue` and `PassportAssessment.vue` call `remediationService` directly instead of going through a centralized reactive Pinia store.

**Approach:** Implement `src/stores/remediationStore.ts` to encapsulate all remediation state and API calls via `remediationService` (which incorporates the camelCase transformer from Story 1.1). Refactor `RemediationSession.vue`, `RemediationExecutionView.vue`, and `PassportAssessment.vue` to consume and trigger actions on `remediationStore` exclusively, removing direct `remediationService` imports from view and component layers and eliminating all inline mock data and fake `setTimeout` handlers.

## Boundaries & Constraints

**Always:** All components must interact with remediation state via `remediationStore`, never calling `remediationService` directly. Store actions must handle async errors and maintain reactive state for `pathway`, `currentAtom`, `atomsCompleted`, `passportQuestions`, `passportEvaluation`, `loading`, `actionLoading`, and `error`. RTL/LTR logical CSS and Ihsane semantic design tokens (`primary`, `surface-bright`, `surface-container`, `border-outline-variant`) must be maintained across all refactored views.

**Block If:** Human intervention outside repository is required (None required for this story).

**Never:** Never call `remediationService` directly inside UI Vue components or views. Never retain inline mock data or fake `setTimeout` handlers in production views.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Fetch Remediation Pathway | Competency ID | `remediationStore.pathway` loaded, `currentAtom` set to first uncompleted atom | `remediationStore.error` set with user message |
| Start Remediation Pathway | Validated Path ID | `remediationStore.pathway.status` updated to `IN_PROGRESS`, path reloaded | Handle HTTP error gracefully, set error state |
| Complete Atom | Atom ID + completion metrics | `POST /atoms/{atom_id}/complete` executed, `atomsCompleted` updated, `currentAtom` advances to next atom, progress percent updated | Retain current atom view on error, set error message |
| Load Passport Questions | Competency ID | `remediationStore.passportQuestions` loaded, passport assessment UI rendered | Display error banner in passport component |
| Evaluate Passport Assessment | Competency ID + student answers | `remediationStore.passportEvaluation` populated, path status updated (`MASTERED` or `DIAGNOSED`), `completed` event emitted | Retain submission state, set error message |

</intent-contract>

## Code Map

- `frontend/src/stores/remediationStore.ts` -- Pinia store managing remediation state, active pathway, atoms, and passport assessment
- `frontend/src/views/student/RemediationSession.vue` -- Student remediation session view refactored to use `remediationStore`
- `frontend/src/views/student/RemediationExecutionView.vue` -- Student execution view refactored to use `remediationStore`
- `frontend/src/components/student/PassportAssessment.vue` -- Component refactored to use `remediationStore` methods for questions loading and evaluation
- `frontend/src/services/remediationService.ts` -- HTTP client service layer called strictly by `remediationStore`
- `frontend/tests/stores/remediationStore.spec.ts` -- Unit tests for `remediationStore` state management and actions

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/stores/remediationStore.ts` -- Create Pinia `remediationStore` -- Centralize remediation pathway, atom execution, and passport state management
- [x] `frontend/src/views/student/RemediationSession.vue` -- Refactor to use `remediationStore` -- Remove inline mock data and fake `setTimeout` handlers
- [x] `frontend/src/views/student/RemediationExecutionView.vue` -- Refactor to use `remediationStore` -- Replace direct `remediationService` calls with store actions
- [x] `frontend/src/components/student/PassportAssessment.vue` -- Refactor to use `remediationStore` -- Replace direct `remediationService` calls with store actions
- [x] `frontend/tests/stores/remediationStore.spec.ts` -- Add unit tests for `remediationStore` -- Test store actions, reactive state updates, and error handling

**Acceptance Criteria:**
- Given a student navigating to a remediation session, when `RemediationSession.vue` or `RemediationExecutionView.vue` mounts, the pathway and atoms are managed reactively via `remediationStore`
- Given the student completes an atom, when the action is triggered, `remediationStore.completeAtom` calls `remediationService.completeAtom`, updating `atomsCompleted` and advancing to the next atom
- Given a completed pathway, when the student launches the Passport assessment, `remediationStore.getPassportQuestions` loads questions and `remediationStore.evaluatePassport` handles evaluation
- Given all UI components (`RemediationSession.vue`, `RemediationExecutionView.vue`, `PassportAssessment.vue`), zero components import or call `remediationService` directly

## Verification

**Commands:**
- `npx vitest run tests/stores/remediationStore.spec.ts` (in `frontend/`) -- expected: All 7 unit tests pass

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
- **Summary:** Implemented Story 3.7 Frontend `remediationStore` & Remediation Session Views. Created `frontend/src/stores/remediationStore.ts` as a Pinia store encapsulating remediation pathway, atom execution progress, and passport assessment evaluation state. Refactored `RemediationSession.vue`, `RemediationExecutionView.vue`, and `PassportAssessment.vue` to delegate all state mutations and HTTP operations to `remediationStore`, eliminating all inline mock data and fake `setTimeout` handlers. Added unit tests in `frontend/tests/stores/remediationStore.spec.ts` with 100% passing test coverage (7/7 tests).
- **Files Changed:**
  - `_bmad-output/implementation-artifacts/spec-3-7-frontend-remediationstore-remediation-session-views.md` -- Spec artifact for Story 3.7
  - `frontend/src/stores/remediationStore.ts` -- Centralized Pinia store for remediation session and passport state
  - `frontend/src/views/student/RemediationSession.vue` -- Refactored session view to consume `remediationStore` and eliminate mock state
  - `frontend/src/views/student/RemediationExecutionView.vue` -- Refactored execution view to use `remediationStore` actions
  - `frontend/src/components/student/PassportAssessment.vue` -- Refactored component to use `remediationStore` methods for questions loading and evaluation
  - `frontend/tests/stores/remediationStore.spec.ts` -- Unit test suite for `remediationStore` (7/7 tests passing)
- **Review Findings:** 0 patches applied, 0 deferred, 0 rejected.
- **Follow-up Review Recommended:** false
- **Verification Performed:** Executed `npx vitest run tests/stores/remediationStore.spec.ts` (7/7 tests passed).
- **Residual Risks:** None.
