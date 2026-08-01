"""API endpoints for diagnostic sessions using repository layer and stateless domain engine per AD-1.
"""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_student, get_db
from app.engines.diagnostic_engine import DiagnosticEngine
from app.models.diagnostic import (
    DiagnosticSessionStatus,
    ErrorClassification,
    MasteryLevel,
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
from app.services.alert_manager import AlertManager

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

    # Retrieve module to determine target competency
    module = await content_repo.get_module(session.module_id)
    competency_id = module.competency_id if module else "C1"

    org_id = getattr(session, "organization_id", None) or UUID("00000000-0000-0000-0000-000000000000")

    # Get student's current competency profile P(learned)
    profile = await diag_repo.get_competency_profile(current_user.id, competency_id)
    current_p_learned = profile.p_learned if profile else 0.5

    # Process answer with stateless DiagnosticEngine & BKT
    engine = DiagnosticEngine()
    processed = engine.process_answer(
        current_p_learned=current_p_learned,
        is_correct=is_correct,
        response_time_ms=answer_data.time_ms,
        difficulty_level=question.difficulty_level,
        target_misconception_id=question.target_misconception_id,
    )

    new_p_learned = processed["current_mastery"]
    mastery_level_val = processed["mastery_level"]
    error_classification_val = processed["error_classification"]

    # Persist updated competency profile P(learned) and mastery level to DB
    await diag_repo.update_or_create_competency_profile(
        student_id=current_user.id,
        competency_id=competency_id,
        organization_id=org_id,
        p_learned=new_p_learned,
        mastery_level=MasteryLevel(mastery_level_val),
    )

    # Record student answer in DB
    await diag_repo.record_answer(
        session_id=answer_data.session_id,
        question_id=answer_data.question_id,
        organization_id=org_id,
        is_correct=1 if is_correct else 0,
        response_time_ms=answer_data.time_ms,
        error_classification=ErrorClassification(error_classification_val),
    )

    answers = await diag_repo.get_session_answers(answer_data.session_id)
    answer_count = len(answers)

    answers_dicts = [
        {
            "is_correct": bool(a.is_correct),
            "response_time_ms": a.response_time_ms,
            "misconception_id": getattr(a, "misconception_id", None)
            or (question.target_misconception_id if not a.is_correct else None),
        }
        for a in answers
    ]
    session_data_dict = {
        "started_at": session.started_at,
        "completed_at": session.completed_at,
        "answers_count": answer_count,
        "expected_count": 10,
    }
    alert_mgr = AlertManager()
    generated_alerts = alert_mgr.check_session_for_alerts(
        student_id=current_user.id,
        session_data=session_data_dict,
        answers=answers_dicts,
    )
    if generated_alerts:
        await alert_mgr.process_and_persist_alerts(
            alerts=generated_alerts,
            organization_id=org_id,
            db=db,
        )

    is_complete = engine.is_session_complete(
        answers_count=answer_count,
        current_p_learned=new_p_learned,
    )

    if not is_complete:
        answered_ids = [str(a.question_id) for a in answers]
        module_questions = await content_repo.list_module_questions(session.module_id)
        questions_dicts = [
            {
                "id": str(q.id),
                "content": q.content,
                "difficulty_level": q.difficulty_level,
                "target_misconception_id": q.target_misconception_id,
                "estimated_time_sec": q.estimated_time_sec,
                "_question_obj": q,
            }
            for q in module_questions
        ]

        selected_dict = engine.question_selector.select_next_question(
            questions=questions_dicts,
            answered_question_ids=answered_ids,
            current_mastery=new_p_learned,
            target_misconceptions=[question.target_misconception_id] if question.target_misconception_id else [],
        )

        if not selected_dict:
            is_complete = True
        else:
            next_q = selected_dict["_question_obj"]
            return AnswerSubmitResponse(
                is_correct=is_correct,
                error_classification=ErrorClassification(error_classification_val),
                current_mastery=new_p_learned,
                mastery_level=mastery_level_val,
                next_question={
                    "id": str(next_q.id),
                    "content": next_q.content,
                    "difficulty_level": next_q.difficulty_level,
                    "estimated_time_sec": next_q.estimated_time_sec,
                },
                is_complete=False,
            )

    if is_complete:
        correct_count = sum(a.is_correct for a in answers)
        eval_results = engine.evaluate_session_results(
            session_id=session.id,
            final_p_learned=new_p_learned,
            correct_count=correct_count,
            total_count=len(answers),
        )

        rec_group_raw = eval_results["recommended_group"]
        rec_group_enum = RemediationGroup(
            rec_group_raw.value if hasattr(rec_group_raw, "value") else str(rec_group_raw)
        )

        await diag_repo.update_session_status(
            session.id, DiagnosticSessionStatus.COMPLETED, rec_group_enum
        )

        return AnswerSubmitResponse(
            is_correct=is_correct,
            error_classification=ErrorClassification(error_classification_val),
            current_mastery=eval_results["mastery_probability"],
            mastery_level=eval_results["mastery_level"],
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
    content_repo = ContentRepository(db)

    session = await diag_repo.get_session(session_id)
    if not session or session.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    answers = await diag_repo.get_session_answers(session_id)
    total_questions = len(answers)
    correct_answers = sum(a.is_correct for a in answers)

    module = await content_repo.get_module(session.module_id)
    competency_id = module.competency_id if module else "C1"
    profile = await diag_repo.get_competency_profile(current_user.id, competency_id)
    p_learned = profile.p_learned if profile else (correct_answers / total_questions if total_questions > 0 else 0.5)

    engine = DiagnosticEngine()
    eval_results = engine.evaluate_session_results(
        session_id=session.id,
        final_p_learned=p_learned,
        correct_count=correct_answers,
        total_count=total_questions,
    )

    rec_group_raw = eval_results["recommended_group"]
    rec_group_val = rec_group_raw.value if hasattr(rec_group_raw, "value") else str(rec_group_raw)

    return DiagnosticResultsResponse(
        session_id=session_id,
        mastery_probability=eval_results["mastery_probability"],
        mastery_level=eval_results["mastery_level"],
        recommended_group=rec_group_val,
        total_questions=total_questions,
        correct_answers=correct_answers,
        accuracy=eval_results["accuracy"],
        completed_at=session.completed_at or datetime.now(UTC),
    )


@router.get(
    "/competency-profile",
    response_model=list[CompetencyProfileResponse],
    summary="Get student's competency profiles",
)
async def get_competency_profiles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_student),
) -> list[CompetencyProfileResponse]:
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
