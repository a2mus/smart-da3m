"""
Unit tests for diagnostic engine (BKT + question selection) (T022).
Tests Bayesian Knowledge Tracing logic and adaptive question selection.
"""

import pytest
from uuid import uuid4

from app.services.diagnostic_engine import (
    BayesianKnowledgeTracing,
    DiagnosticEngine,
    ErrorClassification,
    QuestionSelector,
    RemediationGroup,
)


class TestBayesianKnowledgeTracing:
    """Test suite for BKT algorithm."""

    def test_bkt_initialization(self):
        """Test BKT model initializes with default probabilities."""
        bkt = BayesianKnowledgeTracing()

        assert bkt.p_learned == 0.0
        assert bkt.p_learn == 0.3  # Probability of learning
        assert bkt.p_guess == 0.2  # Probability of guessing correctly
        assert bkt.p_slip == 0.1  # Probability of slipping (incorrect when known)

    def test_bkt_update_correct_answer(self):
        """Test BKT update after correct answer."""
        bkt = BayesianKnowledgeTracing()
        bkt.p_learned = 0.5  # Set initial state

        # Update with correct answer
        bkt.update(is_correct=True)

        # P(learned) should increase after correct answer
        assert bkt.p_learned > 0.5
        assert 0.0 <= bkt.p_learned <= 1.0

    def test_bkt_update_incorrect_answer(self):
        """Test BKT update after incorrect answer."""
        bkt = BayesianKnowledgeTracing()
        bkt.p_learned = 0.5  # Set initial state

        # Update with incorrect answer
        bkt.update(is_correct=False)

        # P(learned) should decrease after incorrect answer
        assert bkt.p_learned < 0.5
        assert 0.0 <= bkt.p_learned <= 1.0

    def test_bkt_converges_to_mastery(self):
        """Test BKT converges toward 1.0 with consecutive correct answers."""
        bkt = BayesianKnowledgeTracing()

        # Simulate 5 consecutive correct answers
        for _ in range(5):
            bkt.update(is_correct=True)

        # Should be close to mastery
        assert bkt.p_learned > 0.8

    def test_bkt_converges_to_not_learned(self):
        """Test BKT converges toward 0.0 with consecutive incorrect answers."""
        bkt = BayesianKnowledgeTracing()
        bkt.p_learned = 0.5  # Start from middle

        # Simulate 5 consecutive incorrect answers
        for _ in range(5):
            bkt.update(is_correct=False)

        # Should be close to not learned
        assert bkt.p_learned < 0.3

    def test_get_mastery_level(self):
        """Test mastery level calculation from probability."""
        bkt = BayesianKnowledgeTracing()

        # Test different probability levels
        bkt.p_learned = 0.05
        assert bkt.get_mastery_level() == "NOT_STARTED"

        bkt.p_learned = 0.25
        assert bkt.get_mastery_level() == "ATTEMPTED"

        bkt.p_learned = 0.50
        assert bkt.get_mastery_level() == "FAMILIAR"

        bkt.p_learned = 0.75
        assert bkt.get_mastery_level() == "PROFICIENT"

        bkt.p_learned = 0.95
        assert bkt.get_mastery_level() == "MASTERED"


class TestErrorClassification:
    """Test suite for error classification logic."""

    def test_classify_resource_error(self):
        """Test classification of resource errors (missing prerequisites)."""
        classifier = ErrorClassification()

        # Wrong answer with specific misconception pattern
        classification = classifier.classify(
            is_correct=False,
            target_misconception_id="MATH-FRAC-DENOM-01",
            response_time_ms=8000,
            difficulty_level=3,
        )

        assert classification == "RESOURCE"

    def test_classify_process_error(self):
        """Test classification of process errors (methodology misunderstanding)."""
        classifier = ErrorClassification()

        # Wrong answer with procedural misconception
        classification = classifier.classify(
            is_correct=False,
            target_misconception_id="MATH-FRAC-ADD-01",
            response_time_ms=25000,
            difficulty_level=3,
        )

        assert classification == "PROCESS"

    def test_classify_incidental_error(self):
        """Test classification of incidental errors (carelessness)."""
        classifier = ErrorClassification()

        # Very fast wrong answer suggests carelessness
        classification = classifier.classify(
            is_correct=False,
            target_misconception_id=None,
            response_time_ms=2000,
            difficulty_level=5,
        )

        assert classification == "INCIDENTAL"

    def test_classify_none_for_correct(self):
        """Test that correct answers have no error classification."""
        classifier = ErrorClassification()

        classification = classifier.classify(
            is_correct=True,
            target_misconception_id=None,
            response_time_ms=10000,
            difficulty_level=3,
        )

        assert classification == "NONE"


