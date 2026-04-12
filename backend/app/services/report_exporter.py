"""
Report exporter service for generating PDF and CSV reports.
Handles remediation cards, heatmaps, and analytics exports.
"""

import csv
import os
import tempfile
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.diagnostic import CompetencyProfile, MasteryLevel
from app.models.user import User, UserRole


class ReportExporter:
    """Service for exporting analytics reports in various formats."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.export_dir = tempfile.gettempdir()

    async def export_csv(
        self,
        report_type: str,
        filters: Optional[Any] = None,
        student_ids: Optional[List[UUID]] = None,
    ) -> str:
        """Export analytics data as CSV."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{report_type}_{timestamp}.csv"
        filepath = os.path.join(self.export_dir, filename)

        if report_type == "heatmap":
            await self._export_heatmap_csv(filepath, filters, student_ids)
        elif report_type == "remediation_card":
            await self._export_remediation_csv(filepath, student_ids)
        elif report_type == "full_report":
            await self._export_full_report_csv(filepath, filters, student_ids)
        else:
            raise ValueError(f"Unknown report type: {report_type}")

        return filepath

    async def _export_heatmap_csv(
        self,
        filepath: str,
        filters: Optional[Any] = None,
        student_ids: Optional[List[UUID]] = None,
    ) -> None:
        """Export competency heatmap as CSV."""
        query = select(User).where(User.role == UserRole.STUDENT)
        if student_ids:
            query = query.where(User.id.in_(student_ids))

        result = await self.db.execute(query)
        students = list(result.scalars().all())

        student_ids_list = [s.id for s in students]
        profile_query = select(CompetencyProfile).where(
            CompetencyProfile.student_id.in_(student_ids_list)
        )

        if filters and hasattr(filters, "competency_ids") and filters.competency_ids:
            profile_query = profile_query.where(
                CompetencyProfile.competency_id.in_(filters.competency_ids)
            )

        result = await self.db.execute(profile_query)
        profiles = list(result.scalars().all())

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Student ID",
                "Competency ID",
                "Mastery Level",
                "Probability Learned",
                "Last Assessed",
            ])

            for profile in profiles:
                writer.writerow([
                    str(profile.student_id),
                    profile.competency_id,
                    profile.mastery_level.value,
                    f"{profile.p_learned:.2f}",
                    profile.last_assessed.isoformat() if profile.last_assessed else "",
                ])

    async def _export_remediation_csv(
        self,
        filepath: str,
        student_ids: Optional[List[UUID]] = None,
    ) -> None:
        """Export remediation cards as CSV."""
        if not student_ids:
            raise ValueError("Student IDs required for remediation card export")

        query = select(CompetencyProfile).where(
            CompetencyProfile.student_id.in_(student_ids),
            CompetencyProfile.mastery_level.in_([
                MasteryLevel.NOT_STARTED,
                MasteryLevel.ATTEMPTED,
            ]),
        )

        result = await self.db.execute(query)
        profiles = list(result.scalars().all())

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Student ID",
                "Competency ID",
                "Current Mastery",
                "Gap Level",
                "Recommended Action",
            ])

            for profile in profiles:
                gap_level = (
                    "Critical" if profile.mastery_level == MasteryLevel.NOT_STARTED
                    else "Moderate"
                )
                writer.writerow([
                    str(profile.student_id),
                    profile.competency_id,
                    profile.mastery_level.value,
                    gap_level,
                    f"Targeted remediation for {profile.competency_id}",
                ])

    async def _export_full_report_csv(
        self,
        filepath: str,
        filters: Optional[Any] = None,
        student_ids: Optional[List[UUID]] = None,
    ) -> None:
        """Export full analytics report as CSV."""
        query = select(User).where(User.role == UserRole.STUDENT)
        if student_ids:
            query = query.where(User.id.in_(student_ids))

        result = await self.db.execute(query)
        students = list(result.scalars().all())

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Report Generated",
                datetime.now(timezone.utc).isoformat(),
            ])
            writer.writerow([])
            writer.writerow([
                "Total Students",
                len(students),
            ])
            writer.writerow([])

            student_ids_list = [s.id for s in students]
            profile_query = select(CompetencyProfile).where(
                CompetencyProfile.student_id.in_(student_ids_list)
            )
            result = await self.db.execute(profile_query)
            profiles = list(result.scalars().all())

            mastery_counts: Dict[str, int] = {}
            for profile in profiles:
                level = profile.mastery_level.value
                mastery_counts[level] = mastery_counts.get(level, 0) + 1

            writer.writerow(["Mastery Distribution"])
            writer.writerow(["Level", "Count"])
            for level, count in sorted(mastery_counts.items()):
                writer.writerow([level, count])

    async def export_pdf(
        self,
        report_type: str,
        filters: Optional[Any] = None,
        student_ids: Optional[List[UUID]] = None,
    ) -> str:
        """Export analytics data as PDF."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{report_type}_{timestamp}.pdf"
        filepath = os.path.join(self.export_dir, filename)

        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import (
                Paragraph,
                SimpleDocTemplate,
                Spacer,
                Table,
            )
        except ImportError:
            return await self._export_pdf_fallback(
                filepath, report_type, filters, student_ids
            )

        if report_type == "heatmap":
            await self._export_heatmap_pdf(filepath, filters, student_ids)
        elif report_type == "remediation_card":
            await self._export_remediation_pdf(filepath, student_ids)
        elif report_type == "full_report":
            await self._export_full_report_pdf(filepath, filters, student_ids)
        else:
            raise ValueError(f"Unknown report type: {report_type}")

        return filepath

    async def _export_pdf_fallback(
        self,
        filepath: str,
        report_type: str,
        filters: Optional[Any],
        student_ids: Optional[List[UUID]],
    ) -> str:
        """Fallback PDF generation using text format."""
        txt_filepath = filepath.replace(".pdf", ".txt")

        with open(txt_filepath, "w", encoding="utf-8") as f:
            f.write(f"Ihsane Platform - {report_type.upper()} Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now(timezone.utc).isoformat()}\n\n")

            if student_ids:
                f.write(f"Students: {len(student_ids)}\n")

            f.write("\n[PDF generation requires ReportLab package]\n")
            f.write("Please install: pip install reportlab\n")

        return txt_filepath

    async def _export_heatmap_pdf(
        self,
        filepath: str,
        filters: Optional[Any],
        student_ids: Optional[List[UUID]],
    ) -> None:
        """Export competency heatmap as PDF."""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table

        doc = SimpleDocTemplate(filepath, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        elements = []

        title = Paragraph("Competency Heatmap Report", styles["Heading1"])
        elements.append(title)
        elements.append(Spacer(1, 20))

        query = select(User).where(User.role == UserRole.STUDENT)
        if student_ids:
            query = query.where(User.id.in_(student_ids))

        result = await self.db.execute(query)
        students = list(result.scalars().all())

        student_ids_list = [s.id for s in students]
        profile_query = select(CompetencyProfile).where(
            CompetencyProfile.student_id.in_(student_ids_list)
        )
        result = await self.db.execute(profile_query)
        profiles = list(result.scalars().all())

        competency_ids = sorted(set(p.competency_id for p in profiles))

        header = ["Student"] + competency_ids[:8]
        data = [header]

        for student in students[:20]:
            row = [f"Student {str(student.id)[:8]}"]
            for competency_id in competency_ids[:8]:
                profile = next(
                    (
                        p
                        for p in profiles
                        if p.student_id == student.id
                        and p.competency_id == competency_id
                    ),
                    None,
                )
                if profile:
                    row.append(profile.mastery_level.value[:3])
                else:
                    row.append("-")
            data.append(row)

        table = Table(data)
        table.setStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ])

        elements.append(table)
        doc.build(elements)

    async def _export_remediation_pdf(
        self,
        filepath: str,
        student_ids: Optional[List[UUID]],
    ) -> None:
        """Export remediation cards as PDF."""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        title = Paragraph("Student Remediation Cards", styles["Heading1"])
        elements.append(title)
        elements.append(Spacer(1, 20))

        if not student_ids:
            elements.append(Paragraph("No students specified", styles["Normal"]))
            doc.build(elements)
            return

        query = select(CompetencyProfile).where(
            CompetencyProfile.student_id.in_(student_ids),
            CompetencyProfile.mastery_level.in_([
                MasteryLevel.NOT_STARTED,
                MasteryLevel.ATTEMPTED,
            ]),
        )
        result = await self.db.execute(query)
        profiles = list(result.scalars().all())

        by_student: Dict[str, List[CompetencyProfile]] = {}
        for profile in profiles:
            sid = str(profile.student_id)
            if sid not in by_student:
                by_student[sid] = []
            by_student[sid].append(profile)

        for student_id, student_profiles in by_student.items():
            elements.append(
                Paragraph(f"Student: {student_id[:8]}", styles["Heading2"])
            )

            for profile in student_profiles:
                elements.append(
                    Paragraph(
                        f"• {profile.competency_id}: {profile.mastery_level.value}",
                        styles["Normal"],
                    )
                )

            elements.append(Spacer(1, 20))

        doc.build(elements)

    async def _export_full_report_pdf(
        self,
        filepath: str,
        filters: Optional[Any],
        student_ids: Optional[List[UUID]],
    ) -> None:
        """Export full analytics report as PDF."""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("Ihsane Platform Analytics Report", styles["Heading1"]))
        elements.append(Spacer(1, 20))
        elements.append(
            Paragraph(
                f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
                styles["Normal"],
            )
        )
        elements.append(Spacer(1, 40))

        query = select(User).where(User.role == UserRole.STUDENT)
        if student_ids:
            query = query.where(User.id.in_(student_ids))

        result = await self.db.execute(query)
        students = list(result.scalars().all())

        elements.append(Paragraph(f"Total Students: {len(students)}", styles["Heading2"]))
        elements.append(Spacer(1, 20))

        student_ids_list = [s.id for s in students]
        profile_query = select(CompetencyProfile).where(
            CompetencyProfile.student_id.in_(student_ids_list)
        )
        result = await self.db.execute(profile_query)
        profiles = list(result.scalars().all())

        elements.append(Paragraph("Mastery Distribution", styles["Heading2"]))

        mastery_counts: Dict[str, int] = {}
        for profile in profiles:
            level = profile.mastery_level.value
            mastery_counts[level] = mastery_counts.get(level, 0) + 1

        for level, count in sorted(mastery_counts.items()):
            elements.append(Paragraph(f"{level}: {count}", styles["Normal"]))

        doc.build(elements)
