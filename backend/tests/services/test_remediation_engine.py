"""
Unit tests for dynamic difficulty algorithm (T030).
Tests remediation pathway generation and difficulty adaptation.
"""

import pytest
from uuid import uuid4

from app.services.remediation_engine import (
    DynamicDifficultyAdjuster,
    PathwayGenerator,
    PassportEvaluator,
    RemediationEngine,
    StudentEngagementTracker,
)


class TestDynamicDifficultyAdjuster:
    """Test suite for dynamic difficulty adjustment."""

    def test_increase_difficulty_when_fast_and_accurate(self):
        """Test difficulty increases when student responds quickly and accurately."""
        adjuster = DynamicDifficultyAdjuster()

        # Fast (2s), correct answer
        new_difficulty = adjuster.adjust(
            current_difficulty=5,
            response_time_ms=2000,
            is_correct=True,
            estimated_time_ms=10000,
        )

        assert new_difficulty > 5

    def test_decrease_difficulty_when_slow(self):
        """Test difficulty decreases when student responds slowly."""
        adjuster = DynamicDifficultyAdjuster()

        # Very slow (20s), correct answer
        new_difficulty = adjuster.adjust(
            current_difficulty=5,
            response_time_ms=20000,
            is_correct=True,
            estimated_time_ms=10000,
        )

        assert new_difficulty < 5

    def test_decrease_difficulty_when_incorrect(self):
        """Test difficulty decreases after incorrect answer."""
        adjuster = DynamicDifficultyAdjuster()

        new_difficulty = adjuster.adjust(
            current_difficulty=7,
            response_time_ms=8000,
            is_correct=False,
            estimated_time_ms=10000,
        )

        assert new_difficulty < 7

    def test_maintain_difficulty_when_appropriate(self):
        """Test difficulty stays same when performance is on target."""
        adjuster = DynamicDifficultyAdjuster()

        new_difficulty = adjuster.adjust(
            current_difficulty=5,
            response_time_ms=9500,  # Just under estimated time
            is_correct=True,
            estimated_time_ms=10000,
        )

        assert new_difficulty == 5

    def test_clamp_difficulty_to_valid_range(self):
        """Test difficulty stays within 1-10 range."""
        adjuster = DynamicDifficultyAdjuster()

        # Try to go below 1
        difficulty = adjuster.adjust(
            current_difficulty=1,
            response_time_ms=30000,
            is_correct=False,
            estimated_time_ms=5000,
        )
        assert difficulty == 1

        # Try to go above 10
        difficulty = adjuster.adjust(
            current_difficulty=10,
            response_time_ms=1000,
            is_correct=True,
            estimated_time_ms=30000,
        )
        assert difficulty == 10


class TestStudentEngagementTracker:
    """Test suite for engagement tracking."""

    def test_detect_frustration_declining_speed(self):
        """Test frustration detection from declining response speeds."""
        tracker = StudentEngagementTracker()

        # Record increasingly slower responses
        tracker.record_response(5000, True)
        tracker.record_response(8000, True)
        tracker.record_response(12000, False)

        assert tracker.is_frustrated() is True

    def test_detect_boredom_fast_accurate_responses(self):
        """Test boredom detection from very fast accurate responses."""
        tracker = StudentEngagementTracker()

        # Record very fast correct responses
        tracker.record_response(2000, True)
        tracker.record_response(1500, True)
        tracker.record_response(1800, True)

        assert tracker.is_bored() is True

    def test_detect_normal_engagement(self):
        """Test normal engagement state."""
        tracker = StudentEngagementTracker()

        # Normal varied responses
        tracker.record_response(8000, True)
        tracker.record_response(10000, False)
        tracker.record_response(9000, True)

        assert tracker.is_frustrated() is False
        assert tracker.is_bored() is False

    def test_get_engagement_recommendation(self):
        """Test getting recommendations based on engagement."""
        tracker = StudentEngagementTracker()

        # Bored student
        tracker.record_response(2000, True)
        tracker.record_response(1500, True)

        rec = tracker.get_recommendation()
        assert rec["action"] == "increase_difficulty"


