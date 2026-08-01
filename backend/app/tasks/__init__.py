"""
Celery background tasks package.
"""

from app.tasks.ai_proposal import generate_remediation_proposal

__all__ = ["generate_remediation_proposal"]
