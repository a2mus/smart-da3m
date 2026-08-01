"""
Engines package containing stateless pure functions and domain logic.
Per AD-1, engines hold no in-memory state between calls.
"""

from app.engines.bkt import BKTParams, get_mastery_level, update_mastery
from app.engines.diagnostic_engine import (
    DiagnosticEngine,
    ErrorClassification,
    MultiArmBanditSelector,
    QuestionSelector,
    RemediationGroup,
)
from app.engines.remediation_engine import (
    DynamicDifficultyAdjuster,
    PassportEvaluator,
    PathwayGenerator,
    RemediationEngine,
    StudentEngagementTracker,
)

__all__ = [
    "BKTParams",
    "update_mastery",
    "get_mastery_level",
    "ErrorClassification",
    "QuestionSelector",
    "MultiArmBanditSelector",
    "RemediationGroup",
    "DiagnosticEngine",
    "DynamicDifficultyAdjuster",
    "StudentEngagementTracker",
    "PathwayGenerator",
    "PassportEvaluator",
    "RemediationEngine",
]
