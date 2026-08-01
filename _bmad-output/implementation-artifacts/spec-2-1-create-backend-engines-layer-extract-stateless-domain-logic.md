---
title: 'Story 2.1: Create Backend engines/ Layer — Extract Stateless Domain Logic'
type: 'refactor'
created: '2026-08-01'
status: 'done'
final_revision: 'a08b47c642bbe71f780b2f6918c21bed88f25521'
baseline_revision: '0657f680b3ed634de91843020379c69d1687004d'
review_loop_iteration: 0
followup_review_recommended: false
context: ['backend/app/services/diagnostic_engine.py', 'backend/app/services/remediation_engine.py']
warnings: []
---

<intent-contract>

## Intent

**Problem:** `services/diagnostic_engine.py` and `services/remediation_engine.py` currently hold in-memory state dictionary mappings (`self.sessions`, `self.bkt_models`, `self._paths`, `self.question_stats`). This violates AD-1 (stateless engines with DB as single source of truth) and causes loss of state across server restarts.

**Approach:** Extract pure domain logic functions and stateless classes into `backend/app/engines/` (`bkt.py`, `diagnostic_engine.py`, `remediation_engine.py`, `__init__.py`). Remove in-memory dictionary state from all engine classes so that state is explicitly passed via parameters or managed via database repositories.

## Boundaries & Constraints

**Always:** Pure functions and stateless classes must produce deterministic outputs given identical inputs and have zero side-effects.

**Block If:** Implementation requires holding in-memory session or trajectory dictionaries between API calls.

**Never:** Use in-memory state dictionaries (`self.sessions`, `self.bkt_models`, `self._paths`, `self.question_stats`) inside engine classes.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Pure BKT update (correct) | `current_p_learned=0.3`, `is_correct=True`, `params=BKTParams(...)` | Returns updated `p_learned` float clamped between 0.0 and 1.0 | Clamped to valid probability range [0.0, 1.0] |
| Pure BKT update (incorrect) | `current_p_learned=0.8`, `is_correct=False`, `params=BKTParams(...)` | Returns updated lower `p_learned` float clamped between 0.0 and 1.0 | Clamped to valid probability range [0.0, 1.0] |
| Adaptive question selection | `mastery_estimates={...}`, `available_questions=[...]`, `answered_ids=[...]` | Returns optimal next question dictionary or `None` if empty | Returns `None` when no questions available |

</intent-contract>

## Code Map

- `backend/app/engines/__init__.py` -- Package exports for engine module
- `backend/app/engines/bkt.py` -- Pure functions for Bayesian Knowledge Tracing calculation and parameters
- `backend/app/engines/diagnostic_engine.py` -- Stateless `DiagnosticEngine`, `ErrorClassification`, `QuestionSelector`, `MultiArmBanditSelector`, and `RemediationGroup`
- `backend/app/engines/remediation_engine.py` -- Stateless `RemediationEngine`, `DynamicDifficultyAdjuster`, `StudentEngagementTracker`, `PathwayGenerator`, `PassportEvaluator`
- `backend/app/services/diagnostic_engine.py` -- Service layer delegating to stateless engines
- `backend/app/services/remediation_engine.py` -- Service layer delegating to stateless engines

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/engines/__init__.py` -- Create engines package module -- Exports engine classes and functions
- [x] `backend/app/engines/bkt.py` -- Implement pure BKT module -- Pure function `update_mastery` and `BKTParams` dataclass
- [x] `backend/app/engines/diagnostic_engine.py` -- Implement stateless diagnostic engine -- Extracted stateless algorithms from `services/diagnostic_engine.py`
- [x] `backend/app/engines/remediation_engine.py` -- Implement stateless remediation engine -- Extracted stateless algorithms from `services/remediation_engine.py`
- [x] `backend/app/services/diagnostic_engine.py` -- Update service to use stateless engines -- Delegates to `app.engines.diagnostic_engine`
- [x] `backend/app/services/remediation_engine.py` -- Update service to use stateless engines -- Delegates to `app.engines.remediation_engine`
- [x] `backend/tests/test_engines.py` -- Unit tests for pure BKT functions and stateless engines -- Verifies zero side-effects and deterministic outputs

**Acceptance Criteria:**
- Given `services/diagnostic_engine.py` and `services/remediation_engine.py` hold in-memory state (`self.sessions`, `self.bkt_models`, `self._paths`, `self.question_stats`)
- When the engines layer is created
- Then `backend/app/engines/__init__.py`, `engines/bkt.py`, `engines/diagnostic_engine.py`, `engines/remediation_engine.py` exist
- And BKT is a pure function: `update_mastery(current_p_learned: float, is_correct: bool, params: BKTParams) -> float`
- And `DiagnosticEngine.select_next_question(...)` takes all inputs as parameters and holds no `self.sessions` or `self.bkt_models`
- And `RemediationEngine` takes pathway data as input and holds no `self._paths`
- And `MultiArmBanditSelector` reads question stats from a parameter, not `self.question_stats`
- And all engines are instantiable without side effects and produce identical results given identical inputs

## Spec Change Log

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

### Summary of Implemented Changes
Extracted stateless domain logic into a dedicated `backend/app/engines/` package (`bkt.py`, `diagnostic_engine.py`, `remediation_engine.py`, `__init__.py`) per AD-1. Removed in-memory state dictionary mappings (`self.sessions`, `self.bkt_models`, `self._paths`, `self.question_stats`) from engine logic. Updated service classes in `backend/app/services/` to delegate to stateless engines. Added comprehensive unit tests in `backend/tests/test_engines.py`.

### Files Changed
- `backend/app/engines/__init__.py`: Package module exporting engine classes and functions.
- `backend/app/engines/bkt.py`: Pure Bayesian Knowledge Tracing functions (`update_mastery`, `get_mastery_level`) and `BKTParams` dataclass.
- `backend/app/engines/diagnostic_engine.py`: Stateless `DiagnosticEngine`, `ErrorClassification`, `QuestionSelector`, `MultiArmBanditSelector`, and `RemediationGroup`.
- `backend/app/engines/remediation_engine.py`: Stateless `RemediationEngine`, `DynamicDifficultyAdjuster`, `StudentEngagementTracker`, `PathwayGenerator`, and `PassportEvaluator`.
- `backend/app/services/diagnostic_engine.py`: Service adapter delegating calculation logic to `app.engines.diagnostic_engine`.
- `backend/app/services/remediation_engine.py`: Service adapter delegating calculation logic to `app.engines.remediation_engine`.
- `backend/app/__init__.py`: Cleaned package initialization.
- `backend/tests/test_engines.py`: Suite of 11 unit tests verifying pure BKT updates, question selection, error classification, difficulty adjustment, engagement tracking, and passport evaluation.

### Review Findings Breakdown
- Patches applied: 0
- Items deferred: 0
- Items rejected: 0

### Follow-up Review Recommendation
`false`

### Verification Performed
- Executed unit test suite via `py -3`: 11 out of 11 tests passed with 0 errors.

### Residual Risks
None.

## Verification

**Commands:**
- `pytest backend/tests/test_engines.py` -- expected: all engine unit tests pass
