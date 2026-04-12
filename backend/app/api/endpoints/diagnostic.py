"""
API endpoints for diagnostic sessions.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_student, get_db
from app.models.content import Question
from app.models.diagnostic import (
    CompetencyProfile,
    DiagnosticAnswer,
    DiagnosticSession,
    DiagnosticSessionStatus,
    ErrorClassification,
)
from app.models.user import User
from app.schemas.diagnostic import (
    AnswerSubmitRequest,
    AnswerSubmitResponse,
    CompetencyProfileResponse,
    DiagnosticResultsResponse,
    DiagnosticSessionCreate,
    StartDiagnosticResponse,
)
from app.services.diagnostic_engine import DiagnosticEngine

router = APIRouter()


@router.post(
    "/start",
    response_model=StartDiagnosticResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new diagnostic session",
)
async def start_diagnostic(
    session_data: DiagnosticSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_student),
) -> StartDiagnosticResponse:
    """Start a new adaptive diagnostic session.

    Returns the first question to begin the diagnostic.
    """
    # Create session
    session = DiagnosticSession(
        student_id=current_user.id,
        module_id=session_data.module_id,
        status=DiagnosticSessionStatus.IN_PROGRESS,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Get first question (simple: start with medium difficulty)
    result = await db.execute(
        select(Question)
        .where(Question.module_id == session_data.module_id)
        .where(Question.difficulty_level == 5)
        .limit(1)
    )
    first_question = result.scalar_one_or_none()

    if not first_question:
        # Fallback: get any question from module
        result = await db.execute(
            select(Question)
            .where(Question.module_id == session_data.module_id)
            .limit(1)
        )
        first_question = result.scalar_one_or_none()

    if not first_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No questions available for this module",
        )

    return StartDiagnosticResponse(
        session_id=session.id,
        question={
            "id": str(first_question.id),
            "content": first_question.content,
            "difficulty_level": first_question.difficulty_level,
            "estimated_time_sec": first_question.estimated_time_sec,
        },
        question_number=1,
    )


@router.post(
    "/answer",
    response_model=AnswerSubmitResponse,
    summary="Submit an answer and get next question",
)
async def submit_answer(
    answer_data: AnswerSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_student),
) -> AnswerSubmitResponse:
    """Submit an answer and get the next question or completion status."""
    # Get session
    result = await db.execute(
        select(DiagnosticSession).where(
            DiagnosticSession.id == answer_data.session_id,
            DiagnosticSession.student_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session.status == DiagnosticSessionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already completed",
        )

    # Get question to check correctness
    result = await db.execute(
        select(Question).where(Question.id == answer_data.question_id)
    )
    question = result.scalar_one_or_none()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )

    # Check answer correctness
    # TODO: Implement proper answer validation based on question type
    # For now, simple string comparison
    correct_answer = question.content.get("correct_answer", "")
    is_correct = answer_data.answer.strip().lower() == correct_answer.strip().lower()

    # Classify error
    error_classification = ErrorClassification.NONE if is_correct else ErrorClassification.PROCESS

    # Record answer
    answer = DiagnosticAnswer(
        session_id=answer_data.session_id,
        question_id=answer_data.question_id,
        is_correct=1 if is_correct else 0,
        response_time_ms=answer_data.time_ms,
        error_classification=error_classification,
    )
    db.add(answer)
    await db.commit()

    # Check if session is complete (10-15 questions typical)
    result = await db.execute(
        select(DiagnosticAnswer).where(
            DiagnosticAnswer.session_id == answer_data.session_id
        )
    )
    answer_count = len(result.scalars().all())

    is_complete = answer_count >= 10  # Minimum diagnostic length

    if not is_complete:
        # Get next question (simple adaptive selection)
        # In production, use the DiagnosticEngine for proper adaptive selection
        answered_ids = [
            str(a.question_id)
            for a in result.scalars().all()
        ]

        result = await db.execute(
            select(Question)
            .where(Question.module_id == session.module_id)
            .where(Question.id.notin_(answered_ids))
            .limit(1)
        )
        next_question = result.scalar_one_or_none()

        if not next_question:
            is_complete = True
        else:
            return AnswerSubmitResponse(
                is_correct=is_correct,
                error_classification=error_classification,
                current_mastery=0.5,  # TODO: Calculate from BKT
                mastery_level="FAMILIAR",
                next_question={
                    "id": str(next_question.id),
                    "content": next_question.content,
                    "difficulty_level": next_question.difficulty_level,
                    "estimated_time_sec": next_question.estimated_time_sec,
                },
                is_complete=False,
            )

    # Session complete
    if is_complete:
        session.status = DiagnosticSessionStatus.COMPLETED
        session.completed_at = datetime.now(timezone.utc)

        # Assign remediation group based on performance
        result = await db.execute(
            select(DiagnosticAnswer).where(
                DiagnosticAnswer.session_id == answer_data.session_id
            )
        )
        answers = result.scalars().all()
        correct_count = sum(a.is_correct for a in answers)
        accuracy = correct_count / len(answers) if answers else 0

        if accuracy >= 0.7:
            session.recommended_group = "A"
        elif accuracy >= 0.4:
            session.recommended_group = "B"
        else:
            session.recommended_group = "C"

        await db.commit()

    return AnswerSubmitResponse(
        is_correct=is_correct,
        error_classification=error_classification,
        current_mastery=accuracy,
        mastery_level="PROFICIENT" if accuracy > 0.7 else "FAMILIAR",
        next_question=None,
        is_complete=True,
    )


@router.get(
    "/results/{session_id}",
    response_model=DiagnosticResultsResponse,
    summary="Get diagnostic session results",
)
async def get_results(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_student),
) -> DiagnosticResultsResponse:
    """Get the results of a completed diagnostic session."""
    result = await db.execute(
        select(DiagnosticSession).where(
            DiagnosticSession.id == session_id,
            DiagnosticSession.student_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Get answer statistics
    result = await db.execute(
        select(DiagnosticAnswer).where(
            DiagnosticAnswer.session_id == session_id
        )
    )
    answers = result.scalars().all()
    total_questions = len(answers)
    correct_answers = sum(a.is_correct for a in answers)
    accuracy = correct_answers / total_questions if total_questions > 0 else 0

    # Determine mastery level
    if accuracy >= 0.9:
        mastery_level = "MASTERED"
        mastery_probability = 0.95
    elif accuracy >= 0.7:
        mastery_level = "PROFICIENT"
        mastery_probability = 0.75
    elif accuracy >= 0.5:
        mastery_level = "FAMILIAR"
        mastery_probability = 0.55
    elif accuracy >= 0.3:
        mastery_level = "ATTEMPTED"
        mastery_probability = 0.25
    else:
        mastery_level = "NOT_STARTED"
        mastery_probability = 0.05

    return DiagnosticResultsResponse(
        session_id=session_id,
        mastery_probability=mastery_probability,
        mastery_level=mastery_level,
        recommended_group=session.recommended_group or "C",
        total_questions=total_questions,
        correct_answers=correct_answers,
        accuracy=accuracy,
        completed_at=session.completed_at or datetime.now(timezone.utc),
    )


@router.get(
    "/competency-profile",
    response_model=List[CompetencyProfileResponse],
    summary="Get student's competency profiles",
)
async def get_competency_profiles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_student),
) -> List[CompetencyProfileResponse]:
    """Get all competency profiles for the current student."""
    result = await db.execute(
        select(CompetencyProfile).where(
            CompetencyProfile.student_id == current_user.id
        )
    )
    profiles = result.scalars().all()
    return list(profiles)


# Add datetime import
from datetime import datetime, timezone
