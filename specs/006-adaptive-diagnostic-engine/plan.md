# Plan: Adaptive Diagnostic Engine Frontend

**Feature**: 006-adaptive-diagnostic-engine
**Backend status**: Fully implemented (BKT, error classification, question selection, API, models, tests)

## Summary

Build the student-facing diagnostic test UI in Vue 3, connecting to the existing FastAPI diagnostic endpoints. Add multi-arm bandit to the backend QuestionSelector.

## Files to Create

| File | Purpose |
|------|---------|
| `frontend/src/components/student/DiagnosticQuestion.vue` | Single question card with answer options |
| `frontend/src/components/student/DiagnosticProgress.vue` | Progress bar + question counter |
| `frontend/src/components/student/DiagnosticResults.vue` | Results: mastery, errors, group |

## Files to Modify

| File | Change |
|------|--------|
| `frontend/src/views/student/DiagnosticSession.vue` | Wire up full diagnostic flow (start → answer loop → results) |
| `frontend/src/services/api.ts` | Add diagnostic API calls |
| `backend/app/services/diagnostic_engine.py` | Add MultiArmBandit question selector |

## API Endpoints (existing)

- `POST /diagnostic/start` — Start session, returns first question
- `POST /diagnostic/answer` — Submit answer, returns next question + BKT state
- `GET /diagnostic/{id}/results` — Get final results
