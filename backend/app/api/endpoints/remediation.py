"""
API endpoints for remediation pathways and Passport assessments.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_student, get_db
from app.models.content import KnowledgeAtom, Question
from app.models.diagnostic import CompetencyProfile, MasteryLevel
from app.models.remediation import (
    AtomCompletion,
    PassportAssessment,
    RemediationPath,
    RemediationPathStatus,
)
from app.models.user import User
from app.schemas.remediation import (
    AtomCompleteRequest,
    AtomCompleteResponse,
    EngagementStatusResponse,
    PassportEvaluateRequest,
    PassportEvaluateResponse,
    PassportQuestionsResponse,
    RemediationPathRequest,
    RemediationPathResponse,
    RemediationStatusResponse,
)
from app.services.remediation_engine import RemediationEngine

router = APIRouter()


@router.get(
    "/pathway/{competency_id}",
    response_model=RemediationPathResponse,
    summary="Get remediation pathway for a competency",
)
async def get_remediation_pathway(
    competency_id: str,
    student_group: str = "B",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_student),
) -> RemediationPathResponse:
    """Get or create a personalized remediation pathway."""
    # Check for existing path
    result = await db.execute(
        select(RemediationPath).where(
            RemediationPath.student_id == current_user.id,
            RemediationPath.competency_id == competency_id,
        )
    )
    path = result.scalar_one_or_none()

    if not path:
        # Create new path
        path = RemediationPath(
            student_id=current_user.id,
            competency_id=competency_id,
            status=RemediationPathStatus.IN_PROGRESS,
            atoms_completed=[],
        )
        db.add(path)
        await db.commit()
        await db.refresh(path)

    # Get available atoms for this competency
    result = await db.execute(
        select(KnowledgeAtom).where(
            KnowledgeAtom.competency_id == competency_id
        )
    )
    atoms = result.scalars().all()

    # Generate pathway using engine
    engine = RemediationEngine()
    pathway_atoms = engine.pathway_generator.generate(
        competency_id=competency_id,
        student_group=student_group,
        available_atoms=[
            {
                "id": str(a.id),
                "competency_id": a.competency_id,
                "remediation_type": a.remediation_type.value,
                "content": a.content,
            }
            for a in atoms
        ],
    )

    # Calculate progress
    total_atoms = len(pathway_atoms)
    completed_count = len(path.atoms_completed) if path.atoms_completed else 0
    progress_percent = (completed_count / total_atoms * 100) if total_atoms > 0 else 0

    return RemediationPathResponse(
        id=path.id,
        student_id=path.student_id,
        competency_id=path.competency_id,
        status=path.status,
        atoms=[
            RemediationAtom(
                id=UUID(a["id"]),
                competency_id=a["competency_id"],
                remediation_type=a["remediation_type"],
                content=a["content"],
                order=i,
            )
            for i, a in enumerate(pathway_atoms)
        ],
        atoms_completed=path.atoms_completed or [],
        progress_percent=progress_percent,
        current_difficulty=path.current_difficulty,
        started_at=path.started_at,
        completed_at=path.completed_at,
    )


@router.post(
    "/atoms/{atom_id}/complete",
    response_model=AtomCompleteResponse,
    summary="Mark a knowledge atom as complete",
)
async def complete_atom(
    atom_id: UUID,
    completion_data: AtomCompleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_student),
) -> AtomCompleteResponse:
    """Mark a knowledge atom as completed and track progress."""
    # Find the atom
    result = await db.execute(
        select(KnowledgeAtom).where(KnowledgeAtom.id == atom_id)
    )
    atom = result.scalar_one_or_none()

    if not atom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge atom not found",
        )

    # Find or create remediation path
    result = await db.execute(
        select(RemediationPath).where(
            RemediationPath.student_id == current_user.id,
            RemediationPath.competency_id == atom.competency_id,
        )
    )
    path = result.scalar_one_or_none()

    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remediation path not found",
        )

    # Record completion
    completion = AtomCompletion(
        path_id=path.id,
        atom_id=atom_id,
        time_spent_ms=completion_data.time_spent_ms,
        interactions_count=completion_data.interactions_count,
    )
    db.add(completion)

    # Update path
    if path.atoms_completed is None:
        path.atoms_completed = []

    if atom_id not in path.atoms_completed:
        path.atoms_completed.append(atom_id)

    # Update difficulty
    engine = RemediationEngine()
    new_difficulty = engine.difficulty_adjuster.adjust(
        current_difficulty=path.current_difficulty,
        response_time_ms=completion_data.time_spent_ms,
        is_correct=completion_data.is_correct,
        estimated_time_ms=30000,
    )
    path.current_difficulty = new_difficulty

    await db.commit()

    # Check if pathway complete
    result = await db.execute(
        select(KnowledgeAtom).where(
            KnowledgeAtom.competency_id == atom.competency_id
        )
    )
    total_atoms = len(result.scalars().all())
    completed_count = len(path.atoms_completed)
    progress_percent = (completed_count / total_atoms * 100) if total_atoms > 0 else 0

    # Check for engagement recommendation
    rec = engine.engagement_tracker.get_recommendation()

    return AtomCompleteResponse(
        atom_id=atom_id,
        atoms_completed=completed_count,
        total_atoms=total_atoms,
        progress_percent=progress_percent,
        new_difficulty=new_difficulty,
        next_atom=None,  # Would calculate next
        recommendation=rec.get("message"),
    )


@router.get(
    "/status/{competency_id}",
    response_model=RemediationStatusResponse,
    summary="Get remediation status for a competency",
)
async def get_remediation_status(
    competency_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_student),
) -> RemediationStatusResponse:
    """Get current remediation status."""
    result = await db.execute(
        select(RemediationPath).where(
            RemediationPath.student_id == current_user.id,
            RemediationPath.competency_id == competency_id,
        )
    )
    path = result.scalar_one_or_none()

    if not path:
        return RemediationStatusResponse(
            competency_id=competency_id,
            status=RemediationPathStatus.IN_PROGRESS,
            atoms_completed=[],
            progress_percent=0.0,
            can_take_passport=False,
        )

    # Get total atoms for this competency
    result = await db.execute(
        select(KnowledgeAtom).where(
            KnowledgeAtom.competency_id == competency_id
        )
    )
    total_atoms = len(result.scalars().all())
    completed_count = len(path.atoms_completed) if path.atoms_completed else 0
    progress_percent = (completed_count / total_atoms * 100) if total_atoms > 0 else 0

    # Can take passport if significant progress made
    can_take_passport = progress_percent >= 50 or completed_count >= 3

    return RemediationStatusResponse(
        competency_id=competency_id,
        status=path.status,
        atoms_completed=path.atoms_completed or [],
        progress_percent=progress_percent,
        can_take_passport=can_take_passport,
    )


@router.get(
    "/passport/questions/{competency_id}",
    response_model=PassportQuestionsResponse,
    summary="Get Passport assessment questions",
)
async def get_passport_questions(
    competency_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_student),
) -> PassportQuestionsResponse:
    """Get questions for the Passport mastery assessment."""
    # Create assessment record
    assessment = PassportAssessment(
        student_id=current_user.id,
        competency_id=competency_id,
    )
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)

    # Get questions for this competency
    # In production, would query by competency via question-competency mapping
    result = await db.execute(
        select(Question)
        .where(Question.difficulty_level.between(4, 7))
        .limit(5)
    )
    questions = result.scalars().all()

    return PassportQuestionsResponse(
        competency_id=competency_id,
        questions=[
            {
                "id": str(q.id),
                "content": q.content,
                "difficulty_level": q.difficulty_level,
            }
            for q in questions
        ],
        assessment_id=assessment.id,
    )


@router.post(
    "/passport/evaluate",
    response_model=PassportEvaluateResponse,
    summary="Evaluate Passport assessment",
)
async def evaluate_passport(
    evaluate_data: PassportEvaluateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_student),
) -> PassportEvaluateResponse:
    """Evaluate Passport assessment and update mastery."""
    # Get current competency profile
    result = await db.execute(
        select(CompetencyProfile).where(
            CompetencyProfile.student_id == current_user.id,
            CompetencyProfile.competency_id == evaluate_data.competency_id,
        )
    )
    profile = result.scalar_one_or_none()

    if not profile:
        # Create default profile
        profile = CompetencyProfile(
            student_id=current_user.id,
            competency_id=evaluate_data.competency_id,
            mastery_level=MasteryLevel.FAMILIAR,
            p_learned=0.5,
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)

    # Check answers
    answers = []
    for ans in evaluate_data.answers:
        # Get question to check correctness
        result = await db.execute(
            select(Question).where(Question.id == ans.question_id)
        )
        question = result.scalar_one_or_none()

        if question:
            correct = ans.answer.strip().lower() == question.content.get("correct_answer", "").strip().lower()
            answers.append({"question_id": ans.question_id, "is_correct": correct})

    # Evaluate using engine
    engine = RemediationEngine()
    evaluation = engine.evaluate_passport(
        current_mastery=profile.mastery_level.value,
        answers=answers,
    )

    # Update profile
    previous_level = profile.mastery_level.value
    profile.mastery_level = evaluation["new_mastery_level"]
    profile.last_assessed = datetime.now(timezone.utc)

    # Update or create assessment record
    assessment = PassportAssessment(
        student_id=current_user.id,
        competency_id=evaluate_data.competency_id,
        passed=1 if evaluation["passed"] else 0,
        accuracy=int(evaluation["accuracy"] * 100),
        questions_answered=len(answers),
        correct_answers=evaluation["correct_count"],
        completed_at=datetime.now(timezone.utc),
    )
    db.add(assessment)

    # If passed, update remediation path status
    if evaluation["passed"]:
        result = await db.execute(
            select(RemediationPath).where(
                RemediationPath.student_id == current_user.id,
                RemediationPath.competency_id == evaluate_data.competency_id,
            )
        )
        path = result.scalar_one_or_none()
        if path:
            path.status = RemediationPathStatus.COMPLETED
            path.completed_at = datetime.now(timezone.utc)

    await db.commit()

    # Generate message
    if evaluation["passed"]:
        message = f"Congratulations! You've advanced to {evaluation['new_mastery_level']} level!"
    else:
        message = "Keep practicing! You'll get there."

    return PassportEvaluateResponse(
        passed=evaluation["passed"],
        accuracy=evaluation["accuracy"],
        correct_count=evaluation["correct_count"],
        total_questions=evaluation["total_questions"],
        previous_mastery_level=previous_level,
        new_mastery_level=evaluation["new_mastery_level"],
        badge_earned=evaluate_data.competency_id if evaluation["passed"] else None,
        alert_triggered=evaluation["alert_triggered"],
        message=message,
    )


from datetime import datetime, timezone

# Import for type hints
from app.schemas.remediation import RemediationAtom
