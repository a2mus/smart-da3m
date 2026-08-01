"""
API endpoints for diagnostic sessions using repository layer for DB access.
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_student, get_db
from app.models.diagnostic import (
    DiagnosticSessionStatus,
    ErrorClassification,
    RemediationGroup,
)
from app.models.user import User
from app.repositories.content_repo import ContentRepository
from app.repositories.diagnostic_repo import DiagnosticRepository
from app.schemas.diagnostic import (
    AnswerSubmitRequest,
    AnswerSubmitResponse,
    CompetencyProfileResponse,
    DiagnosticResultsResponse,
    DiagnosticSessionCreate,
    StartDiagnosticResponse,
)

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
    """Start a new adaptive diagnostic session."""
    diag_repo = DiagnosticRepository(db)
    content_repo = ContentRepository(db)

    org_id = getattr(current_user, "organization_id", None) or UUID("00000000-0000-0000-0000-000000000000")

    session = await diag_repo.create_session(
        student_id=current_user.id,
        module_id=session_data.module_id,
        organization_id=org_id,
        status=DiagnosticSessionStatus.IN_PROGRESS,
    )

    questions = await content_repo.list_module_questions(session_data.module_id)
    first_question = None
    for q in questions:
        if q.difficulty_level == 5:
            first_question = q
            break
    if not first_question and questions:
        first_question = questions[0]

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
    diag_repo = DiagnosticRepository(db)
    content_repo = ContentRepository(db)

    session = await diag_repo.get_session(answer_data.session_id)
    if not session or session.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session.status == DiagnosticSessionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already completed",
        )

    question = await content_repo.get_question(answer_data.question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )

    correct_answer = question.content.get("correct_answer", "")
    is_correct = answer_data.answer.strip().lower() == correct_answer.strip().lower()
    error_classification = ErrorClassification.NONE if is_correct else ErrorClassification.PROCESS

    org_id = getattr(session, "organization_id", None) or UUID("00000000-0000-0000-0000-000000000000")

    await diag_repo.record_answer(
        session_id=answer_data.session_id,
        question_id=answer_data.question_id,
        organization_id=org_id,
        is_correct=1 if is_correct else 0,
        response_time_ms=answer_data.time_ms,
        error_classification=error_classification,
    )

    answers = await diag_repo.get_session_answers(answer_data.session_id)
    answer_count = len(answers)
    is_complete = answer_count >= 10

    if not is_complete:
        answered_ids = {a.question_id for a in answers}
        module_questions = await content_repo.list_module_questions(session.module_id)
        next_question = next((q for q in module_questions if q.id not in answered_ids), None)

        if not next_question:
            is_complete = True
        else:
            return AnswerSubmitResponse(
                is_correct=is_correct,
                error_classification=error_classification,
                current_mastery=0.5,
                mastery_level="FAMILIAR",
                next_question={
                    "id": str(next_question.id),
                    "content": next_question.content,
                    "difficulty_level": next_question.difficulty_level,
                    "estimated_time_sec": next_question.estimated_time_sec,
                },
                is_complete=False,
            )

    if is_complete:
        correct_count = sum(a.is_correct for a in answers)
        accuracy = correct_count / len(answers) if answers else 0.0

        if accuracy >= 0.7:
            rec_group = RemediationGroup.A
        elif accuracy >= 0.4:
            rec_group = RemediationGroup.B
        else:
            rec_group = RemediationGroup.C

        await diag_repo.update_session_status(
            session.id, DiagnosticSessionStatus.COMPLETED, rec_group
        )

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
    diag_repo = DiagnosticRepository(db)
    session = await diag_repo.get_session(session_id)

    if not session or session.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    answers = await diag_repo.get_session_answers(session_id)
    total_questions = len(answers)
    correct_answers = sum(a.is_correct for a in answers)
    accuracy = correct_answers / total_questions if total_questions > 0 else 0.0

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

    rec_group_val = session.recommended_group.value if session.recommended_group else "C"

    return DiagnosticResultsResponse(
        session_id=session_id,
        mastery_probability=mastery_probability,
        mastery_level=mastery_level,
        recommended_group=rec_group_val,
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
    diag_repo = DiagnosticRepository(db)
    profiles = await diag_repo.get_student_competencies(current_user.id)
    return [
        CompetencyProfileResponse(
            id=p.id,
            competency_id=p.competency_id,
            mastery_level=p.mastery_level.value if hasattr(p.mastery_level, "value") else str(p.mastery_level),
            p_learned=p.p_learned,
            last_assessed=p.last_assessed,
        )
        for p in profiles
    ]
