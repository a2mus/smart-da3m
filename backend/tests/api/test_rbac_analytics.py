"""
Unit & API integration tests for RBAC role check enum case fix.
Verifies `require_expert` and RBAC authorization behavior.
"""

import pytest
from fastapi import HTTPException

from app.core.security import require_expert
from app.models.user import User, UserRole


def test_require_expert_with_expert_user():
    """Verify require_expert permits users with UserRole.EXPERT."""
    expert_user = User(role=UserRole.EXPERT)
    result = require_expert(expert_user)
    assert result == expert_user


def test_require_expert_with_student_user():
    """Verify require_expert rejects users with UserRole.STUDENT with 403."""
    student_user = User(role=UserRole.STUDENT)
    with pytest.raises(HTTPException) as exc_info:
        require_expert(student_user)
    assert exc_info.value.status_code == 403
    assert "Expert access required" in exc_info.value.detail


def test_require_expert_with_parent_user():
    """Verify require_expert rejects users with UserRole.PARENT with 403."""
    parent_user = User(role=UserRole.PARENT)
    with pytest.raises(HTTPException) as exc_info:
        require_expert(parent_user)
    assert exc_info.value.status_code == 403
    assert "Expert access required" in exc_info.value.detail


def test_require_expert_with_none():
    """Verify require_expert rejects None user with 403."""
    with pytest.raises(HTTPException) as exc_info:
        require_expert(None)
    assert exc_info.value.status_code == 403
    assert "Expert access required" in exc_info.value.detail


def test_metric_response_schema_fields():
    """Verify MetricResponse schema contains both mastery_speed and mastery_speed_days."""
    from app.schemas.analytics import MetricResponse

    metric = MetricResponse(
        gap_reduction_rate=85.0,
        mastery_speed=2.5,
        mastery_speed_days=2.5,
        retention_rate=90.0,
        effort_vs_results=0.8,
        resilience_score=75.0,
        total_students=10,
        total_assessments=50,
    )
    dump = metric.model_dump()
    assert dump["mastery_speed"] == 2.5
    assert dump["mastery_speed_days"] == 2.5

