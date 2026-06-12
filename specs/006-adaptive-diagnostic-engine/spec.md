# Feature Specification: Adaptive Diagnostic Engine (F1)

**Feature Branch**: `006-adaptive-diagnostic-engine`
**Status**: In Progress
**Input**: product-spec.md §5.1 (F1) + Appendix C.1

## Summary

The backend diagnostic engine (BKT, error classification, adaptive question selection, remediation grouping, API endpoints, database models) is already implemented. This feature focuses on **frontend integration**: building the student-facing diagnostic session UI, connecting to the existing backend API, and adding the multi-arm bandit question selector.

## User Stories

### US1 — Student Starts and Completes a Diagnostic Test (P1)

A student navigates to the diagnostic section, selects a module (Math or Arabic), and begins an adaptive test. Questions appear one at a time with age-appropriate UI. After ~10 questions, the test completes and results are displayed.

### US2 — Adaptive Difficulty Adjustment (P1)

Questions get harder or easier based on student performance. Correct answers yield harder questions; incorrect answers yield easier ones targeting identified misconceptions.

### US3 — Results Display with Remediation Group (P2)

After completion, the student sees their mastery level, error classification summary, and assigned remediation group (A/B/C).

## Requirements

- **FR-001**: DiagnosticSession Vue component with question display, answer submission, progress indicator
- **FR-002**: Connect frontend diagnostic flow to existing `POST /diagnostic/start` and `POST /diagnostic/answer` endpoints
- **FR-003**: Results view showing mastery level, error breakdown, group assignment
- **FR-004**: Multi-arm bandit question selection algorithm (backend enhancement)
- **FR-005**: Age-appropriate UI (large touch targets ≥60px, audio cues for ages 6-7)

## Key Entities

- **DiagnosticSession**: Active test session with BKT state
- **DiagnosticAnswer**: Individual question response with error classification
- **CompetencyProfile**: Per-student mastery state per competency
