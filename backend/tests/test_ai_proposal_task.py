"""
Unit tests for Celery AI proposal task and LiteLLM integration fallback.
"""

import sys
from unittest.mock import MagicMock, patch

from app.tasks.ai_proposal import _call_litellm_augmentation, generate_remediation_proposal


def test_generate_remediation_proposal_deterministic_fallback():
    """Test proposal generation when LiteLLM raises an exception or is unavailable."""
    sample_atoms = [
        {"id": "atom-1", "competency_id": "MATH_ADD_01", "remediation_type": "AUDIO_VISUAL"},
        {"id": "atom-2", "competency_id": "MATH_ADD_01", "remediation_type": "SIMULATION"},
    ]

    with patch("app.tasks.ai_proposal._call_litellm_augmentation") as mock_litellm:
        mock_litellm.side_effect = lambda competency_id, atoms, gap_profile: atoms

        result = generate_remediation_proposal(
            session_id="session-123",
            competency_id="MATH_ADD_01",
            student_group="C",
            available_atoms=sample_atoms,
        )

        assert result["status"] == "PROPOSED"
        assert result["competency_id"] == "MATH_ADD_01"
        assert result["atoms_count"] == 2
        assert len(result["atoms"]) == 2


def test_litellm_augmentation_success():
    """Test LiteLLM augmentation when completion succeeds."""
    sample_atoms = [
        {"id": "atom-1", "competency_id": "MATH_ADD_01", "remediation_type": "AUDIO_VISUAL"}
    ]

    mock_litellm = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Pedagogical focus on concrete counting."
    mock_litellm.completion.return_value = mock_response

    with patch.dict(sys.modules, {"litellm": mock_litellm}):
        augmented = _call_litellm_augmentation("MATH_ADD_01", sample_atoms)
        assert len(augmented) == 1
        assert "ai_pedagogical_justification" in augmented[0]
        assert "Pedagogical focus" in augmented[0]["ai_pedagogical_justification"]


def test_litellm_augmentation_failure_fallback():
    """Test LiteLLM augmentation falls back to raw atoms on LiteLLM exception."""
    sample_atoms = [
        {"id": "atom-1", "competency_id": "MATH_ADD_01", "remediation_type": "AUDIO_VISUAL"}
    ]

    mock_litellm = MagicMock()
    mock_litellm.completion.side_effect = RuntimeError("LiteLLM API connection error")

    with patch.dict(sys.modules, {"litellm": mock_litellm}):
        augmented = _call_litellm_augmentation("MATH_ADD_01", sample_atoms)
        assert len(augmented) == 1
        assert augmented == sample_atoms
