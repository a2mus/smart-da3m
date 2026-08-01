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
