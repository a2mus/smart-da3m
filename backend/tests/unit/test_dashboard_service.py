"""
Unit tests for DashboardService.generate_insights (Story 8.3: Smart Insight Messages - Zero Raw Scores).
"""

import pytest
from unittest.mock import MagicMock
from app.services.dashboard_service import DashboardAggregator
from app.models.diagnostic import MasteryLevel


def test_generate_insights_empty_profiles():
    service = DashboardAggregator(db=MagicMock())
    insights = service.generate_insights([])
    assert len(insights) == 1
    assert insights[0]["type"] == "GENERAL"
    assert "hasn't completed" in insights[0]["text"]
    assert "%" not in insights[0]["text"]


def test_generate_insights_strengths_and_gaps():
    service = DashboardAggregator(db=MagicMock())
    profiles = [
        {"competency_id": "ARAB_TAA_MARBUTA", "mastery_level": "MASTERED"},
        {"competency_id": "MATH_ADDITION", "mastery_level": "ATTEMPTED"},
    ]
    insights = service.generate_insights(profiles)

    assert len(insights) == 2
    types = [i["type"] for i in insights]
    assert "STRENGTH" in types
    assert "GAP" in types

    strength = next(i for i in insights if i["type"] == "STRENGTH")
    gap = next(i for i in insights if i["type"] == "GAP")

    assert strength["competency_id"] == "ARAB_TAA_MARBUTA"
    assert "تاء مربوطة" in strength["competency_name"]
    assert gap["competency_id"] == "MATH_ADDITION"

    for insight in insights:
        text = insight["text"]
        assert "%" not in text
        assert "/10" not in text


def test_generate_insights_mastery_level_enum():
    service = DashboardAggregator(db=MagicMock())

    class MockProfile:
        def __init__(self, competency_id, mastery_level):
            self.competency_id = competency_id
            self.mastery_level = mastery_level

    profiles = [
        MockProfile("FREN_GRAMMAR", MasteryLevel.PROFICIENT),
        MockProfile("SCI_LIVING_THINGS", MasteryLevel.NOT_STARTED),
    ]

    insights = service.generate_insights(profiles)
    assert len(insights) == 2

    for insight in insights:
        assert insight["text"] != ""
        assert "%" not in insight["text"]
