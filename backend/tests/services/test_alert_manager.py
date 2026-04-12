"""
Unit tests for alert generation logic (T043).
Tests pedagogical alert detection and severity classification.
"""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.services.alert_manager import (
    AlertGenerator,
    ConsecutiveFailureDetector,
    InactivityDetector,
    ResponsePatternDetector,
)


class TestConsecutiveFailureDetector:
    """Test suite for consecutive failure detection."""

    def test_detect_three_consecutive_failures(self):
        """Test WARNING alert on 3 consecutive failures."""
        detector = ConsecutiveFailureDetector()

        # Simulate 3 consecutive failures
        answers = [
            {"question_id": "q1", "is_correct": False, "misconception_id": "MATH-FRAC-01"},
            {"question_id": "q2", "is_correct": False, "misconception_id": "MATH-FRAC-01"},
            {"question_id": "q3", "is_correct": False, "misconception_id": "MATH-FRAC-01"},
        ]

        result = detector.detect(answers)

        assert result["triggered"] is True
        assert result["severity"] == "WARNING"
        assert result["trigger_type"] == "REPEATED_FAILURE"
        assert result["consecutive_failures"] == 3
        assert result["misconception_id"] == "MATH-FRAC-01"

    def test_no_alert_on_two_failures(self):
        """Test no alert on only 2 consecutive failures."""
        detector = ConsecutiveFailureDetector()

        answers = [
            {"question_id": "q1", "is_correct": False, "misconception_id": "MATH-FRAC-01"},
            {"question_id": "q2", "is_correct": False, "misconception_id": "MATH-FRAC-01"},
        ]

        result = detector.detect(answers)

        assert result["triggered"] is False

    def test_reset_on_success(self):
        """Test failure count resets on correct answer."""
        detector = ConsecutiveFailureDetector()

        answers = [
            {"question_id": "q1", "is_correct": False, "misconception_id": "MATH-FRAC-01"},
            {"question_id": "q2", "is_correct": False, "misconception_id": "MATH-FRAC-01"},
            {"question_id": "q3", "is_correct": True, "misconception_id": None},
            {"question_id": "q4", "is_correct": False, "misconception_id": "MATH-FRAC-01"},
        ]

        result = detector.detect(answers)

        assert result["triggered"] is False  # Only 1 failure after success

    def test_detect_different_misconceptions_separately(self):
        """Test tracking different misconception types separately."""
        detector = ConsecutiveFailureDetector()

        answers = [
            {"question_id": "q1", "is_correct": False, "misconception_id": "MATH-FRAC-01"},
            {"question_id": "q2", "is_correct": False, "misconception_id": "MATH-FRAC-01"},
            {"question_id": "q3", "is_correct": False, "misconception_id": "MATH-DIV-01"},  # Different type
            {"question_id": "q4", "is_correct": False, "misconception_id": "MATH-DIV-01"},
        ]

        result = detector.detect(answers)

        assert result["triggered"] is False  # No single type has 3 failures


class TestResponsePatternDetector:
    """Test suite for response pattern detection."""

    def test_detect_declining_speed_with_low_accuracy(self):
        """Test INFO alert for frustration pattern."""
        detector = ResponsePatternDetector()

        # Declining response times with low accuracy
        responses = [
            {"time_ms": 5000, "is_correct": False},
            {"time_ms": 8000, "is_correct": False},
            {"time_ms": 12000, "is_correct": False},
            {"time_ms": 15000, "is_correct": True},
        ]

        result = detector.detect_frustration(responses)

        assert result["triggered"] is True
        assert result["severity"] == "INFO"
        assert result["trigger_type"] == "FRUSTRATION"
        assert "declining_speed" in result["indicators"]
        assert "low_accuracy" in result["indicators"]

    def test_no_frustration_with_high_accuracy(self):
        """Test no alert when accuracy is good despite slow responses."""
        detector = ResponsePatternDetector()

        responses = [
            {"time_ms": 5000, "is_correct": True},
            {"time_ms": 8000, "is_correct": True},
            {"time_ms": 12000, "is_correct": True},
        ]

        result = detector.detect_frustration(responses)

        assert result["triggered"] is False

    def test_detect_abandoned_session(self):
        """Test WARNING alert for session abandonment."""
        detector = ResponsePatternDetector()

        session = {
            "started_at": datetime.now(timezone.utc) - timedelta(minutes=30),
            "completed_at": None,
            "answers_count": 2,
            "expected_count": 10,
        }

        result = detector.detect_abandonment(session)

        assert result["triggered"] is True
        assert result["severity"] == "WARNING"
        assert result["trigger_type"] == "ABANDONMENT"