class TestPathwayGenerator:
    """Test suite for remediation pathway generation."""

    def test_generate_pathway_for_competency(self):
        """Test pathway generation targets specific competency."""
        generator = PathwayGenerator()

        atoms = [
            {"id": "a1", "competency_id": "MATH-4-FRAC-01", "remediation_type": "AUDIO_VISUAL"},
            {"id": "a2", "competency_id": "MATH-4-FRAC-01", "remediation_type": "SIMULATION"},
            {"id": "a3", "competency_id": "MATH-4-DIV-01", "remediation_type": "MIND_MAP"},
        ]

        pathway = generator.generate(
            competency_id="MATH-4-FRAC-01",
            student_group="B",
            available_atoms=atoms,
        )

        # Should only include atoms for target competency
        assert len(pathway) == 2
        assert all(a["competency_id"] == "MATH-4-FRAC-01" for a in pathway)

    def test_order_atoms_by_type_for_group_b(self):
        """Test Group B gets atoms in optimal learning order."""
        generator = PathwayGenerator()

        atoms = [
            {"id": "a1", "competency_id": "TEST-01", "remediation_type": "SIMULATION"},
            {"id": "a2", "competency_id": "TEST-01", "remediation_type": "AUDIO_VISUAL"},
            {"id": "a3", "competency_id": "TEST-01", "remediation_type": "MIND_MAP"},
        ]

        pathway = generator.generate(
            competency_id="TEST-01",
            student_group="B",
            available_atoms=atoms,
        )

        # Group B: Start with AUDIO_VISUAL, then SIMULATION, then MIND_MAP
        assert pathway[0]["remediation_type"] == "AUDIO_VISUAL"

    def test_group_c_gets_more_atoms(self):
        """Test Group C (no mastery) gets more intensive pathway."""
        generator = PathwayGenerator()

        atoms = [
            {"id": f"a{i}", "competency_id": "TEST-01", "remediation_type": t}
            for i, t in enumerate(["AUDIO_VISUAL", "SIMULATION", "MIND_MAP", "AUDIO_VISUAL", "SIMULATION"])
        ]

        pathway_b = generator.generate("TEST-01", "B", atoms)
        pathway_c = generator.generate("TEST-01", "C", atoms)

        # Group C should get more atoms than Group B
        assert len(pathway_c) > len(pathway_b)


class TestPassportEvaluator:
    """Test suite for Passport assessment evaluation."""

    def test_pass_when_meets_threshold(self):
        """Test student passes when accuracy meets threshold."""
        evaluator = PassportEvaluator()

        answers = [
            {"question_id": "q1", "is_correct": True},
            {"question_id": "q2", "is_correct": True},
            {"question_id": "q3", "is_correct": False},
            {"question_id": "q4", "is_correct": True},
            {"question_id": "q5", "is_correct": True},
        ]

        result = evaluator.evaluate(answers, passing_threshold=0.7)

        assert result["passed"] is True
        assert result["accuracy"] == 0.8

    def test_fail_when_below_threshold(self):
        """Test student fails when accuracy below threshold."""
        evaluator = PassportEvaluator()

        answers = [
            {"question_id": "q1", "is_correct": True},
            {"question_id": "q2", "is_correct": False},
            {"question_id": "q3", "is_correct": False},
            {"question_id": "q4", "is_correct": False},
            {"question_id": "q5", "is_correct": True},
        ]

        result = evaluator.evaluate(answers, passing_threshold=0.7)

        assert result["passed"] is False
        assert result["accuracy"] == 0.4

    def test_update_mastery_level_on_pass(self):
        """Test mastery level advances on passing."""
        evaluator = PassportEvaluator()

        result = evaluator.calculate_new_mastery(
            current_mastery="FAMILIAR",
            passed=True,
            accuracy=0.85,
        )

        assert result == "PROFICIENT"

    def test_regression_on_fail(self):
        """Test mastery level regresses on failing."""
        evaluator = PassportEvaluator()

        result = evaluator.calculate_new_mastery(
            current_mastery="PROFICIENT",
            passed=False,
            accuracy=0.4,
        )

        assert result == "FAMILIAR"


class TestRemediationEngine:
    """Test suite for main remediation engine."""

    def test_start_remediation_path(self):
        """Test starting a new remediation path."""
        engine = RemediationEngine()

        student_id = uuid4()
        competency_id = "MATH-4-FRAC-01"

        path = engine.start_path(
            student_id=student_id,
            competency_id=competency_id,
            student_group="B",
        )

        assert path["student_id"] == student_id
        assert path["competency_id"] == competency_id
        assert path["status"] == "IN_PROGRESS"
        assert "atoms" in path

    def test_get_next_atom(self):
        """Test getting next atom in pathway."""
        engine = RemediationEngine()

        student_id = uuid4()
        engine.start_path(student_id, "TEST-01", "B")

        atom = engine.get_next_atom(student_id, "TEST-01")

        assert atom is not None
        assert "id" in atom
        assert "content" in atom

    def test_complete_atom(self):
        """Test marking an atom as complete."""
        engine = RemediationEngine()

        student_id = uuid4()
        path = engine.start_path(student_id, "TEST-01", "B")

        first_atom = path["atoms"][0]
        result = engine.complete_atom(
            student_id=student_id,
            competency_id="TEST-01",
            atom_id=first_atom["id"],
            performance_data={"time_ms": 5000, "interactions": 3},
        )

        assert result["atoms_completed"] == 1
        assert result["progress_percent"] > 0

    def test_is_pathway_complete(self):
        """Test pathway completion detection."""
        engine = RemediationEngine()

        student_id = uuid4()
        engine.start_path(student_id, "TEST-01", "B")

        # Initially not complete
        assert engine.is_pathway_complete(student_id, "TEST-01") is False

    def test_generate_passport_questions(self):
        """Test generating Passport assessment questions."""
        engine = RemediationEngine()

        questions = engine.generate_passport_questions(
            competency_id="TEST-01",
            count=5,
        )

        assert len(questions) == 5
        assert all("id" in q for q in questions)
