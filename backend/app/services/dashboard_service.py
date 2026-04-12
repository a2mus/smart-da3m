"""
Dashboard service for aggregating parent dashboard data.
Pulls data from diagnostic, remediation, and competency sources.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Module
from app.models.diagnostic import (
    CompetencyProfile,
    DiagnosticSession,
    MasteryLevel,
)
from app.models.remediation import RemediationPath
from app.models.user import User, UserRole


class DashboardAggregator:
    """
    Aggregates dashboard data for parents.

    Pulls together:
    - Child profiles and progress
    - Subject competency data
    - Recent activities
    - Smart recommendations
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_children_for_parent(
        self, parent_id: UUID
    ) -> List[User]:
        """Get all children for a parent."""
        result = await self.db.execute(
            select(User).where(
                User.parent_id == parent_id,
                User.role == UserRole.STUDENT,
            )
        )
        return list(result.scalars().all())

    async def get_child_subjects(
        self, student_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get subject competency data for a child."""
        result = await self.db.execute(
            select(CompetencyProfile).where(
                CompetencyProfile.student_id == student_id
            )
        )
        profiles = result.scalars().all()

        subjects = []
        for profile in profiles:
            # Map competency_id to subject name
            # In production, this would query a subject/competency mapping table
            subject_name = self._map_competency_to_subject(
                profile.competency_id
            )

            # Convert mastery level to score (0-100)
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
        # Simple mapping - in production would use database lookup
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

        # Get recent diagnostic sessions
        result = await self.db.execute(
            select(DiagnosticSession)
            .where(DiagnosticSession.student_id == student_id)
            .order_by(DiagnosticSession.started_at.desc())
            .limit(limit)
        )
        sessions = result.scalars().all()

        for session in sessions:
            activities.append({
                "type": "DIAGNOSTIC",
                "title": f"Completed diagnostic assessment",
                "timestamp": session.completed_at.isoformat()
                if session.completed_at
                else session.started_at.isoformat(),
                "status": "completed" if session.completed_at else "in_progress",
            })

        # Get recent remediation paths
        result = await self.db.execute(
            select(RemediationPath)
            .where(RemediationPath.student_id == student_id)
            .order_by(RemediationPath.started_at.desc())
            .limit(limit)
        )
        paths = result.scalars().all()

        for path in paths:
            if path.atoms_completed and len(path.atoms_completed) > 0:
                activities.append({
                    "type": "REMEDIATION",
                    "title": f"Learning activity completed",
                    "timestamp": path.started_at.isoformat(),
                    "progress": len(path.atoms_completed),
                })

        # Sort by timestamp descending
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities[:limit]

    def generate_summary_message(
        self, subjects: List[Dict[str, Any]]
    ) -> str:
        """Generate qualitative summary message for parent."""
        if not subjects:
            return "Your child hasn't started any assessments yet."

        # Find strongest and weakest subjects
        strongest = max(subjects, key=lambda x: x["score"])
        weakest = min(subjects, key=lambda x: x["score"])

        # Generate appropriate message
        if strongest["score"] >= 80 and weakest["score"] >= 60:
            return f"Great progress! Your child excels in {strongest['name']} and is doing well across all subjects."
        elif strongest["score"] >= 80:
            return f"Your child shows strong skills in {strongest['name']}. Consider spending more time on {weakest['name']}."
        elif weakest["score"] < 40:
            return f"Your child is making progress. Focus on {weakest['name']} with short daily practice sessions."
        else:
            return f"Your child is steadily improving. Keep encouraging their efforts in all subjects!"

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

        # Add general recommendation
        recommendations.append({
            "title": "Encourage Regular Practice",
            "description": "Celebrate your child's efforts and progress to keep them motivated.",
            "duration": "Daily",
            "priority": "low",
        })

        return recommendations[:3]  # Limit to top 3

    async def get_child_dashboard_data(
        self, student_id: UUID
    ) -> Dict[str, Any]:
        """Get complete dashboard data for a child."""
        # Get student info
        result = await self.db.execute(
            select(User).where(User.id == student_id)
        )
        student = result.scalar_one_or_none()

        if not student:
            raise ValueError(f"Student {student_id} not found")

        # Get subjects
        subjects = await self.get_child_subjects(student_id)

        # Get activities
        activities = await self.get_recent_activities(student_id)

        # Generate insights
        summary = self.generate_summary_message(subjects)
        recommendations = self.generate_recommendations(subjects)

        # Calculate overall progress
        if subjects:
            avg_score = sum(s["score"] for s in subjects) / len(subjects)
        else:
            avg_score = 0

        return {
            "id": str(student_id),
            "name": f"Student {str(student_id)[:8]}",  # Placeholder name
            "subjects": subjects,
            "recent_activities": activities,
            "summary": summary,
            "recommendations": recommendations,
            "overall_progress": round(avg_score, 1),
            "last_active": activities[0]["timestamp"] if activities else None,
        }

    async def get_parent_dashboard(
        self, parent_id: UUID
    ) -> Dict[str, Any]:
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


# Add missing import
from datetime import datetime, timezone
