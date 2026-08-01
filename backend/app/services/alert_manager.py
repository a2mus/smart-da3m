"""Alert manager service for detecting and generating pedagogical alerts.
"""

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.tenant import reset_active_organization_id, set_active_organization_id
from app.models.alert import (
    AlertSeverity,
    AlertStatus,
    AlertTriggerType,
    PedagogicalAlert,
)
from app.services.event_publisher import publish_tenant_event

logger = logging.getLogger(__name__)


class ConsecutiveFailureDetector:
    """Detects failure thresholds over window days (OQ-4).
    """

    def __init__(
        self,
        threshold: int | None = None,
        warning_threshold: int | None = None,
        critical_threshold: int | None = None,
        window_days: int | None = None,
    ):
        if threshold is not None:
            self.warning_threshold = warning_threshold if warning_threshold is not None else threshold
            self.critical_threshold = critical_threshold if critical_threshold is not None else threshold
            self.min_threshold = threshold
        else:
            self.warning_threshold = (
                warning_threshold
                if warning_threshold is not None
                else settings.ALERT_WARNING_FAILURE_THRESHOLD
            )
            self.critical_threshold = (
                critical_threshold
                if critical_threshold is not None
                else settings.ALERT_CRITICAL_FAILURE_THRESHOLD
            )
            self.min_threshold = 1
        self.window_days = (
            window_days
            if window_days is not None
            else settings.ALERT_FAILURE_WINDOW_DAYS
        )

    def detect(self, answers: list[dict[str, Any]]) -> dict[str, Any]:
        """Detect failure levels in answer history according to OQ-4 thresholds.

        Args:
            answers: List of answer results with timestamp and misconception_id/is_correct

        Returns:
            Detection result with severity, trigger_type, and context details
        """
        if not answers:
            return {"triggered": False}

        now = datetime.now(UTC)
        window_seconds = self.window_days * 86400

        recent_answers = []
        for ans in answers:
            ts = ans.get("timestamp")
            if ts:
                if isinstance(ts, str):
                    ts_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                else:
                    ts_dt = ts
                if (now - ts_dt).total_seconds() > window_seconds:
                    continue
            recent_answers.append(ans)

        if not recent_answers:
            return {"triggered": False}

        current_streak = 0
        current_misconception = None
        max_streak = 0
        max_misconception = None

        for answer in recent_answers:
            if not answer.get("is_correct"):
                misconception = answer.get("misconception_id", "default_gap")

                if misconception == current_misconception:
                    current_streak += 1
                else:
                    current_misconception = misconception
                    current_streak = 1

                if current_streak > max_streak:
                    max_streak = current_streak
                    max_misconception = current_misconception
            else:
                current_streak = 0
                current_misconception = None

        if max_streak < self.min_threshold or not max_misconception:
            return {"triggered": False}

        if max_streak >= self.critical_threshold:
            severity = AlertSeverity.CRITICAL
        elif max_streak >= self.warning_threshold:
            severity = AlertSeverity.WARNING
        else:
            severity = AlertSeverity.INFO

        return {
            "triggered": True,
            "severity": severity,
            "trigger_type": AlertTriggerType.REPEATED_FAILURE,
            "consecutive_failures": max_streak,
            "misconception_id": max_misconception,
        }


class ResponsePatternDetector:
    """Detects concerning response patterns indicating frustration or abandonment.
    """

    def detect_frustration(self, responses: list[dict[str, Any]]) -> dict[str, Any]:
        """Detect frustration from declining speed and low accuracy.

        Args:
            responses: List of response data with time_ms and is_correct

        Returns:
            Detection result
        """
        if len(responses) < 3:
            return {"triggered": False}

        # Check for declining speed
        times = [r["time_ms"] for r in responses]
        is_declining = times[-1] > times[0] * 1.5

        # Check for low accuracy
        correct_count = sum(1 for r in responses if r.get("is_correct"))
        accuracy = correct_count / len(responses)
        is_low_accuracy = accuracy < 0.5

        if is_declining and is_low_accuracy:
            return {
                "triggered": True,
                "severity": AlertSeverity.INFO,
                "trigger_type": AlertTriggerType.FRUSTRATION,
                "indicators": ["declining_speed", "low_accuracy"],
                "average_response_time": sum(times) / len(times),
                "accuracy": accuracy,
            }

        return {"triggered": False}

    def detect_abandonment(self, session: dict[str, Any]) -> dict[str, Any]:
        """Detect abandoned sessions (started but not completed within timeframe).

        Args:
            session: Session data with timestamps and answer counts

        Returns:
            Detection result
        """
        from datetime import datetime

        if session.get("completed_at"):
            return {"triggered": False}

        started_at = session.get("started_at")
        if not started_at:
            return {"triggered": False}

        # Check if session has been inactive for > 30 minutes
        if isinstance(started_at, str):
            started_at = datetime.fromisoformat(started_at.replace("Z", "+00:00"))

        elapsed_minutes = (datetime.now(UTC) - started_at).total_seconds() / 60

        if elapsed_minutes >= 29.9:
            answers_count = session.get("answers_count", 0)
            expected_count = session.get("expected_count", 10)

            if answers_count < expected_count * 0.5:  # Less than 50% complete
                return {
                    "triggered": True,
                    "severity": AlertSeverity.CRITICAL,
                    "trigger_type": AlertTriggerType.ABANDONMENT,
                    "elapsed_minutes": elapsed_minutes,
                    "answers_completed": answers_count,
                    "expected_answers": expected_count,
                }

        return {"triggered": False}


