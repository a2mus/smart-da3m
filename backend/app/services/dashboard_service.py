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

    async def generate_daily_recommendation(
        self, student_id: UUID, subjects: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate exactly one off-platform reinforcement activity recommendation per child per day."""
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        cache_key = f"{student_id}_{today_str}"

        if hasattr(self, "_daily_cache") and cache_key in self._daily_cache:
            return self._daily_cache[cache_key]

        failed_comp = None
        if hasattr(self.repo, "get_latest_failed_competency"):
            failed_comp = await self.repo.get_latest_failed_competency(student_id)

        OFF_PLATFORM_TEMPLATES = [
            {
                "competency_key": "ARABIC",
                "title": "Practice writing تاء مربوطة with sand tray",
                "description": "Practice writing تاء مربوطة with your child for 10 minutes using a sand tray or finger paint to reinforce letter endings.",
                "duration": "10 minutes",
                "priority": "high",
                "activity_type": "OFF_PLATFORM",
                "off_platform": True,
            },
            {
                "competency_key": "MATH",
                "title": "Counting physical kitchen objects",
                "description": "Count 10 household items or toys with your child and practice grouping them into sets of 5 to strengthen number sense.",
                "duration": "10 minutes",
                "priority": "medium",
                "activity_type": "OFF_PLATFORM",
                "off_platform": True,
            },
            {
                "competency_key": "FRENCH",
                "title": "Daily vocabulary flashcard game",
                "description": "Play a 10-minute quiet naming game with household items in French to boost vocabulary retention.",
                "duration": "10 minutes",
                "priority": "medium",
                "activity_type": "OFF_PLATFORM",
                "off_platform": True,
            },
        ]

        if failed_comp:
            comp_id_upper = (str(failed_comp.competency_id) if failed_comp.competency_id else "").upper()
            selected = next(
                (t for t in OFF_PLATFORM_TEMPLATES if t["competency_key"] in comp_id_upper),
                OFF_PLATFORM_TEMPLATES[0],
            )
            rec = {
                **selected,
                "competency_id": str(failed_comp.competency_id) if failed_comp.competency_id else None,
            }
        else:
            valid_subjects = [
                s for s in (subjects or [])
                if isinstance(s, dict) and isinstance(s.get("score"), (int, float)) and s.get("name")
            ]
            weakest = min(valid_subjects, key=lambda x: x["score"]) if valid_subjects else None
            subject_name = (weakest["name"] if weakest else "").upper()
            if "MATH" in subject_name or "حساب" in subject_name or "رياضيات" in subject_name:
                rec = OFF_PLATFORM_TEMPLATES[1]
            elif "FRENCH" in subject_name or "فرنسية" in subject_name:
                rec = OFF_PLATFORM_TEMPLATES[2]
            else:
                rec = OFF_PLATFORM_TEMPLATES[0]

        if not hasattr(self, "_daily_cache"):
            self._daily_cache = {}
        self._daily_cache[cache_key] = rec
        return rec

    async def get_child_dashboard_data(self, student_id: UUID) -> Dict[str, Any]:
        """Get complete dashboard data for a child."""
        student = await self.repo.get_child_by_id(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")

        subjects = await self.get_child_subjects(student_id)
        activities = await self.get_recent_activities(student_id)
        summary = self.generate_summary_message(subjects)
        recommendations = self.generate_recommendations(subjects)
        try:
            daily_recommendation = await self.generate_daily_recommendation(student_id, subjects)
        except Exception:
            daily_recommendation = None

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
            "recommendations": recommendations,
            "daily_recommendation": daily_recommendation,
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
