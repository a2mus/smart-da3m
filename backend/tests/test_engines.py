"""
Unit tests for backend/app/engines (stateless domain logic).
Verifies pure BKT functions, stateless diagnostic engine, and stateless remediation engine.
"""

from uuid import uuid4

import pytest
from app.engines.bkt import BKTParams, MasteryLevel, get_mastery_level, update_mastery
from app.engines.diagnostic_engine import (
    DiagnosticEngine,
    ErrorClassification,
    ErrorClassificationEnum as ErrorEnum,
    MultiArmBanditSelector,
    QuestionSelector,
    RemediationGroup,
    RemediationGroupEnum as GroupEnum,
)
from app.engines.remediation_engine import (
    DynamicDifficultyAdjuster,
    PassportEvaluator,
    PathwayGenerator,
    RemediationEngine as StatelessRemediationEngine,
    StudentEngagementTracker,
)


def test_bkt_pure_update_correct():
    params = BKTParams(p_learn=0.3, p_guess=0.2, p_slip=0.1)
    # Initial P(L) = 0.0, answer correct -> should increase
    p1 = update_mastery(0.0, is_correct=True, params=params)
    assert p1 > 0.0
    assert p1 <= 1.0

    # Repeat correct -> should approach 1.0
    p2 = update_mastery(p1, is_correct=True, params=params)
    assert p2 > p1


def test_bkt_pure_update_incorrect():
    params = BKTParams(p_learn=0.3, p_guess=0.2, p_slip=0.1)
    p0 = 0.8
    p1 = update_mastery(p0, is_correct=False, params=params)
    assert p1 < p0
    assert p1 >= 0.0


def test_bkt_mastery_level_mapping():
    assert get_mastery_level(0.05) == MasteryLevel.NOT_STARTED
    assert get_mastery_level(0.2) == MasteryLevel.ATTEMPTED
    assert get_mastery_level(0.5) == MasteryLevel.FAMILIAR
    assert get_mastery_level(0.8) == MasteryLevel.PROFICIENT
    assert get_mastery_level(0.95) == MasteryLevel.MASTERED


def test_error_classification():
    classifier = ErrorClassification()
    # Correct -> NONE
    assert classifier.classify(True, None, 5000, 5) == ErrorEnum.NONE

    # Fast incorrect -> INCIDENTAL
    assert classifier.classify(False, None, 1000, 5) == ErrorEnum.INCIDENTAL

    # Targeted misconception -> RESOURCE
    assert classifier.classify(False, "misc_1", 20000, 5) == ErrorEnum.RESOURCE

    # Default incorrect -> PROCESS
    assert classifier.classify(False, None, 20000, 5) == ErrorEnum.PROCESS


def test_stateless_question_selector():
    selector = QuestionSelector()
    questions = [
        {"id": "q1", "difficulty_level": 2},
        {"id": "q2", "difficulty_level": 5},
        {"id": "q3", "difficulty_level": 9},
    ]
    # Mastery 0.1 -> target difficulty 2 -> select q1
    selected = selector.select_next_question(questions, [], 0.1, [])
    assert selected["id"] == "q1"

    # Exclude q1 -> select q2
    selected2 = selector.select_next_question(questions, ["q1"], 0.1, [])
    assert selected2["id"] == "q2"


def test_stateless_multi_arm_bandit_selector():
    selector = MultiArmBanditSelector()
    questions = [
        {"id": "q1", "difficulty_level": 5},
        {"id": "q2", "difficulty_level": 5},
    ]
    stats = {
        "q1": {"success": 10, "total": 10},
        "q2": {"success": 0, "total": 10},
    }
    selected = selector.select_next_question(
        questions=questions,
        answered_question_ids=[],
        current_mastery=0.5,
        target_misconceptions=[],
        question_stats=stats,
        exploration_weight=0.0,
    )
    assert selected is not None


def test_remediation_group_assignment():
    assigner = RemediationGroup()
    assert assigner.assign(0.8, 8, 10) == GroupEnum.A
    assert assigner.assign(0.3, 3, 10) == GroupEnum.C
    assert assigner.assign(0.5, 6, 10) == GroupEnum.B


def test_dynamic_difficulty_adjuster():
    adjuster = DynamicDifficultyAdjuster()
    # Fast correct -> increase difficulty
    new_diff = adjuster.adjust(current_difficulty=5, response_time_ms=2000, is_correct=True, estimated_time_ms=10000)
    assert new_diff > 5

    # Slow wrong -> decrease difficulty
    new_diff_wrong = adjuster.adjust(current_difficulty=5, response_time_ms=15000, is_correct=False, estimated_time_ms=10000)
    assert new_diff_wrong < 5


def test_student_engagement_tracker():
    tracker = StudentEngagementTracker()
    bored_responses = [
        {"time_ms": 1000, "is_correct": True},
        {"time_ms": 1200, "is_correct": True},
        {"time_ms": 1100, "is_correct": True},
    ]
    assert tracker.is_bored(bored_responses) is True
    assert tracker.get_recommendation(bored_responses)["action"] == "increase_difficulty"


def test_stateless_diagnostic_engine_process_answer():
    engine = DiagnosticEngine()
    result = engine.process_answer(
        current_p_learned=0.5,
        is_correct=True,
        response_time_ms=5000,
        difficulty_level=5,
    )
    assert "error_classification" in result
    assert result["current_mastery"] > 0.5
    assert result["mastery_level"] in [MasteryLevel.FAMILIAR, MasteryLevel.PROFICIENT, MasteryLevel.MASTERED]


def test_stateless_remediation_engine():
    engine = StatelessRemediationEngine()
    eval_res = engine.evaluate_passport(
        current_mastery=MasteryLevel.FAMILIAR,
        answers=[{"is_correct": True}, {"is_correct": True}, {"is_correct": True}],
    )
    assert eval_res["passed"] is True
    assert eval_res["new_mastery_level"] == MasteryLevel.PROFICIENT
