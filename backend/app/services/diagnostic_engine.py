"""
Diagnostic service coordinating BKT, question selection, and evaluation.
Delegates domain logic calculations to app.engines.diagnostic_engine and app.engines.bkt.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from app.engines.bkt import BKTParams, get_mastery_level, update_mastery
from app.engines.diagnostic_engine import (
    DiagnosticEngine as StatelessDiagnosticEngine,
    ErrorClassification as StatelessErrorClassification,
    MultiArmBanditSelector as StatelessMultiArmBanditSelector,
    QuestionSelector as StatelessQuestionSelector,
    RemediationGroup as StatelessRemediationGroup,
)
from app.models.diagnostic import (
    ErrorClassification as ErrorClassificationEnum,
    MasteryLevel,
    RemediationGroup as RemediationGroupEnum,
)


class BayesianKnowledgeTracing:
    """
    Stateful BKT wrapper around app.engines.bkt.update_mastery.
    Maintained for service-layer backward compatibility.
    """

    def __init__(
        self,
        p_learn: float = 0.3,
        p_guess: float = 0.2,
        p_slip: float = 0.1,
    ):
        self.params = BKTParams(p_learn=p_learn, p_guess=p_guess, p_slip=p_slip)
        self.p_learned = 0.0

    @property
    def p_learn(self) -> float:
        return self.params.p_learn

    @property
    def p_guess(self) -> float:
        return self.params.p_guess

    @property
    def p_slip(self) -> float:
        return self.params.p_slip

    def update(self, is_correct: bool) -> None:
        self.p_learned = update_mastery(self.p_learned, is_correct, self.params)

    def get_mastery_level(self) -> str:
        return get_mastery_level(self.p_learned)


class ErrorClassification(StatelessErrorClassification):
    """Adapter for ErrorClassification delegating to stateless engine."""

    pass


class QuestionSelector(StatelessQuestionSelector):
    """Adapter for QuestionSelector delegating to stateless engine."""

    pass


class MultiArmBanditSelector:
    """
    Adapter for MultiArmBanditSelector keeping track of session stats if needed,
    but delegating calculations to StatelessMultiArmBanditSelector.
    """

    def __init__(self):
        self.question_stats: Dict[str, Dict[str, int]] = {}
        self._stateless = StatelessMultiArmBanditSelector()

    def record_outcome(self, question_id: str, is_correct: bool) -> None:
        if question_id not in self.question_stats:
            self.question_stats[question_id] = {"success": 0, "total": 0}
        self.question_stats[question_id]["total"] += 1
        if is_correct:
            self.question_stats[question_id]["success"] += 1

    def select_next_question(
        self,
        questions: List[Dict[str, Any]],
        answered_question_ids: List[str],
        current_mastery: float,
        target_misconceptions: List[str],
        exploration_weight: float = 0.3,
    ) -> Optional[Dict[str, Any]]:
        return self._stateless.select_next_question(
            questions=questions,
            answered_question_ids=answered_question_ids,
            current_mastery=current_mastery,
            target_misconceptions=target_misconceptions,
            question_stats=self.question_stats,
            exploration_weight=exploration_weight,
        )


class RemediationGroup(StatelessRemediationGroup):
    """Adapter for RemediationGroup delegating to stateless engine."""

    pass


class DiagnosticEngine:
    """
    Diagnostic engine service delegating to app.engines.
    Note: For backward compatibility with tests/services expecting in-memory session tracking,
    session dictionary storage is kept at the service level, while engine calculation is stateless.
    """

    def __init__(self):
        self.sessions: Dict[UUID, Dict[str, Any]] = {}
        self.bkt_models: Dict[str, BayesianKnowledgeTracing] = {}
        self.engine = StatelessDiagnosticEngine()
        self.error_classifier = self.engine.error_classifier
        self.question_selector = self.engine.question_selector
        self.group_assigner = self.engine.group_assigner

    def start_session(
        self,
        session_id: UUID,
        student_id: UUID,
        module_id: UUID,
    ) -> Dict[str, Any]:
        from datetime import datetime, timezone

        session = {
            "id": session_id,
            "student_id": student_id,
            "module_id": module_id,
            "answers": [],
            "started_at": datetime.now(timezone.utc),
            "completed_at": None,
            "bkt": BayesianKnowledgeTracing(),
        }

        self.sessions[session_id] = session

        return {
            "id": session_id,
            "student_id": student_id,
            "module_id": module_id,
            "started_at": session["started_at"],
            "completed_at": None,
        }

    def process_answer(
        self,
        session_id: UUID,
        question_id: UUID,
        is_correct: bool,
        response_time_ms: int,
        target_misconception_id: Optional[str],
    ) -> Dict[str, Any]:
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        current_p = session["bkt"].p_learned
        result = self.engine.process_answer(
            current_p_learned=current_p,
            is_correct=is_correct,
            response_time_ms=response_time_ms,
            difficulty_level=5,
            target_misconception_id=target_misconception_id,
        )

        session["bkt"].p_learned = result["current_mastery"]
        session["answers"].append({
            "question_id": question_id,
            "is_correct": is_correct,
            "response_time_ms": response_time_ms,
            "error_classification": result["error_classification"],
        })

        return result

    def is_session_complete(
        self,
        session_id: UUID,
        min_questions: int = 10,
        max_questions: int = 15,
    ) -> bool:
        session = self.sessions.get(session_id)
        if not session:
            return False

        return self.engine.is_session_complete(
            answers_count=len(session["answers"]),
            current_p_learned=session["bkt"].p_learned,
            min_questions=min_questions,
            max_questions=max_questions,
        )

    def get_results(self, session_id: UUID) -> Dict[str, Any]:
        from datetime import datetime, timezone

        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        bkt = session["bkt"]
        answers = session["answers"]
        correct_count = sum(1 for a in answers if a["is_correct"])
        total_count = len(answers)

        results = self.engine.evaluate_session_results(
            session_id=session_id,
            final_p_learned=bkt.p_learned,
            correct_count=correct_count,
            total_count=total_count,
        )

        session["completed_at"] = datetime.now(timezone.utc)
        results["completed_at"] = session["completed_at"]

        return results
