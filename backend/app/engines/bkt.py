"""
Bayesian Knowledge Tracing (BKT) pure functions and parameters.
Stateless implementation per AD-1.
"""

from dataclasses import dataclass
import enum
from typing import Optional


class MasteryLevel(str, enum.Enum):
    """Mastery level enumeration for competency profiles."""

    NOT_STARTED = "NOT_STARTED"
    ATTEMPTED = "ATTEMPTED"
    FAMILIAR = "FAMILIAR"
    PROFICIENT = "PROFICIENT"
    MASTERED = "MASTERED"


@dataclass(frozen=True)
class BKTParams:
    """BKT configuration parameters."""

    p_learn: float = 0.3  # Probability of learning
    p_guess: float = 0.2  # Probability of guessing correctly
    p_slip: float = 0.1  # Probability of slipping (incorrect when known)


def update_mastery(
    current_p_learned: float,
    is_correct: bool,
    params: Optional[BKTParams] = None,
) -> float:
    """
    Pure function to update P(learned) based on student's answer using Bayes' theorem.

    Args:
        current_p_learned: Current probability student has learned the competency [0.0, 1.0]
        is_correct: Whether the student answered correctly
        params: BKT parameters (defaults to standard BKTParams if None)

    Returns:
        Updated P(learned) clamped to valid probability range [0.0, 1.0]
    """
    if params is None:
        params = BKTParams()

    p_learned = max(0.0, min(1.0, current_p_learned))

    if is_correct:
        # P(L|Correct) using Bayes' theorem
        p_correct_given_learned = 1.0 - params.p_slip
        p_correct_given_not_learned = params.p_guess

        p_correct = (
            p_learned * p_correct_given_learned
            + (1.0 - p_learned) * p_correct_given_not_learned
        )

        if p_correct > 0:
            p_learned = (p_learned * p_correct_given_learned) / p_correct
        # Apply transition probability p_learn
        p_learned = p_learned + (1.0 - p_learned) * params.p_learn
    else:
        # P(L|Incorrect)
        p_incorrect_given_learned = params.p_slip
        p_incorrect_given_not_learned = 1.0 - params.p_guess

        p_incorrect = (
            p_learned * p_incorrect_given_learned
            + (1.0 - p_learned) * p_incorrect_given_not_learned
        )

        if p_incorrect > 0:
            p_learned = (p_learned * p_incorrect_given_learned) / p_incorrect

    # Clamp to valid probability range
    return max(0.0, min(1.0, p_learned))


def get_mastery_level(p_learned: float) -> str:
    """
    Convert P(learned) float to discrete mastery level string.

    Args:
        p_learned: P(learned) probability [0.0, 1.0]

    Returns:
        Mastery level enum value string
    """
    if p_learned < 0.1:
        return MasteryLevel.NOT_STARTED
    elif p_learned < 0.4:
        return MasteryLevel.ATTEMPTED
    elif p_learned < 0.7:
        return MasteryLevel.FAMILIAR
    elif p_learned < 0.9:
        return MasteryLevel.PROFICIENT
    else:
        return MasteryLevel.MASTERED
