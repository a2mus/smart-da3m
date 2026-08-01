"""Unit tests for pedagogical alert trigger thresholds and duplicate prevention (OQ-4).
"""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.models.alert import AlertSeverity, AlertTriggerType
from app.services.alert_manager import (
    AlertGenerator,
    AlertManager,
    ConsecutiveFailureDetector,
    ResponsePatternDetector,
)


def test_consecutive_failure_threshold_info():
    """Test 1st failure triggers INFO severity alert."""
    detector = ConsecutiveFailureDetector()
    answers = [
        {"is_correct": False, "misconception_id": "MISC_01", "timestamp": datetime.now(UTC).isoformat()}
    ]
    res = detector.detect(answers)
    assert res["triggered"] is True
    assert res["severity"] == AlertSeverity.INFO
    assert res["consecutive_failures"] == 1


def test_consecutive_failure_threshold_warning():
    """Test 2 failures within window trigger WARNING severity alert."""
    detector = ConsecutiveFailureDetector()
    answers = [
        {"is_correct": False, "misconception_id": "MISC_01", "timestamp": datetime.now(UTC).isoformat()},
        {"is_correct": False, "misconception_id": "MISC_01", "timestamp": datetime.now(UTC).isoformat()},
    ]
    res = detector.detect(answers)
    assert res["triggered"] is True
    assert res["severity"] == AlertSeverity.WARNING
    assert res["consecutive_failures"] == 2


def test_consecutive_failure_threshold_critical():
    """Test 3+ failures within window trigger CRITICAL severity alert."""
    detector = ConsecutiveFailureDetector()
    answers = [
        {"is_correct": False, "misconception_id": "MISC_01", "timestamp": datetime.now(UTC).isoformat()},
        {"is_correct": False, "misconception_id": "MISC_01", "timestamp": datetime.now(UTC).isoformat()},
        {"is_correct": False, "misconception_id": "MISC_01", "timestamp": datetime.now(UTC).isoformat()},
    ]
    res = detector.detect(answers)
    assert res["triggered"] is True
    assert res["severity"] == AlertSeverity.CRITICAL
    assert res["consecutive_failures"] == 3


def test_consecutive_failure_window_filtering():
    """Test failures outside 7-day window are ignored."""
    detector = ConsecutiveFailureDetector(window_days=7)
    old_ts = (datetime.now(UTC) - timedelta(days=10)).isoformat()
    recent_ts = datetime.now(UTC).isoformat()
    answers = [
        {"is_correct": False, "misconception_id": "MISC_01", "timestamp": old_ts},
        {"is_correct": False, "misconception_id": "MISC_01", "timestamp": old_ts},
        {"is_correct": False, "misconception_id": "MISC_01", "timestamp": recent_ts},
    ]
    res = detector.detect(answers)
    assert res["triggered"] is True
    assert res["severity"] == AlertSeverity.INFO
    assert res["consecutive_failures"] == 1


def test_passport_failure_severities():
    """Test passport failure 1st fail -> WARNING, 2nd fail -> CRITICAL."""
    manager = AlertManager()
    student_id = uuid4()

    warn_alert = manager.check_passport_failure(student_id, "COMP_MATH_01", fail_count=1)
    assert warn_alert is not None
    assert warn_alert["severity"] == AlertSeverity.WARNING

    generator = AlertGenerator(cooldown_hours=0)  # Bypass cooldown for test
    manager.generator = generator
    crit_alert = manager.check_passport_failure(student_id, "COMP_MATH_01", fail_count=2)
    assert crit_alert is not None
    assert crit_alert["severity"] == AlertSeverity.CRITICAL


def test_abandonment_severity_critical():
    """Test session abandonment triggers CRITICAL alert."""
    detector = ResponsePatternDetector()
    old_start = (datetime.now(UTC) - timedelta(minutes=40)).isoformat()
    session_data = {"started_at": old_start, "answers_count": 1, "expected_count": 10}
    res = detector.detect_abandonment(session_data)
    assert res["triggered"] is True
    assert res["severity"] == AlertSeverity.CRITICAL


def test_cooldown_duplicate_prevention():
    """Test alert generation is suppressed within cooldown window."""
    generator = AlertGenerator(cooldown_hours=24)
    student_id = uuid4()
    detection = {
        "triggered": True,
        "severity": AlertSeverity.WARNING,
        "trigger_type": AlertTriggerType.REPEATED_FAILURE,
        "misconception_id": "MISC_ADD_01",
    }

    first = generator.generate(student_id, detection)
    assert first is not None

    second = generator.generate(student_id, detection)
    assert second is None
