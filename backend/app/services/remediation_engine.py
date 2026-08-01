"""
Remediation engine service coordinating pathway generation and assessment.
Delegates calculation logic to app.engines.remediation_engine.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from app.engines.remediation_engine import (
    DynamicDifficultyAdjuster as StatelessDynamicDifficultyAdjuster,
    PassportEvaluator as StatelessPassportEvaluator,
    PathwayGenerator as StatelessPathwayGenerator,
    RemediationEngine as StatelessRemediationEngine,
    StudentEngagementTracker as StatelessStudentEngagementTracker,
)
from app.models.diagnostic import MasteryLevel
from app.models.remediation import RemediationPathStatus


class DynamicDifficultyAdjuster(StatelessDynamicDifficultyAdjuster):
    """Adapter delegating to stateless dynamic difficulty adjuster engine."""

    pass


class StudentEngagementTracker:
    """
    Adapter keeping track of responses history in memory for service compatibility,
    delegating checks to stateless StudentEngagementTracker engine.
    """

    def __init__(self, window_size: int = 5):
        self.responses: List[Dict[str, Any]] = []
        self.window_size = window_size
        self._stateless = StatelessStudentEngagementTracker()

    def record_response(self, time_ms: int, is_correct: bool) -> None:
        self.responses.append({"time_ms": time_ms, "is_correct": is_correct})
        if len(self.responses) > self.window_size:
            self.responses = self.responses[-self.window_size :]

    def is_frustrated(self) -> bool:
        return self._stateless.is_frustrated(self.responses)

    def is_bored(self) -> bool:
        return self._stateless.is_bored(self.responses)

    def get_recommendation(self) -> Dict[str, str]:
        return self._stateless.get_recommendation(self.responses)


class PathwayGenerator(StatelessPathwayGenerator):
    """Adapter delegating to stateless pathway generator engine."""

    pass


class PassportEvaluator(StatelessPassportEvaluator):
    """Adapter delegating to stateless passport evaluator engine."""

    pass


class RemediationEngine:
    """
    Remediation engine service wrapper.
    Delegates domain calculations to app.engines.remediation_engine.
    """

    def __init__(self):
        self.engine = StatelessRemediationEngine()
        self.difficulty_adjuster = self.engine.difficulty_adjuster
        self.engagement_tracker = StudentEngagementTracker()
        self.pathway_generator = self.engine.pathway_generator
        self.passport_evaluator = self.engine.passport_evaluator
        self._paths: Dict[str, Dict[str, Any]] = {}

    def start_path(
        self,
        student_id: UUID,
        competency_id: str,
        student_group: str,
    ) -> Dict[str, Any]:
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
        key = f"{student_id}:{competency_id}"
        if key in self._paths:
            self._paths[key]["atoms"] = atoms

    def get_next_atom(
        self,
        student_id: UUID,
        competency_id: str,
    ) -> Optional[Dict[str, Any]]:
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
        key = f"{student_id}:{competency_id}"
        path = self._paths.get(key)
        if not path:
            raise ValueError("Path not found")

        if atom_id not in path["atoms_completed"]:
            path["atoms_completed"].append(atom_id)

        result = self.engine.process_atom_completion(
            current_difficulty=path.get("current_difficulty", 5),
            performance_data=performance_data,
            atoms_completed_count=len(path["atoms_completed"]) - 1,
            total_atoms=len(path.get("atoms", [])),
        )

        path["current_difficulty"] = result["new_difficulty"]
        return result

    def is_pathway_complete(self, student_id: UUID, competency_id: str) -> bool:
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
        return self.engine.evaluate_passport(current_mastery, answers)
