"""
Diagnostic engine with Bayesian Knowledge Tracing (BKT) and adaptive question selection.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from app.models.diagnostic import (
    ErrorClassification as ErrorClassificationEnum,
    MasteryLevel,
    RemediationGroup as RemediationGroupEnum,
)


class BayesianKnowledgeTracing:
    """
    Bayesian Knowledge Tracing implementation.

    Tracks the probability that a student has learned a competency
    using Bayesian inference based on their answers.
    """

    def __init__(
        self,
        p_learn: float = 0.3,  # Probability of learning
        p_guess: float = 0.2,  # Probability of guessing correctly
        p_slip: float = 0.1,  # Probability of slipping (incorrect when known)
    ):
        self.p_learn = p_learn
        self.p_guess = p_guess
        self.p_slip = p_slip
        self.p_learned = 0.0  # Initial probability: not learned

    def update(self, is_correct: bool) -> None:
        """
        Update P(learned) based on student's answer using Bayes' theorem.

        Args:
            is_correct: Whether the student answered correctly
        """
        if is_correct:
            # P(L|Correct) using Bayes' theorem
            p_correct_given_learned = 1 - self.p_slip
            p_correct_given_not_learned = self.p_guess

            p_correct = (
                self.p_learned * p_correct_given_learned
                + (1 - self.p_learned) * p_correct_given_not_learned
            )

            self.p_learned = (
                self.p_learned * p_correct_given_learned / p_correct
            )
        else:
            # P(L|Incorrect)
            p_incorrect_given_learned = self.p_slip
            p_incorrect_given_not_learned = 1 - self.p_guess

            p_incorrect = (
                self.p_learned * p_incorrect_given_learned
                + (1 - self.p_learned) * p_incorrect_given_not_learned
            )

            self.p_learned = (
                self.p_learned * p_incorrect_given_learned / p_incorrect
            )

        # Clamp to valid probability range
        self.p_learned = max(0.0, min(1.0, self.p_learned))

    def get_mastery_level(self) -> str:
        """
        Convert P(learned) to discrete mastery level.

        Returns:
            Mastery level string
        """
        p = self.p_learned
        if p < 0.1:
            return MasteryLevel.NOT_STARTED
        elif p < 0.4:
            return MasteryLevel.ATTEMPTED
        elif p < 0.7:
            return MasteryLevel.FAMILIAR
        elif p < 0.9:
            return MasteryLevel.PROFICIENT
        else:
            return MasteryLevel.MASTERED


class ErrorClassification:
    """
    Classifies student errors into categories:
    - RESOURCE: Missing prerequisites
    - PROCESS: Methodology misunderstanding
    - INCIDENTAL: Carelessness
    - NONE: Correct answer
    """

    def classify(
        self,
        is_correct: bool,
        target_misconception_id: Optional[str],
        response_time_ms: int,
        difficulty_level: int,
    ) -> str:
        """
        Classify the error based on answer correctness and timing.

        Args:
            is_correct: Whether answer was correct
            target_misconception_id: Misconception tag if any
            response_time_ms: Response time in milliseconds
            difficulty_level: Question difficulty (1-10)

        Returns:
            Error classification string
        """
        if is_correct:
            return ErrorClassificationEnum.NONE

        estimated_time = difficulty_level * 10000  # ~10s per difficulty level

        # Very fast wrong answers suggest carelessness
        if response_time_ms < estimated_time * 0.3:
            return ErrorClassificationEnum.INCIDENTAL

        # Wrong answers targeting specific misconceptions suggest resource gap
        if target_misconception_id:
            return ErrorClassificationEnum.RESOURCE

        # Otherwise assume process error
        return ErrorClassificationEnum.PROCESS


class QuestionSelector:
    """
    Adaptive question selection algorithm.

    Selects next question based on:
    - Current mastery level
    - Target misconceptions to probe
    - Difficulty progression
    - Avoiding repetition
    """

    def select_next_question(
        self,
        questions: List[Dict[str, Any]],
        answered_question_ids: List[str],
        current_mastery: float,
        target_misconceptions: List[str],
    ) -> Optional[Dict[str, Any]]:
        """
        Select the next question adaptively.

        Args:
            questions: Available questions
            answered_question_ids: IDs of already answered questions
            current_mastery: Current BKT P(learned) value
            target_misconceptions: Misconceptions to target

        Returns:
            Selected question or None if no questions available
        """
        # Filter out answered questions
        available = [
            q for q in questions if q.get("id") not in answered_question_ids
        ]

        if not available:
            return None

        # Calculate target difficulty based on mastery
        # Map mastery (0-1) to difficulty (1-10)
        target_difficulty = min(10, max(1, int(current_mastery * 10) + 1))

        # Score each question
        def score_question(q: Dict[str, Any]) -> float:
            score = 0.0

            # Difficulty match score (closer is better)
            q_difficulty = q.get("difficulty_level", 5)
            difficulty_diff = abs(q_difficulty - target_difficulty)
            score -= difficulty_diff * 10  # Penalty for difficulty mismatch

            # Misconception targeting bonus
            q_misconception = q.get("target_misconception_id")
            if q_misconception and q_misconception in target_misconceptions:
                score += 50  # Strong bonus for targeting needed misconception

            return score

        # Select highest scoring question
        available.sort(key=score_question, reverse=True)
        return available[0]


class RemediationGroup:
    """
    Assigns students to remediation groups based on diagnostic performance.

    Groups:
    - A: Mastery (enrichment)
    - B: Partial mastery (targeted remediation)
    - C: No mastery (intensive remediation)
    """

    def assign(
        self,
        mastery_probability: float,
        correct_answers: int,
        total_questions: int,
    ) -> str:
        """
        Assign remediation group.

        Args:
            mastery_probability: Final BKT P(learned)
            correct_answers: Number of correct answers
            total_questions: Total questions answered

        Returns:
            Group assignment (A, B, or C)
        """
        accuracy = correct_answers / total_questions if total_questions > 0 else 0

        # Group A: High mastery and good accuracy
        if mastery_probability >= 0.75 and accuracy >= 0.7:
            return RemediationGroupEnum.A

        # Group C: Low mastery or poor accuracy
        if mastery_probability < 0.4 or accuracy < 0.4:
            return RemediationGroupEnum.C

        # Group B: Everything else
        return RemediationGroupEnum.B


class DiagnosticEngine:
    """
    Main diagnostic engine coordinating BKT, question selection, and results.
    """

    def __init__(self):
        self.sessions: Dict[UUID, Dict[str, Any]] = {}
        self.bkt_models: Dict[str, BayesianKnowledgeTracing] = {}
        self.error_classifier = ErrorClassification()
        self.question_selector = QuestionSelector()
        self.group_assigner = RemediationGroup()

    def start_session(
        self,
        session_id: UUID,
        student_id: UUID,
        module_id: UUID,
    ) -> Dict[str, Any]:
        """Start a new diagnostic session."""
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
        """Process an answer and update BKT state."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Classify the error
        error_classification = self.error_classifier.classify(
            is_correct=is_correct,
            target_misconception_id=target_misconception_id,
            response_time_ms=response_time_ms,
            difficulty_level=5,  # Default, should be passed from question
        )

        # Update BKT
        session["bkt"].update(is_correct)

        # Record answer
        session["answers"].append({
            "question_id": question_id,
            "is_correct": is_correct,
            "response_time_ms": response_time_ms,
            "error_classification": error_classification,
        })

        return {
            "error_classification": error_classification,
            "current_mastery": session["bkt"].p_learned,
            "mastery_level": session["bkt"].get_mastery_level(),
        }

    def is_session_complete(
        self,
        session_id: UUID,
        min_questions: int = 10,
        max_questions: int = 15,
    ) -> bool:
        """Check if diagnostic session should end."""
        session = self.sessions.get(session_id)
        if not session:
            return False

        num_answers = len(session["answers"])

        # Minimum questions threshold
        if num_answers < min_questions:
            return False

        # Maximum questions cap
        if num_answers >= max_questions:
            return True

        # Converged mastery (confident in assessment)
        bkt = session["bkt"]
        if bkt.p_learned > 0.9 or bkt.p_learned < 0.1:
            return True

        return False

    def get_results(self, session_id: UUID) -> Dict[str, Any]:
        """Get diagnostic session results."""
        from datetime import datetime, timezone

        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        bkt = session["bkt"]
        answers = session["answers"]

        correct_count = sum(1 for a in answers if a["is_correct"])
        total_count = len(answers)

        # Assign remediation group
        recommended_group = self.group_assigner.assign(
            mastery_probability=bkt.p_learned,
            correct_answers=correct_count,
            total_questions=total_count,
        )

        # Mark session complete
        session["completed_at"] = datetime.now(timezone.utc)

        return {
            "session_id": session_id,
            "mastery_probability": bkt.p_learned,
            "mastery_level": bkt.get_mastery_level(),
            "recommended_group": recommended_group,
            "total_questions": total_count,
            "correct_answers": correct_count,
            "accuracy": correct_count / total_count if total_count > 0 else 0,
            "completed_at": session["completed_at"],
        }
