"""
Stateless diagnostic engine components per AD-1.
All classes and functions are stateless and take state via parameters.
"""

import enum
import random
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.engines.bkt import get_mastery_level, update_mastery


class ErrorClassificationEnum(str, enum.Enum):
    """Error classification for diagnostic answers."""

    RESOURCE = "RESOURCE"
    PROCESS = "PROCESS"
    INCIDENTAL = "INCIDENTAL"
    NONE = "NONE"


class RemediationGroupEnum(str, enum.Enum):
    """Remediation group assignment based on diagnostic results."""

    A = "A"
    B = "B"
    C = "C"


class ErrorClassification:
    """
    Classifies student errors into categories (stateless).
    """

    def classify(
        self,
        is_correct: bool,
        target_misconception_id: Optional[str],
        response_time_ms: int,
        difficulty_level: int,
    ) -> str:
        """
        Classify the error based on answer correctness, timing, and misconception tags.
        """
        if is_correct:
            return ErrorClassificationEnum.NONE

        # Very fast wrong answers suggest carelessness (< 4 seconds)
        if response_time_ms < 4000:
            return ErrorClassificationEnum.INCIDENTAL

        # Slow response time (> 20 seconds) suggests process/procedural difficulty
        if response_time_ms > 20000:
            return ErrorClassificationEnum.PROCESS

        # Wrong answers targeting specific misconceptions suggest resource gap
        if target_misconception_id:
            return ErrorClassificationEnum.RESOURCE

        return ErrorClassificationEnum.PROCESS


class QuestionSelector:
    def select_next_question(
        self,
        questions: List[Dict[str, Any]],
        answered_question_ids: List[str],
        current_mastery: float,
        target_misconceptions: List[str],
        due_review_question_ids: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        review_ids = [str(rid) for rid in (due_review_question_ids or [])]
        available = [
            q for q in questions if str(q.get("id")) not in [str(aid) for aid in answered_question_ids]
        ]

        if not available:
            return None

        if current_mastery == 0.0:
            target_difficulty = 5
        else:
            target_difficulty = min(10, max(1, int(current_mastery * 10) + 1))

        def score_question(q: Dict[str, Any]) -> float:
            score = 0.0
            qid = str(q.get("id", ""))

            if qid in review_ids:
                score += 100

            q_difficulty = q.get("difficulty_level", 5)
            difficulty_diff = abs(q_difficulty - target_difficulty)
            score -= difficulty_diff * 10

            q_misconception = q.get("target_misconception_id")
            if q_misconception and q_misconception in target_misconceptions:
                score += 50

            return score

        available.sort(key=score_question, reverse=True)
        selected = dict(available[0])
        selected["is_review"] = str(selected.get("id")) in review_ids
        return selected


class MultiArmBanditSelector:
    """
    Multi-arm bandit question selection (Thompson Sampling, stateless).
    Accepts question_stats parameter rather than storing self.question_stats.
    """

    def select_next_question(
        self,
        questions: List[Dict[str, Any]],
        answered_question_ids: List[str],
        current_mastery: float,
        target_misconceptions: List[str],
        question_stats: Optional[Dict[str, Dict[str, int]]] = None,
        exploration_weight: float = 0.3,
    ) -> Optional[Dict[str, Any]]:
        """
        Select question using Thompson Sampling with exploration bonus.
        """
        stats_map = question_stats or {}
        available = [
            q for q in questions if str(q.get("id")) not in [str(aid) for aid in answered_question_ids]
        ]

        if not available:
            return None

        target_difficulty = min(10, max(1, int(current_mastery * 10) + 1))

        def score_question(q: Dict[str, Any]) -> float:
            score = 0.0
            qid = str(q.get("id", ""))

            if qid in stats_map:
                stats = stats_map[qid]
                if stats.get("total", 0) > 0:
                    success_rate = stats.get("success", 0) / stats["total"]
                    score += success_rate * 30

            q_difficulty = q.get("difficulty_level", 5)
            difficulty_diff = abs(q_difficulty - target_difficulty)
            score -= difficulty_diff * 8

            q_misconception = q.get("target_misconception_id")
            if q_misconception and q_misconception in target_misconceptions:
                score += 40

            total_uses = stats_map.get(qid, {}).get("total", 0)
            exploration_bonus = exploration_weight * (1.0 / (1.0 + total_uses))
            score += exploration_bonus * 20

            score += random.uniform(-5, 5)

            return score

        available.sort(key=score_question, reverse=True)
        return available[0]


class RemediationGroup:
    """
    Assigns students to remediation groups based on performance (stateless).
    """

    def assign(
        self,
        mastery_probability: float,
        correct_answers: int,
        total_questions: int,
    ) -> str:
        """
        Assign remediation group (A, B, or C).
        """
        accuracy = correct_answers / total_questions if total_questions > 0 else 0.0

        if mastery_probability >= 0.75 and accuracy >= 0.7:
            return RemediationGroupEnum.A

        if mastery_probability < 0.4 or accuracy < 0.4:
            return RemediationGroupEnum.C

        return RemediationGroupEnum.B


class DiagnosticEngine:
    """
    Stateless diagnostic engine coordinating BKT, question selection, and evaluation.
    Holds no session state or bkt_models dictionaries per AD-1.
    """

    def __init__(self):
        self.error_classifier = ErrorClassification()
        self.question_selector = QuestionSelector()
        self.group_assigner = RemediationGroup()

    def process_answer(
        self,
        current_p_learned: float,
        is_correct: bool,
        response_time_ms: int,
        difficulty_level: int = 5,
        target_misconception_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process an answer statelessly given current P(learned).
        """
        error_classification = self.error_classifier.classify(
            is_correct=is_correct,
            target_misconception_id=target_misconception_id,
            response_time_ms=response_time_ms,
            difficulty_level=difficulty_level,
        )

        new_p_learned = update_mastery(current_p_learned, is_correct)
        mastery_lvl = get_mastery_level(new_p_learned)

        return {
            "error_classification": error_classification,
            "current_mastery": new_p_learned,
            "mastery_level": mastery_lvl,
        }

    def is_session_complete(
        self,
        answers_count: int,
        current_p_learned: float,
        min_questions: int = 10,
        max_questions: int = 15,
    ) -> bool:
        """
        Statelessly check if a diagnostic session should complete.
        """
        if answers_count < min_questions:
            return False

        if answers_count >= max_questions:
            return True

        if current_p_learned > 0.9 or current_p_learned < 0.1:
            return True

        return False

    def evaluate_session_results(
        self,
        session_id: UUID,
        final_p_learned: float,
        correct_count: int,
        total_count: int,
    ) -> Dict[str, Any]:
        """
        Statelessly calculate final session evaluation results.
        """
        recommended_group = self.group_assigner.assign(
            mastery_probability=final_p_learned,
            correct_answers=correct_count,
            total_questions=total_count,
        )

        mastery_lvl = get_mastery_level(final_p_learned)
        accuracy = correct_count / total_count if total_count > 0 else 0.0

        return {
            "session_id": session_id,
            "mastery_probability": final_p_learned,
            "mastery_level": mastery_lvl,
            "recommended_group": recommended_group,
            "total_questions": total_count,
            "correct_answers": correct_count,
            "accuracy": accuracy,
        }