class TestQuestionSelector:
    """Test suite for adaptive question selection."""

    def test_select_initial_question(self):
        """Test selection of first question (medium difficulty)."""
        selector = QuestionSelector()

        questions = [
            {"id": "q1", "difficulty_level": 2},
            {"id": "q2", "difficulty_level": 5},
            {"id": "q3", "difficulty_level": 8},
        ]

        selected = selector.select_next_question(
            questions=questions,
            answered_question_ids=[],
            current_mastery=0.0,
            target_misconceptions=[],
        )

        assert selected is not None
        assert selected["difficulty_level"] == 5  # Should start with medium

    def test_increase_difficulty_after_correct(self):
        """Test difficulty increases after correct answer."""
        selector = QuestionSelector()

        questions = [
            {"id": "q1", "difficulty_level": 3},
            {"id": "q2", "difficulty_level": 5},
            {"id": "q3", "difficulty_level": 7},
        ]

        selected = selector.select_next_question(
            questions=questions,
            answered_question_ids=["q1"],
            current_mastery=0.6,
            target_misconceptions=[],
        )

        # After showing mastery (0.6), should select harder question
        assert selected["difficulty_level"] > 3

    def test_decrease_difficulty_after_incorrect(self):
        """Test difficulty decreases after incorrect answer."""
        selector = QuestionSelector()

        questions = [
            {"id": "q1", "difficulty_level": 8},
            {"id": "q2", "difficulty_level": 5},
            {"id": "q3", "difficulty_level": 3},
        ]

        selected = selector.select_next_question(
            questions=questions,
            answered_question_ids=["q1"],
            current_mastery=0.2,
            target_misconceptions=["MATH-FRAC-01"],
        )

        # After low mastery, should select easier question
        assert selected["difficulty_level"] < 8

    def test_target_misconception_questions(self):
        """Test selection prioritizes questions targeting identified misconceptions."""
        selector = QuestionSelector()

        questions = [
            {"id": "q1", "difficulty_level": 5, "target_misconception_id": "MATH-FRAC-01"},
            {"id": "q2", "difficulty_level": 5, "target_misconception_id": None},
            {"id": "q3", "difficulty_level": 5, "target_misconception_id": "MATH-DIV-01"},
        ]

        selected = selector.select_next_question(
            questions=questions,
            answered_question_ids=[],
            current_mastery=0.5,
            target_misconceptions=["MATH-FRAC-01"],
        )

        # Should prioritize question targeting the misconception
        assert selected["target_misconception_id"] == "MATH-FRAC-01"

    def test_avoid_repeating_questions(self):
        """Test that answered questions are not repeated."""
        selector = QuestionSelector()

        questions = [
            {"id": "q1", "difficulty_level": 5},
            {"id": "q2", "difficulty_level": 5},
        ]

        selected = selector.select_next_question(
            questions=questions,
            answered_question_ids=["q1"],
            current_mastery=0.5,
            target_misconceptions=[],
        )

        assert selected["id"] == "q2"

    def test_return_none_when_no_questions(self):
        """Test returns None when all questions answered."""
        selector = QuestionSelector()

        questions = [
            {"id": "q1", "difficulty_level": 5},
        ]

        selected = selector.select_next_question(
            questions=questions,
            answered_question_ids=["q1"],
            current_mastery=0.5,
            target_misconceptions=[],
        )

        assert selected is None


class TestRemediationGroup:
    """Test suite for remediation group assignment."""

    def test_assign_group_a_mastery(self):
        """Test Group A assignment for high mastery."""
        assigner = RemediationGroup()

        group = assigner.assign(
            mastery_probability=0.85,
            correct_answers=8,
            total_questions=10,
        )

        assert group == "A"

    def test_assign_group_b_partial(self):
        """Test Group B assignment for partial mastery."""
        assigner = RemediationGroup()

        group = assigner.assign(
            mastery_probability=0.55,
            correct_answers=5,
            total_questions=10,
        )

        assert group == "B"

    def test_assign_group_c_no_mastery(self):
        """Test Group C assignment for low mastery."""
        assigner = RemediationGroup()

        group = assigner.assign(
            mastery_probability=0.25,
            correct_answers=2,
            total_questions=10,
        )

        assert group == "C"


class TestDiagnosticEngine:
    """Test suite for main diagnostic engine."""

    def test_start_session(self):
        """Test starting a new diagnostic session."""
        engine = DiagnosticEngine()

        session_id = uuid4()
        student_id = uuid4()
        module_id = uuid4()

        session = engine.start_session(
            session_id=session_id,
            student_id=student_id,
            module_id=module_id,
        )

        assert session["id"] == session_id
        assert session["student_id"] == student_id
        assert session["module_id"] == module_id
        assert "started_at" in session
        assert session["completed_at"] is None

    def test_process_answer_updates_bkt(self):
        """Test that processing an answer updates BKT state."""
        engine = DiagnosticEngine()

        session_id = uuid4()
        student_id = uuid4()
        module_id = uuid4()

        engine.start_session(
            session_id=session_id,
            student_id=student_id,
            module_id=module_id,
        )

        result = engine.process_answer(
            session_id=session_id,
            question_id=uuid4(),
            is_correct=True,
            response_time_ms=10000,
            target_misconception_id=None,
        )

        assert "error_classification" in result
        assert result["error_classification"] == "NONE"

    def test_is_session_complete_true(self):
        """Test session completion detection."""
        engine = DiagnosticEngine()

        session_id = uuid4()
        engine.start_session(
            session_id=session_id,
            student_id=uuid4(),
            module_id=uuid4(),
        )

        # Simulate 10 answered questions (typical diagnostic length)
        for i in range(10):
            engine.process_answer(
                session_id=session_id,
                question_id=uuid4(),
                is_correct=True,
                response_time_ms=10000,
                target_misconception_id=None,
            )

        assert engine.is_session_complete(session_id) is True

    def test_get_results(self):
        """Test retrieving diagnostic results."""
        engine = DiagnosticEngine()

        session_id = uuid4()
        student_id = uuid4()
        module_id = uuid4()

        engine.start_session(
            session_id=session_id,
            student_id=student_id,
            module_id=module_id,
        )

        # Simulate some answers
        for i in range(5):
            engine.process_answer(
                session_id=session_id,
                question_id=uuid4(),
                is_correct=i % 2 == 0,
                response_time_ms=10000,
                target_misconception_id=None,
            )

        results = engine.get_results(session_id)

        assert "mastery_level" in results
        assert "recommended_group" in results
        assert "total_questions" in results
        assert "correct_answers" in results
        assert results["session_id"] == session_id
