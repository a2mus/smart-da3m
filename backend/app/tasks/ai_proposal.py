"""
Celery task for AI-augmented remediation pathway proposal generation (AD-3).
Combines deterministic selection via engines.remediation_engine with LiteLLM augmentation.
Includes fallback to deterministic proposal if LiteLLM is unavailable.
"""

import logging
from typing import Any, Dict, List, Optional

from app.core.celery import celery_app
from app.core.config import settings
from app.engines.remediation_engine import PathwayGenerator

logger = logging.getLogger(__name__)


def _call_litellm_augmentation(
    competency_id: str,
    atoms: List[Dict[str, Any]],
    gap_profile: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Call LiteLLM for pedagogical justification augmentation.
    Contains zero student PII per safety constraints.
    """
    try:
        import litellm
    except ImportError:
        logger.warning("litellm package not installed, skipping LLM augmentation")
        return atoms

    try:
        model = settings.LLM_MODEL or "openai/gemini-3.6-flash-high"
        if settings.LLM_BASE_URL and not model.startswith("openai/"):
            model = f"openai/{model}"
        prompt_content = (
            f"Given competency '{competency_id}' and gap profile '{gap_profile or {}}', "
            f"provide pedagogical annotations for these selected knowledge atoms: {atoms}"
        )
        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": [{"role": "user", "content": prompt_content}],
            "temperature": 0.2,
        }
        if settings.LLM_BASE_URL:
            kwargs["api_base"] = settings.LLM_BASE_URL
        if settings.LLM_API_KEY:
            kwargs["api_key"] = settings.LLM_API_KEY

        response = litellm.completion(**kwargs)
        explanation = response.choices[0].message.content

        augmented_atoms = []
        for atom in atoms:
            atom_copy = dict(atom)
            atom_copy["ai_pedagogical_justification"] = (
                f"LLM Augmented ({model}): {explanation[:120]}..."
            )
            augmented_atoms.append(atom_copy)
        return augmented_atoms
    except Exception as exc:
        logger.warning("LiteLLM augmentation failed, falling back to deterministic proposal: %s", exc)
        return atoms


@celery_app.task(name="generate_remediation_proposal")
def generate_remediation_proposal(
    session_id: str,
    competency_id: str,
    student_group: str = "C",
    available_atoms: Optional[List[Dict[str, Any]]] = None,
    organization_id: Optional[str] = None,
    student_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Asynchronous Celery task for generating remediation pathway proposals.
    1. Reads gap profile / parameters.
    2. Runs deterministic PathwayGenerator.
    3. Calls LiteLLM for pedagogical augmentation (with exception fallback).
    4. Formats proposed pathway result with status PROPOSED.
    """
    atoms_input = available_atoms or []

    # Step 1 & 2: Deterministic atom selection via engines.remediation_engine
    generator = PathwayGenerator()
    selected_atoms = generator.generate(
        competency_id=competency_id,
        student_group=student_group,
        available_atoms=atoms_input,
    )

    # Step 3: Send gap profile + selected atoms to LiteLLM with fallback
    gap_profile = {"session_id": session_id, "student_group": student_group}
    augmented_atoms = _call_litellm_augmentation(
        competency_id=competency_id,
        atoms=selected_atoms,
        gap_profile=gap_profile,
    )

    # Step 4 & 5: Format proposed pathway result in PROPOSED state
    proposal_result = {
        "session_id": session_id,
        "organization_id": organization_id,
        "student_id": student_id,
        "competency_id": competency_id,
        "status": "PROPOSED",
        "atoms": augmented_atoms,
        "atoms_count": len(augmented_atoms),
        "student_group": student_group,
    }

    logger.info(
        "Generated remediation proposal for session %s, competency %s (atoms: %d, status: PROPOSED)",
        session_id,
        competency_id,
        len(augmented_atoms),
    )
    return proposal_result
