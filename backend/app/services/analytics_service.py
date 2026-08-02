"""
Analytics Service encapsulating business logic for heatmaps and analytics reports.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.diagnostic import CompetencyProfile, MasteryLevel
from app.repositories.analytics_repo import AnalyticsRepo
from app.schemas.analytics import (
    HeatmapCell,
    HeatmapResponse,
    StudentCompetencyRow,
)


class AnalyticsService:
    """Service for computing and formatting analytics data."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AnalyticsRepo(db)

    async def get_heatmap(
        self, organization_id: UUID, module_id: Optional[UUID] = None
    ) -> HeatmapResponse:
        """
        Fetch and format heatmap data for an organization, optionally filtered by module.
        """
        profiles = await self.repo.get_heatmap_data(organization_id, module_id)
        students = await self.repo.get_students_for_heatmap(organization_id, module_id)

        if not students and not profiles:
            return HeatmapResponse(
                students=[],
                competencies=[],
                cells=[],
                total_students=0,
                total_competencies=0,
            )

        # Build student list
        student_rows: List[StudentCompetencyRow] = []
        for s in students:
            student_rows.append(
                StudentCompetencyRow(
                    id=s.id,
                    name=s.email.split("@")[0] if s.email else f"Student {str(s.id)[:8]}",
                    grade_level="Primary",
                )
            )

        # Collect unique competencies
        competencies = sorted(list(set(p.competency_id for p in profiles)))

        # Build cells
        cells: List[HeatmapCell] = []
        for profile in profiles:
            color = self._mastery_to_color(profile.mastery_level)
            score = self._mastery_to_score(profile.mastery_level, profile.p_learned)

            cells.append(
                HeatmapCell(
                    student_id=profile.student_id,
                    competency_id=profile.competency_id,
                    mastery_level=profile.mastery_level.value,
                    p_learned=round(profile.p_learned, 2),
                    color=color,
                    score=score,
                )
            )

        return HeatmapResponse(
            students=student_rows,
            competencies=competencies,
            cells=cells,
            total_students=len(student_rows),
            total_competencies=len(competencies),
        )

    @staticmethod
    def _mastery_to_color(mastery: MasteryLevel) -> str:
        colors = {
            MasteryLevel.NOT_STARTED: "#fee2e2",  # Red
            MasteryLevel.ATTEMPTED: "#fef3c7",  # Soft Red/Amber
            MasteryLevel.FAMILIAR: "#fef9c3",  # Yellow
            MasteryLevel.PROFICIENT: "#d1fae5",  # Green
            MasteryLevel.MASTERED: "#86efac",  # Bright Green
        }
        return colors.get(mastery, "#f3f4f6")

    @staticmethod
    def _mastery_to_score(mastery: MasteryLevel, p_learned: float) -> int:
        if p_learned > 0:
            return int(round(p_learned * 100))
        scores = {
            MasteryLevel.NOT_STARTED: 0,
            MasteryLevel.ATTEMPTED: 25,
            MasteryLevel.FAMILIAR: 50,
            MasteryLevel.PROFICIENT: 75,
            MasteryLevel.MASTERED: 100,
        }
        return scores.get(mastery, 0)
