# Tasks: Adaptive Diagnostic Engine

**Input**: `specs/006-adaptive-diagnostic-engine/`
**Backend**: Diagnostic engine, API, models, and tests already exist

## Phase 1: Frontend Components

- [ ] T001 Create DiagnosticQuestion component (question display + answer buttons) in `frontend/src/components/student/DiagnosticQuestion.vue`
- [ ] T002 Create DiagnosticProgress component (progress bar + question counter) in `frontend/src/components/student/DiagnosticProgress.vue`
- [ ] T003 Create DiagnosticResults component (mastery, errors, group) in `frontend/src/components/student/DiagnosticResults.vue`

## Phase 2: API Integration

- [ ] T004 Add diagnostic API calls to api service in `frontend/src/services/api.ts`
- [ ] T005 Wire up DiagnosticSession.vue with start→answer→results flow in `frontend/src/views/student/DiagnosticSession.vue`

## Phase 3: Backend Enhancement

- [ ] T006 Add MultiArmBandit question selector to diagnostic_engine.py in `backend/app/services/diagnostic_engine.py`

## Phase 4: Verification

- [ ] T007 Verify TypeScript build with new components
- [ ] T008 Run existing backend diagnostic tests