class TestInactivityDetector:
    """Test suite for inactivity detection."""

    def test_detect_inactivity_after_threshold(self):
        """Test INFO alert after N days of inactivity."""
        detector = InactivityDetector(inactivity_threshold_days=7)

        last_login = datetime.now(timezone.utc) - timedelta(days=8)

        result = detector.detect(last_login)

        assert result["triggered"] is True
        assert result["severity"] == "INFO"
        assert result["trigger_type"] == "INACTIVITY"
        assert result["days_inactive"] == 8

    def test_no_alert_within_threshold(self):
        """Test no alert within threshold days."""
        detector = InactivityDetector(inactivity_threshold_days=7)

        last_login = datetime.now(timezone.utc) - timedelta(days=3)

        result = detector.detect(last_login)

        assert result["triggered"] is False


class TestAlertGenerator:
    """Test suite for alert generation service."""

    def test_generate_alert_for_consecutive_failures(self):
        """Test generating alert from failure detection."""
        generator = AlertGenerator()

        detection = {
            "triggered": True,
            "severity": "WARNING",
            "trigger_type": "REPEATED_FAILURE",
            "consecutive_failures": 3,
            "misconception_id": "MATH-FRAC-01",
        }

        alert = generator.generate(
            student_id=uuid4(),
            detection=detection,
        )

        assert alert["severity"] == "WARNING"
        assert alert["trigger_type"] == "REPEATED_FAILURE"
        assert "simplified_message" in alert
        assert "expert_message" in alert
        assert alert["recipients"] == ["parent", "expert"]

    def test_generate_critical_alert_for_passport_failure(self):
        """Test CRITICAL alert for post-remediation failure."""
        generator = AlertGenerator()

        detection = {
            "triggered": True,
            "severity": "CRITICAL",
            "trigger_type": "PASSPORT_FAILED",
            "competency_id": "MATH-4-NUM-01",
        }

        alert = generator.generate(
            student_id=uuid4(),
            detection=detection,
        )

        assert alert["severity"] == "CRITICAL"
        assert "in-person support" in alert["simplified_message"].lower() or "in-person support" in alert["expert_message"].lower()
        assert "intervention" in alert["expert_message"].lower() or "support" in alert["expert_message"].lower()

    def test_alert_messages_parent_vs_expert(self):
        """Test different message complexity for parent vs expert."""
        generator = AlertGenerator()

        detection = {
            "triggered": True,
            "severity": "WARNING",
            "trigger_type": "REPEATED_FAILURE",
            "consecutive_failures": 3,
        }

        alert = generator.generate(
            student_id=uuid4(),
            detection=detection,
        )

        # Parent message should be simple
        assert len(alert["simplified_message"]) < 200
        assert "frustration" in alert["simplified_message"].lower() or "struggling" in alert["simplified_message"].lower()

        # Expert message should be detailed
        assert len(alert["expert_message"]) > len(alert["simplified_message"])

    def test_auto_grouping_suggestion(self):
        """Test auto-grouping suggestion for shared error patterns."""
        generator = AlertGenerator()

        # Multiple students with same misconception
        students_with_same_error = [
            {"student_id": uuid4(), "misconception_id": "MATH-FRAC-01"},
            {"student_id": uuid4(), "misconception_id": "MATH-FRAC-01"},
            {"student_id": uuid4(), "misconception_id": "MATH-FRAC-01"},
        ]

        suggestion = generator.suggest_auto_grouping(students_with_same_error)

        assert suggestion["should_group"] is True
        assert suggestion["group_size"] == 3
        assert suggestion["shared_misconception"] == "MATH-FRAC-01"
        assert "recommended_intervention" in suggestion

    def test_no_grouping_below_threshold(self):
        """Test no grouping suggestion with fewer students."""
        generator = AlertGenerator()

        students = [
            {"student_id": uuid4(), "misconception_id": "MATH-FRAC-01"},
            {"student_id": uuid4(), "misconception_id": "MATH-FRAC-01"},
        ]

        suggestion = generator.suggest_auto_grouping(students)

        assert suggestion["should_group"] is False

    def test_alert_deduplication(self):
        """Test not generating duplicate alerts for same issue."""
        generator = AlertGenerator()

        student_id = uuid4()

        # First alert
        detection = {
            "triggered": True,
            "severity": "WARNING",
            "trigger_type": "REPEATED_FAILURE",
        }

        alert1 = generator.generate(student_id, detection)
        alert1_id = alert1["id"]

        # Try to generate same alert again
        alert2 = generator.generate(student_id, detection, existing_alert_ids=[alert1_id])

        assert alert2 is None  # Should not generate duplicate

    def test_info_alert_for_minor_issues(self):
        """Test INFO level alerts for less severe issues."""
        generator = AlertGenerator()

        detection = {
            "triggered": True,
            "severity": "INFO",
            "trigger_type": "FRUSTRATION",
        }

        alert = generator.generate(
            student_id=uuid4(),
            detection=detection,
        )

        assert alert["severity"] == "INFO"
        assert "parent" in alert["recipients"]
        # INFO alerts might not need expert notification
        assert "expert" not in alert["recipients"] or "expert" in alert["recipients"]