class InactivityDetector:
    """Detects extended periods of student inactivity.
    """

    def __init__(self, inactivity_threshold_days: int = 7):
        self.inactivity_threshold_days = inactivity_threshold_days

    def detect(self, last_login: datetime) -> dict[str, Any]:
        """Detect inactivity beyond threshold.

        Args:
            last_login: Datetime of last student login

        Returns:
            Detection result
        """
        from datetime import datetime

        if isinstance(last_login, str):
            last_login = datetime.fromisoformat(last_login.replace("Z", "+00:00"))

        days_inactive = (datetime.now(UTC) - last_login).days

        if days_inactive >= self.inactivity_threshold_days:
            return {
                "triggered": True,
                "severity": AlertSeverity.INFO,
                "trigger_type": AlertTriggerType.INACTIVITY,
                "days_inactive": days_inactive,
                "threshold": self.inactivity_threshold_days,
            }

        return {"triggered": False}


class AlertGenerator:
    """Generates pedagogical alerts with appropriate messages and recipients.
    """

    def __init__(self, cooldown_hours: int | None = None):
        self._alert_cache: dict[str, datetime] = {}
        self.cooldown_hours = (
            cooldown_hours if cooldown_hours is not None else settings.ALERT_COOLDOWN_HOURS
        )

    def generate(
        self,
        student_id: UUID,
        detection: dict[str, Any],
        existing_alert_ids: list[str] | None = None,
    ) -> dict[str, Any] | None:
        """Generate an alert from detection result with cooldown duplicate prevention.

        Args:
            student_id: Student UUID
            detection: Detection result from a detector
            existing_alert_ids: IDs of existing alerts to avoid duplicates

        Returns:
            Alert data or None if duplicate/no alert needed
        """
        if not detection.get("triggered"):
            return None

        key_suffix = detection.get("misconception_id") or detection.get("competency_id") or ""
        alert_key = f"{student_id}:{detection['trigger_type']}:{key_suffix}"
        now = datetime.now(UTC)

        if alert_key in self._alert_cache:
            last_time = self._alert_cache[alert_key]
            if (now - last_time).total_seconds() < self.cooldown_hours * 3600:
                return None

        if existing_alert_ids and alert_key in [str(id) for id in existing_alert_ids]:
            return None

        # Generate messages based on trigger type and severity
        messages = self._generate_messages(detection)

        # Determine recipients based on severity
        recipients = self._determine_recipients(detection["severity"])

        alert = {
            "id": uuid4(),
            "student_id": student_id,
            "severity": detection["severity"],
            "trigger_type": detection["trigger_type"],
            "simplified_message": messages["simplified"],
            "expert_message": messages["expert"],
            "recommended_action": messages["action"],
            "recipients": recipients,
            "context_data": detection,
        }

        # Cache to prevent duplicates within cooldown window
        self._alert_cache[alert_key] = now

        return alert

    def _generate_messages(self, detection: dict[str, Any]) -> dict[str, str]:
        """Generate appropriate messages for parent and expert."""
        trigger_type = detection["trigger_type"]

        if trigger_type == AlertTriggerType.REPEATED_FAILURE:
            simplified = (
                "Your child is working hard but struggling with a specific concept. "
                "Consider spending some extra time reviewing this area together."
            )
            expert = (
                f"Student has failed the same exercise type 3+ consecutive times. "
                f"Misconception: {detection.get('misconception_id', 'Unknown')}. "
                f"Pattern indicates potential gap in prerequisite knowledge. "
                f"Recommended: Targeted micro-learning intervention."
            )
            action = "Review prerequisite concepts with targeted exercises."

        elif trigger_type == AlertTriggerType.FRUSTRATION:
            simplified = (
                "We noticed your child might be feeling frustrated. "
                "A short break or switching to a different activity might help!"
            )
            acc_val = detection.get("accuracy")
            acc_str = f"{acc_val:.0%}" if isinstance(acc_val, (int, float)) else str(acc_val or "N/A")
            expert = (
                f"Declining response speed ({detection.get('average_response_time', 'N/A')}ms avg) "
                f"combined with low accuracy ({acc_str}) "
                f"indicates potential frustration or cognitive overload. "
                f"Consider adjusting difficulty or providing encouragement."
            )
            action = "Simplify difficulty and provide positive reinforcement."

        elif trigger_type == AlertTriggerType.PASSPORT_FAILED:
            simplified = (
                "Your child needs a bit more support. "
                "Consider scheduling a session with their teacher for personalized help."
            )
            expert = (
                "Student failed post-remediation Passport assessment. "
                "Remediation pathway was insufficient. "
                "CRITICAL: May need in-person support or alternative teaching approach. "
                "Current competency gap persists despite intervention."
            )
            action = "Schedule in-person support session. Consider alternative teaching methods."

        elif trigger_type == AlertTriggerType.INACTIVITY:
            days = detection.get("days_inactive", 7)
            simplified = (
                f"It's been {days} days since your child's last session. "
                "Regular practice helps maintain learning momentum!"
            )
            expert = (
                f"Student inactive for {days} days. "
                f"May indicate loss of interest or external factors. "
                f"Consider parent outreach to re-engage."
            )
            action = "Send re-engagement notification to parent."

        elif trigger_type == AlertTriggerType.ABANDONMENT:
            simplified = (
                "Your child started a session but didn't finish. "
                "Check in with them to see if they need help!"
            )
            expert = (
                f"Session abandoned after {detection.get('elapsed_minutes', 'N/A')} minutes. "
                f"Only {detection.get('answers_completed', 0)}/{detection.get('expected_answers', 10)} "
                f"questions attempted. May indicate difficulty spike or external distraction."
            )
            action = "Review session data for difficulty spikes or technical issues."

        else:
            simplified = "An update on your child's learning progress."
            expert = "Alert triggered based on learning pattern analysis."
            action = "Monitor student progress."

        return {
            "simplified": simplified,
            "expert": expert,
            "action": action,
        }

    def _determine_recipients(self, severity: AlertSeverity) -> list[str]:
        """Determine alert recipients based on severity."""
        if severity == AlertSeverity.CRITICAL or severity == AlertSeverity.WARNING:
            return ["parent", "expert"]
        else:  # INFO
            return ["parent"]  # INFO alerts primarily for parents

    def suggest_auto_grouping(
        self, students_with_same_error: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Suggest auto-grouping students with shared error patterns.

        Args:
            students_with_same_error: List of students sharing a misconception

        Returns:
            Grouping suggestion
        """
        MIN_GROUP_SIZE = 3

        if len(students_with_same_error) < MIN_GROUP_SIZE:
            return {"should_group": False}

        # Get shared misconception
        misconception_ids = [s.get("misconception_id") for s in students_with_same_error]
        most_common = max(set(misconception_ids), key=misconception_ids.count)

        return {
            "should_group": True,
            "group_size": len(students_with_same_error),
            "shared_misconception": most_common,
            "recommended_intervention": (
                f"Collective remediation session targeting {most_common}. "
                f"Group size: {len(students_with_same_error)} students."
            ),
        }


class AlertManager:
    """Main alert manager coordinating detection and generation.
    """

    def __init__(self):
        self.failure_detector = ConsecutiveFailureDetector()
        self.pattern_detector = ResponsePatternDetector()
        self.inactivity_detector = InactivityDetector()
        self.generator = AlertGenerator()

    def check_session_for_alerts(
        self,
        student_id: UUID,
        session_data: dict[str, Any],
        answers: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Check a completed session for alert triggers.

        Args:
            student_id: Student UUID
            session_data: Session information
            answers: List of answers from the session

        Returns:
            List of generated alerts
        """
        alerts = []

        # Check for consecutive failures
        failure_detection = self.failure_detector.detect(answers)
        if failure_detection["triggered"]:
            alert = self.generator.generate(student_id, failure_detection)
            if alert:
                alerts.append(alert)

        # Check for frustration patterns
        responses = [
            {"time_ms": a.get("response_time_ms", 10000), "is_correct": a.get("is_correct")}
            for a in answers
        ]
        frustration_detection = self.pattern_detector.detect_frustration(responses)
        if frustration_detection["triggered"]:
            alert = self.generator.generate(student_id, frustration_detection)
            if alert:
                alerts.append(alert)

        # Check for abandonment
        abandonment_detection = self.pattern_detector.detect_abandonment(session_data)
        if abandonment_detection["triggered"]:
            alert = self.generator.generate(student_id, abandonment_detection)
            if alert:
                alerts.append(alert)

        return alerts

    def check_inactivity(self, student_id: UUID, last_login: datetime) -> dict[str, Any] | None:
        """Check for inactivity alert."""
        detection = self.inactivity_detector.detect(last_login)
        if detection["triggered"]:
            return self.generator.generate(student_id, detection)
        return None

    def check_passport_failure(
        self,
        student_id: UUID,
        competency_id: str,
        fail_count: int = 1,
    ) -> dict[str, Any] | None:
        """Generate alert on passport assessment failure according to OQ-4 rules.

        Args:
            student_id: Student UUID
            competency_id: Failed competency identifier
            fail_count: Number of passport failures on this competency

        Returns:
            Generated alert dictionary or None
        """
        severity = (
            AlertSeverity.CRITICAL
            if fail_count >= settings.ALERT_CRITICAL_PASSPORT_FAILS
            else AlertSeverity.WARNING
        )
        detection = {
            "triggered": True,
            "severity": severity,
            "trigger_type": AlertTriggerType.PASSPORT_FAILED,
            "competency_id": competency_id,
            "fail_count": fail_count,
        }
        return self.generator.generate(student_id, detection)

    async def process_and_persist_alerts(
        self,
        alerts: list[dict[str, Any]],
        organization_id: UUID,
        db: AsyncSession,
    ) -> list[PedagogicalAlert]:
        """Persist generated alerts to DB and publish SSE events via Redis Pub/Sub.

        Args:
            alerts: List of alert dictionaries generated by AlertGenerator
            organization_id: Active tenant organization UUID
            db: Async database session

        Returns:
            List of persisted PedagogicalAlert instances
        """
        token = set_active_organization_id(organization_id)
        try:
            saved_alerts = []
            for alert_data in alerts:
                alert_obj = PedagogicalAlert(
                    id=alert_data.get("id") or uuid4(),
                    organization_id=organization_id,
                    student_id=alert_data["student_id"],
                    trigger_type=alert_data["trigger_type"],
                    severity=alert_data["severity"],
                    status=AlertStatus.UNREAD,
                    simplified_message=alert_data["simplified_message"],
                    expert_message=alert_data["expert_message"],
                    context_data=alert_data.get("context_data", {}),
                    recommended_action=alert_data.get("recommended_action"),
                )
                db.add(alert_obj)
                saved_alerts.append(alert_obj)

                trigger_val = (
                    alert_obj.trigger_type.value
                    if hasattr(alert_obj.trigger_type, "value")
                    else str(alert_obj.trigger_type)
                )
                severity_val = (
                    alert_obj.severity.value
                    if hasattr(alert_obj.severity, "value")
                    else str(alert_obj.severity)
                )
                status_val = (
                    alert_obj.status.value
                    if hasattr(alert_obj.status, "value")
                    else str(alert_obj.status)
                )

                payload = {
                    "id": str(alert_obj.id),
                    "student_id": str(alert_obj.student_id),
                    "organization_id": str(organization_id),
                    "trigger_type": trigger_val,
                    "severity": severity_val,
                    "status": status_val,
                    "simplified_message": alert_obj.simplified_message,
                    "expert_message": alert_obj.expert_message,
                    "recommended_action": alert_obj.recommended_action,
                    "created_at": (
                        alert_obj.created_at.isoformat()
                        if alert_obj.created_at
                        else datetime.now(UTC).isoformat()
                    ),
                }

                try:
                    await publish_tenant_event(organization_id, "pedagogical_alert", payload)
                except Exception as exc:
                    logger.error(
                        "Failed to publish pedagogical_alert event to Redis Pub/Sub for org %s: %s",
                        organization_id,
                        exc,
                    )

            if saved_alerts:
                await db.commit()
                for alert_obj in saved_alerts:
                    await db.refresh(alert_obj)

            return saved_alerts
        finally:
            reset_active_organization_id(token)


# Import for uuid generation
