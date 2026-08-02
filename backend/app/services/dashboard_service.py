"""
Dashboard service for aggregating parent dashboard data.
Pulls data from diagnostic, remediation, and competency sources via DashboardRepo.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.diagnostic import MasteryLevel
from app.models.user import User
from app.repositories.dashboard_repo import DashboardRepo


class DashboardAggregator:
    """
    Aggregates dashboard data for parents using DashboardRepo.

    Pulls together:
    - Child profiles and progress
    - Subject competency data
    - Recent activities
    - Smart recommendations
    """

    def __init__(
        self,
        db: AsyncSession,
        tenant_id: Optional[UUID] = None,
        repo: Optional[DashboardRepo] = None,
    ):
        self.db = db
        self.tenant_id = tenant_id
        self.repo = repo or DashboardRepo(db, tenant_id=tenant_id)

    async def get_children_for_parent(self, parent_id: UUID) -> List[User]:
        """Get all children for a parent."""
        return await self.repo.get_children_for_parent(parent_id)

    async def get_child_subjects(self, student_id: UUID) -> List[Dict[str, Any]]:
        """Get subject competency data for a child."""
        profiles = await self.repo.get_child_competency_profiles(student_id)

        subjects = []
        for profile in profiles:
            subject_name = self._map_competency_to_subject(profile.competency_id)
            score = self._mastery_to_score(profile.mastery_level)

            subjects.append({
                "name": subject_name,
                "competency_id": profile.competency_id,
                "score": score,
                "mastery_level": profile.mastery_level.value,
                "last_assessed": profile.last_assessed.isoformat()
                if profile.last_assessed
                else None,
            })

        return subjects

    def _map_competency_to_subject(self, competency_id: str) -> str:
        """Map a competency ID to a human-readable subject name."""
        if "MATH" in competency_id:
            return "Mathematics"
        elif "ARAB" in competency_id:
            return "Arabic"
        elif "FREN" in competency_id:
            return "French"
        elif "SCI" in competency_id:
            return "Science"
        else:
            return "General"

    def _mastery_to_score(self, mastery_level: MasteryLevel) -> int:
        """Convert mastery level to numerical score."""
        scores = {
            MasteryLevel.NOT_STARTED: 0,
            MasteryLevel.ATTEMPTED: 25,
            MasteryLevel.FAMILIAR: 50,
            MasteryLevel.PROFICIENT: 75,
            MasteryLevel.MASTERED: 100,
        }
        return scores.get(mastery_level, 50)

    async def get_recent_activities(
        self, student_id: UUID, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get recent learning activities for a child."""
        activities = []

        sessions = await self.repo.get_recent_diagnostic_sessions(student_id, limit=limit)
        for session in sessions:
            activities.append({
                "type": "DIAGNOSTIC",
                "title": "Completed diagnostic assessment",
                "timestamp": session.completed_at.isoformat()
                if session.completed_at
                else session.started_at.isoformat(),
                "status": "completed" if session.completed_at else "in_progress",
            })

        paths = await self.repo.get_recent_remediation_paths(student_id, limit=limit)
        for path in paths:
            if path.atoms_completed and len(path.atoms_completed) > 0:
                activities.append({
                    "type": "REMEDIATION",
                    "title": "Learning activity completed",
                    "timestamp": path.started_at.isoformat(),
                    "progress": len(path.atoms_completed),
                })

        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities[:limit]

    def generate_insights(self, mastery_profiles: List[Any]) -> List[Dict[str, Any]]:
        """
        Generate plain-language smart insights from student competency profiles (zero raw scores).

        Returns structured insight items referencing human-readable competency names,
        qualitative mastery levels, and non-numeric descriptive text.
        """
        if not mastery_profiles:
            return [{
                "id": "insight-default",
                "type": "GENERAL",
                "text": "Child hasn't completed any assessments yet.",
                "competency_id": None,
                "competency_name": None,
                "mastery_level": "NOT_STARTED",
            }]

        insights = []

        def extract_info(item):
            if isinstance(item, dict):
                c_id = item.get("competency_id") or item.get("competencyId") or "UNKNOWN"
                m_level = item.get("mastery_level") or item.get("masteryLevel") or "NOT_STARTED"
            else:
                c_id = getattr(item, "competency_id", "UNKNOWN")
                m_level = getattr(item, "mastery_level", "NOT_STARTED")
                if hasattr(m_level, "value"):
                    m_level = m_level.value
            return str(c_id), str(m_level).upper()

        COMPETENCY_NAMES = {
            "ARAB_TAA_MARBUTA": "تاء مربوطة (Taa Marbuta)",
            "ARAB_ORAL_EXPR": "التعبير الشفهي (Oral Expression)",
            "ARAB_READING_COMP": "القراءة والفهم (Reading Comprehension)",
            "ARAB_VOCABULARY": "المفردات والتراكيب (Vocabulary)",
            "MATH_ADDITION": "الجمع والطرح (Addition & Subtraction)",
            "MATH_MULTIPLICATION": "الضرب والقسمة (Multiplication & Division)",
            "MATH_GEOMETRY": "الأشكال الهندسية (Geometry & Shapes)",
            "MATH_FRACTIONS": "الكسور (Fractions)",
            "FREN_GRAMMAR": "Grammaire française (French Grammar)",
            "FREN_VOCAB": "Vocabulaire (French Vocabulary)",
            "SCI_LIVING_THINGS": "الكائنات الحية (Living Things)",
            "SCI_PHYSICAL": "الظواهر الفيزيائية (Physical Phenomena)",
        }

        def get_competency_name(cid: str) -> str:
            if cid in COMPETENCY_NAMES:
                return COMPETENCY_NAMES[cid]
            return cid.replace("_", " ").title()

        strengths = []
        gaps = []
        in_progress = []

        for item in mastery_profiles:
            cid, mlevel = extract_info(item)
            cname = get_competency_name(cid)

            if mlevel in ["MASTERED", "PROFICIENT"]:
                strengths.append((cid, cname, mlevel))
            elif mlevel in ["ATTEMPTED", "NOT_STARTED"]:
                gaps.append((cid, cname, mlevel))
            elif mlevel == "FAMILIAR":
                in_progress.append((cid, cname, mlevel))

        for idx, (cid, cname, mlevel) in enumerate(strengths[:2]):
            insights.append({
                "id": f"insight-strength-{idx}",
                "type": "STRENGTH",
                "text": f"Child demonstrates strong concept mastery in {cname}.",
                "competency_id": cid,
                "competency_name": cname,
                "mastery_level": mlevel,
            })

        for idx, (cid, cname, mlevel) in enumerate(gaps[:2]):
            insights.append({
                "id": f"insight-gap-{idx}",
                "type": "GAP",
                "text": f"Child needs targeted practice in {cname} to build confidence.",
                "competency_id": cid,
                "competency_name": cname,
                "mastery_level": mlevel,
            })

        if in_progress:
            cid, cname, mlevel = in_progress[0]
            insights.append({
                "id": "insight-progress-0",
                "type": "PROGRESS",
                "text": f"Child is steadily building familiarity with {cname}.",
                "competency_id": cid,
                "competency_name": cname,
                "mastery_level": mlevel,
            })

        if not insights:
            insights.append({
                "id": "insight-general-0",
                "type": "GENERAL",
                "text": "Child is making steady qualitative progress across all competencies.",
                "competency_id": None,
                "competency_name": None,
                "mastery_level": "FAMILIAR",
            })

        return insights
    def generate_summary_message(self, subjects: List[Dict[str, Any]]) -> str:
        """Generate qualitative summary message for parent."""
        if not subjects:
            return "Your child hasn't started any assessments yet."

        strongest = max(subjects, key=lambda x: x["score"])
        weakest = min(subjects, key=lambda x: x["score"])

        if strongest["score"] >= 80 and weakest["score"] >= 60:
            return f"Great progress! Your child excels in {strongest['name']} and is doing well across all subjects."
        elif strongest["score"] >= 80:
            return f"Your child shows strong skills in {strongest['name']}. Consider spending more time on {weakest['name']}."
        elif weakest["score"] < 40:
            return f"Your child is making progress. Focus on {weakest['name']} with short daily practice sessions."
        else:
            return "Your child is steadily improving. Keep encouraging their efforts in all subjects!"

    def generate_recommendations(
        self, subjects: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Generate actionable recommendations for parent."""
        recommendations = []

        for subject in subjects:
            if subject["score"] < 50:
                recommendations.append({
                    "title": f"Focus on {subject['name']}",
                    "description": f"Practice {subject['name'].lower()} concepts with 10-minute daily sessions.",
                    "duration": "10 minutes",
                    "priority": "high",
                })
            elif subject["score"] < 75:
                recommendations.append({
                    "title": f"Reinforce {subject['name']}",
                    "description": f"Continue building {subject['name'].lower()} skills through guided exercises.",
                    "duration": "15 minutes",
                    "priority": "medium",
                })

        recommendations.append({
            "title": "Encourage Regular Practice",
            "description": "Celebrate your child's efforts and progress to keep them motivated.",
            "duration": "Daily",
            "priority": "low",
        })

        return recommendations[:3]

    async def get_child_dashboard_data(self, student_id: UUID) -> Dict[str, Any]:
        """Get complete dashboard data for a child."""
        student = await self.repo.get_child_by_id(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")

        subjects = await self.get_child_subjects(student_id)
        activities = await self.get_recent_activities(student_id)
        profiles = await self.repo.get_child_competency_profiles(student_id)
        insights = self.generate_insights(profiles if profiles else subjects)
        summary = self.generate_summary_message(subjects)
        recommendations = self.generate_recommendations(subjects)

        if subjects:
            avg_score = sum(s["score"] for s in subjects) / len(subjects)
        else:
            avg_score = 0

        student_name = getattr(student, "full_name", None) or getattr(student, "email", None) or f"Student {str(student_id)[:8]}"

        return {
            "id": str(student_id),
            "name": student_name,
            "subjects": subjects,
            "recent_activities": activities,
            "summary": summary,
            "insights": insights,
            "recommendations": recommendations,
            "overall_progress": round(avg_score, 1),
            "last_active": activities[0]["timestamp"] if activities else None,
        }

    async def get_parent_dashboard(self, parent_id: UUID) -> Dict[str, Any]:
        """Get complete dashboard for a parent."""
        children = await self.get_children_for_parent(parent_id)

        children_data = []
        for child in children:
            child_data = await self.get_child_dashboard_data(child.id)
            children_data.append(child_data)

        return {
            "parent_id": str(parent_id),
            "children_count": len(children_data),
            "children": children_data,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


# Alias DashboardService to DashboardAggregator for compatibility
DashboardService = DashboardAggregator
