"""
Analytics Service encapsulating business logic for heatmaps and analytics reports.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.engines.remediation_engine import RemediationEngine
from app.models.diagnostic import CompetencyProfile, MasteryLevel
from app.repositories.analytics_repo import AnalyticsRepo
from app.schemas.analytics import (
    AutoGroupResponse,
    HeatmapCell,
    HeatmapFilters,
    HeatmapResponse,
    StudentCompetencyRow,
)


class AnalyticsService:
    """Service for computing and formatting analytics data."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AnalyticsRepo(db)
        self.engine = RemediationEngine()

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

    async def auto_group_students(
        self,
        organization_id: UUID,
        filters: Optional[HeatmapFilters] = None,
        group_by: str = "competency",
    ) -> AutoGroupResponse:
        """
        Auto-group students by delegating DB fetching to repo and clustering to RemediationEngine.
        """
        student_ids = filters.student_ids if filters else None
        competency_ids = filters.competency_ids if filters else None

        profiles = await self.repo.get_auto_group_data(
            organization_id=organization_id,
            student_ids=student_ids,
            competency_ids=competency_ids,
        )

        records = [
            {
                "student_id": str(p.student_id),
                "competency_id": p.competency_id,
                "mastery_level": p.mastery_level.value,
                "error_type": getattr(p, "error_type", None) or "PROCESS",
            }
            for p in profiles
        ]

        groups = self.engine.auto_group_students(
            records=records,
            group_by=group_by,
        )

        return AutoGroupResponse(
            groups=groups,
            total_groups=len(groups),
            group_by=group_by,
        )

    async def export_report(
        self,
        organization_id: UUID,
        report_type: str,
        export_format: str,
        filters: Optional[HeatmapFilters] = None,
        student_ids: Optional[List[UUID]] = None,
    ) -> str:
        """
        Delegate report exporting to ReportExporter with organization tenant isolation.
        """
        from app.core.tenant import set_active_organization_id
        from app.services.report_exporter import ReportExporter

        set_active_organization_id(organization_id)

        exporter = ReportExporter(self.db)
        if export_format == "csv":
            return await exporter.export_csv(
                report_type=report_type,
                filters=filters,
                student_ids=student_ids,
                organization_id=organization_id,
            )
        elif export_format == "pdf":
            return await exporter.export_pdf(
                report_type=report_type,
                filters=filters,
                student_ids=student_ids,
                organization_id=organization_id,
            )
        else:
            raise ValueError(f"Unsupported format: {export_format}")

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
