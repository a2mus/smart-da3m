"""
Stateless remediation engine components per AD-1.
All classes and functions are stateless and take state via parameters.
"""

from typing import Any, Dict, List, Optional

from app.engines.bkt import MasteryLevel


class DynamicDifficultyAdjuster:
    """
    Adjusts difficulty dynamically based on student performance (stateless).
    """

    def adjust(
        self,
        current_difficulty: int,
        response_time_ms: int,
        is_correct: bool,
        estimated_time_ms: int,
    ) -> int:
        """
        Calculate new difficulty based on performance parameters.
        """
        new_difficulty = current_difficulty

        if is_correct:
            time_ratio = response_time_ms / estimated_time_ms if estimated_time_ms > 0 else 1.0

            if time_ratio < 0.3:
                new_difficulty += 2
            elif time_ratio < 0.7:
                new_difficulty += 1
        else:
            time_ratio = response_time_ms / estimated_time_ms if estimated_time_ms > 0 else 1.0

            if time_ratio < 0.5:
                new_difficulty -= 1
            else:
                new_difficulty -= 2

        return max(1, min(10, new_difficulty))


class StudentEngagementTracker:
    """
    Tracks student engagement patterns to detect frustration or boredom (stateless).
    Accepts response history as parameter.
    """

    def is_frustrated(self, responses: List[Dict[str, Any]]) -> bool:
        """Detect if student shows frustration signs based on recent responses."""
        recent = responses[-5:] if len(responses) > 5 else responses
        if len(recent) < 3:
            return False

        times = [r.get("time_ms", 0) for r in recent]
        correct_count = sum(1 for r in recent if r.get("is_correct"))

        is_slowing = times[-1] > times[0] * 1.5 if times[0] > 0 else False
        low_accuracy = correct_count < len(recent) * 0.5

        return is_slowing and low_accuracy

    def is_bored(self, responses: List[Dict[str, Any]]) -> bool:
        """Detect if student shows boredom signs (too fast, high accuracy)."""
        recent = responses[-5:] if len(responses) > 5 else responses
        if len(recent) < 3:
            return False

        times = [r.get("time_ms", 0) for r in recent]
        correct_count = sum(1 for r in recent if r.get("is_correct"))

        avg_time = sum(times) / len(times) if len(times) > 0 else 0
        high_accuracy = correct_count == len(recent)

        return avg_time < 3000 and high_accuracy

    def get_recommendation(self, responses: List[Dict[str, Any]]) -> Dict[str, str]:
        """Get recommendation based on engagement state."""
        if self.is_frustrated(responses):
            return {
                "action": "decrease_difficulty",
                "message": "Take a break and try a simpler exercise",
            }
        elif self.is_bored(responses):
            return {
                "action": "increase_difficulty",
                "message": "Great job! Let's try something more challenging",
            }
        else:
            return {"action": "maintain", "message": "Keep up the good work!"}


class PathwayGenerator:
    """
    Generates personalized remediation pathways (stateless).
    """

    def generate(
        self,
        competency_id: str,
        student_group: str,
        available_atoms: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Generate a remediation pathway list.
        """
        relevant_atoms = [
            a for a in available_atoms if a.get("competency_id") == competency_id
        ]

        if not relevant_atoms:
            return []

        type_priority = {
            "AUDIO_VISUAL": 1,
            "SIMULATION": 2,
            "MIND_MAP": 3,
        }

        relevant_atoms.sort(
            key=lambda a: type_priority.get(a.get("remediation_type"), 99)
        )

        if student_group == "C":
            return relevant_atoms
        elif student_group == "B":
            return relevant_atoms[::2] if len(relevant_atoms) > 3 else relevant_atoms
        else:  # Group A
            return relevant_atoms[:1] if relevant_atoms else []


class PassportEvaluator:
    """
    Evaluates Passport assessments and determines mastery progression (stateless).
    """

    def evaluate(
        self,
        answers: List[Dict[str, Any]],
        passing_threshold: float = 0.7,
    ) -> Dict[str, Any]:
        """Evaluate Passport assessment results."""
        if not answers:
            return {"passed": False, "accuracy": 0.0, "correct_count": 0, "total_questions": 0}

        correct_count = sum(1 for a in answers if a.get("is_correct"))
        total = len(answers)
        accuracy = correct_count / total

        return {
            "passed": accuracy >= passing_threshold,
            "accuracy": accuracy,
            "correct_count": correct_count,
            "total_questions": total,
        }

    def calculate_new_mastery(
        self,
        current_mastery: str,
        passed: bool,
        accuracy: float,
    ) -> str:
        """Calculate new mastery level based on Passport results."""
        mastery_order = [
            MasteryLevel.NOT_STARTED,
            MasteryLevel.ATTEMPTED,
            MasteryLevel.FAMILIAR,
            MasteryLevel.PROFICIENT,
            MasteryLevel.MASTERED,
        ]

        current_index = mastery_order.index(current_mastery) if current_mastery in mastery_order else 0

        if passed:
            if accuracy >= 0.75 and current_index < len(mastery_order) - 1:
                return mastery_order[current_index + 1]
            return current_mastery
        else:
            if current_index > 0:
                return mastery_order[current_index - 1]
            return current_mastery


class RemediationEngine:
    """
    Main stateless remediation engine coordinating pathway generation and assessment.
    Holds no in-memory self._paths state per AD-1.
    """

    def __init__(self):
        self.difficulty_adjuster = DynamicDifficultyAdjuster()
        self.engagement_tracker = StudentEngagementTracker()
        self.pathway_generator = PathwayGenerator()
        self.passport_evaluator = PassportEvaluator()

    def process_atom_completion(
        self,
        current_difficulty: int,
        performance_data: Dict[str, Any],
        atoms_completed_count: int,
        total_atoms: int,
    ) -> Dict[str, Any]:
        """
        Statelessly process an atom completion and calculate new state.
        """
        new_difficulty = self.difficulty_adjuster.adjust(
            current_difficulty=current_difficulty,
            response_time_ms=performance_data.get("time_ms", 10000),
            is_correct=performance_data.get("is_correct", True),
            estimated_time_ms=30000,
        )

        new_completed_count = atoms_completed_count + 1
        progress_percent = (
            (new_completed_count / total_atoms * 100.0) if total_atoms > 0 else 0.0
        )

        return {
            "atoms_completed": new_completed_count,
            "total_atoms": total_atoms,
            "progress_percent": progress_percent,
            "new_difficulty": new_difficulty,
        }

    def evaluate_passport(
        self,
        current_mastery: str,
        answers: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Statelessly evaluate a Passport assessment."""
        evaluation = self.passport_evaluator.evaluate(answers)
        new_mastery = self.passport_evaluator.calculate_new_mastery(
            current_mastery=current_mastery,
            passed=evaluation["passed"],
            accuracy=evaluation["accuracy"],
        )

        return {
            **evaluation,
            "new_mastery_level": new_mastery,
            "alert_triggered": not evaluation["passed"],
        }
