"""
Remediation engine for personalized learning pathways and Passport assessments.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from app.models.diagnostic import MasteryLevel
from app.models.remediation import RemediationPathStatus


class DynamicDifficultyAdjuster:
    """
    Adjusts difficulty dynamically based on student performance.

    Adapts to:
    - Response time (too fast = bored, too slow = frustrated)
    - Answer correctness
    - Estimated time for question difficulty
    """

    def adjust(
        self,
        current_difficulty: int,
        response_time_ms: int,
        is_correct: bool,
        estimated_time_ms: int,
    ) -> int:
        """
        Calculate new difficulty based on performance.

        Args:
            current_difficulty: Current difficulty level (1-10)
            response_time_ms: Actual response time in ms
            is_correct: Whether answer was correct
            estimated_time_ms: Expected time for this difficulty

        Returns:
            New difficulty level (1-10)
        """
        new_difficulty = current_difficulty

        # Adjust based on correctness
        if is_correct:
            # Correct answer - consider increasing difficulty
            time_ratio = response_time_ms / estimated_time_ms

            if time_ratio < 0.3:
                # Very fast - student is bored, increase difficulty more
                new_difficulty += 2
            elif time_ratio < 0.7:
                # Good pace - slight increase
                new_difficulty += 1
            elif time_ratio > 1.5:
                # Slow but correct - maintain difficulty
                pass
        else:
            # Incorrect answer - decrease difficulty
            time_ratio = response_time_ms / estimated_time_ms

            if time_ratio < 0.5:
                # Fast wrong answer - careless error, slight decrease
                new_difficulty -= 1
            else:
                # Thought about it but wrong - bigger decrease
                new_difficulty -= 2

        # Clamp to valid range
        return max(1, min(10, new_difficulty))


class StudentEngagementTracker:
    """
    Tracks student engagement patterns to detect frustration or boredom.
    """

    def __init__(self, window_size: int = 5):
        self.responses: List[Dict[str, Any]] = []
        self.window_size = window_size

    def record_response(self, time_ms: int, is_correct: bool) -> None:
        """Record a response for tracking."""
        self.responses.append({"time_ms": time_ms, "is_correct": is_correct})

        # Keep only recent responses
        if len(self.responses) > self.window_size:
            self.responses = self.responses[-self.window_size:]

    def is_frustrated(self) -> bool:
        """Detect if student is showing frustration signs."""
        if len(self.responses) < 3:
            return False

        # Check for declining response times with increasing errors
        times = [r["time_ms"] for r in self.responses]
        correct_count = sum(1 for r in self.responses if r["is_correct"])

        # Declining speed + low accuracy = frustration
        if len(times) >= 3:
            is_slowing = times[-1] > times[0] * 1.5
            low_accuracy = correct_count < len(self.responses) * 0.5
            return is_slowing and low_accuracy

        return False

    def is_bored(self) -> bool:
        """Detect if student is bored (too fast, high accuracy)."""
        if len(self.responses) < 3:
            return False

        times = [r["time_ms"] for r in self.responses]
        correct_count = sum(1 for r in self.responses if r["is_correct"])

        # Very fast + high accuracy = boredom
        avg_time = sum(times) / len(times)
        high_accuracy = correct_count == len(self.responses)

        return avg_time < 3000 and high_accuracy

    def get_recommendation(self) -> Dict[str, str]:
        """Get recommendation based on engagement state."""
        if self.is_frustrated():
            return {
                "action": "decrease_difficulty",
                "message": "Take a break and try a simpler exercise",
            }
        elif self.is_bored():
            return {
                "action": "increase_difficulty",
                "message": "Great job! Let's try something more challenging",
            }
        else:
            return {"action": "maintain", "message": "Keep up the good work!"}


class PathwayGenerator:
    """
    Generates personalized remediation pathways.

    Creates ordered sequences of knowledge atoms based on:
    - Target competency
    - Student group (A, B, C)
    - Available atoms
    """

    def generate(
        self,
        competency_id: str,
        student_group: str,
        available_atoms: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Generate a remediation pathway.

        Args:
            competency_id: Target competency
            student_group: Remediation group (A, B, C)
            available_atoms: Available knowledge atoms

        Returns:
            Ordered list of atoms for the pathway
        """
        # Filter atoms for target competency
        relevant_atoms = [
            a for a in available_atoms if a.get("competency_id") == competency_id
        ]

        if not relevant_atoms:
            return []

        # Define atom type priority for learning progression
        type_priority = {
            "AUDIO_VISUAL": 1,
            "SIMULATION": 2,
            "MIND_MAP": 3,
        }

        # Sort by type priority
        relevant_atoms.sort(
            key=lambda a: type_priority.get(a.get("remediation_type"), 99)
        )

        # Group C gets all atoms (intensive), Group B gets subset
        if student_group == "C":
            return relevant_atoms
        elif student_group == "B":
            # Skip some intermediate atoms
            return relevant_atoms[::2] if len(relevant_atoms) > 3 else relevant_atoms
        else:  # Group A - minimal remediation
            return relevant_atoms[:1] if relevant_atoms else []


class PassportEvaluator:
    """
    Evaluates Passport assessments and determines mastery progression.
    """

    def evaluate(
        self,
        answers: List[Dict[str, Any]],
        passing_threshold: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Evaluate Passport assessment results.

        Args:
            answers: List of answer results
            passing_threshold: Minimum accuracy to pass (0-1)

        Returns:
            Evaluation results including pass/fail and accuracy
        """
        if not answers:
            return {"passed": False, "accuracy": 0.0}

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
        """
        Calculate new mastery level based on Passport results.

        Args:
            current_mastery: Current mastery level string
            passed: Whether student passed
            accuracy: Accuracy percentage

        Returns:
            New mastery level
        """
        mastery_order = [
            MasteryLevel.NOT_STARTED,
            MasteryLevel.ATTEMPTED,
            MasteryLevel.FAMILIAR,
            MasteryLevel.PROFICIENT,
            MasteryLevel.MASTERED,
        ]

        current_index = mastery_order.index(current_mastery)

        if passed:
            # Advance mastery level
            if accuracy >= 0.9 and current_index < len(mastery_order) - 1:
                return mastery_order[current_index + 1]
            elif accuracy >= 0.75 and current_index < len(mastery_order) - 1:
                return mastery_order[current_index + 1]
            else:
                return current_mastery
        else:
            # Regress mastery level (model forgetting)
            if current_index > 0:
                return mastery_order[current_index - 1]
            return current_mastery


class RemediationEngine:
    """
    Main remediation engine coordinating pathway generation and assessment.
    """

    def __init__(self):
        self.difficulty_adjuster = DynamicDifficultyAdjuster()
        self.engagement_tracker = StudentEngagementTracker()
        self.pathway_generator = PathwayGenerator()
        self.passport_evaluator = PassportEvaluator()
        self._paths: Dict[str, Dict[str, Any]] = {}  # In-memory storage for demo

    def start_path(
        self,
        student_id: UUID,
        competency_id: str,
        student_group: str,
    ) -> Dict[str, Any]:
        """Start a new remediation pathway."""
        from datetime import datetime, timezone

        path = {
            "id": uuid4(),
            "student_id": student_id,
            "competency_id": competency_id,
            "status": RemediationPathStatus.IN_PROGRESS,
            "atoms": [],
            "atoms_completed": [],
            "started_at": datetime.now(timezone.utc),
            "current_difficulty": 5,
        }

        key = f"{student_id}:{competency_id}"
        self._paths[key] = path

        return path

    def set_pathway_atoms(
        self,
        student_id: UUID,
        competency_id: str,
        atoms: List[Dict[str, Any]],
    ) -> None:
        """Set the atoms for a pathway."""
        key = f"{student_id}:{competency_id}"
        if key in self._paths:
            self._paths[key]["atoms"] = atoms

    def get_next_atom(
        self,
        student_id: UUID,
        competency_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get the next atom to complete."""
        key = f"{student_id}:{competency_id}"
        path = self._paths.get(key)

        if not path:
            return None

        completed = set(path.get("atoms_completed", []))
        for atom in path.get("atoms", []):
            if atom.get("id") not in completed:
                return atom

        return None

    def complete_atom(
        self,
        student_id: UUID,
        competency_id: str,
        atom_id: str,
        performance_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Mark an atom as complete."""
        key = f"{student_id}:{competency_id}"
        path = self._paths.get(key)

        if not path:
            raise ValueError("Path not found")

        # Add to completed
        if atom_id not in path["atoms_completed"]:
            path["atoms_completed"].append(atom_id)

        # Update difficulty based on performance
        current_difficulty = path.get("current_difficulty", 5)
        new_difficulty = self.difficulty_adjuster.adjust(
            current_difficulty=current_difficulty,
            response_time_ms=performance_data.get("time_ms", 10000),
            is_correct=performance_data.get("is_correct", True),
            estimated_time_ms=30000,  # Default estimate
        )
        path["current_difficulty"] = new_difficulty

        # Calculate progress
        total_atoms = len(path.get("atoms", []))
        completed_count = len(path["atoms_completed"])
        progress_percent = (completed_count / total_atoms * 100) if total_atoms > 0 else 0

        return {
            "atoms_completed": completed_count,
            "total_atoms": total_atoms,
            "progress_percent": progress_percent,
            "new_difficulty": new_difficulty,
        }

    def is_pathway_complete(self, student_id: UUID, competency_id: str) -> bool:
        """Check if pathway is complete."""
        key = f"{student_id}:{competency_id}"
        path = self._paths.get(key)

        if not path:
            return False

        completed = set(path.get("atoms_completed", []))
        all_atoms = path.get("atoms", [])

        return len(completed) >= len(all_atoms) and len(all_atoms) > 0

    def generate_passport_questions(
        self,
        competency_id: str,
        count: int = 5,
    ) -> List[Dict[str, Any]]:
        """Generate Passport assessment questions."""
        # In production, this would query questions by competency
        return [
            {
                "id": f"passport_q_{i}",
                "competency_id": competency_id,
                "difficulty_level": 5,
            }
            for i in range(count)
        ]

    def evaluate_passport(
        self,
        current_mastery: str,
        answers: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Evaluate a Passport assessment."""
        # Evaluate answers
        evaluation = self.passport_evaluator.evaluate(answers)

        # Calculate new mastery
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


# Import uuid here to avoid circular import
from uuid import uuid4
