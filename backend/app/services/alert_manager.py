"""
Alert manager service for detecting and generating pedagogical alerts.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from app.models.alert import AlertSeverity, AlertTriggerType


class ConsecutiveFailureDetector:
    """
    Detects consecutive failures of the same exercise type.

    Triggers WARNING alert after 3 consecutive failures.
    """

    def __init__(self, threshold: int = 3):
        self.threshold = threshold

    def detect(self, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect consecutive failures in answer history.

        Args:
            answers: List of answer results with misconception_id

        Returns:
            Detection result with triggered flag and details
        """
        if len(answers) < self.threshold:
            return {"triggered": False}

        # Track consecutive failures by misconception type
        current_streak = 0
        current_misconception = None

        for answer in answers:
            if not answer.get("is_correct"):
                misconception = answer.get("misconception_id")

                if misconception == current_misconception:
                    current_streak += 1
                else:
                    current_misconception = misconception
                    current_streak = 1

                if current_streak >= self.threshold and current_misconception:
                    return {
                        "triggered": True,
                        "severity": AlertSeverity.WARNING,
                        "trigger_type": AlertTriggerType.REPEATED_FAILURE,
                        "consecutive_failures": current_streak,
                        "misconception_id": current_misconception,
                    }
            else:
                # Reset on correct answer
                current_streak = 0
                current_misconception = None

        return {"triggered": False}


class ResponsePatternDetector:
    """
    Detects concerning response patterns indicating frustration or abandonment.
    """

    def detect_frustration(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect frustration from declining speed and low accuracy.

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

    def detect_abandonment(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect abandoned sessions (started but not completed within timeframe).

        Args:
            session: Session data with timestamps and answer counts

        Returns:
            Detection result
        """
        from datetime import datetime, timezone

        if session.get("completed_at"):
            return {"triggered": False}

        started_at = session.get("started_at")
        if not started_at:
            return {"triggered": False}

        # Check if session has been inactive for > 30 minutes
        if isinstance(started_at, str):
            started_at = datetime.fromisoformat(started_at.replace("Z", "+00:00"))

        elapsed_minutes = (datetime.now(timezone.utc) - started_at).total_seconds() / 60

        if elapsed_minutes > 30:
            answers_count = session.get("answers_count", 0)
            expected_count = session.get("expected_count", 10)

            if answers_count < expected_count * 0.5:  # Less than 50% complete
                return {
                    "triggered": True,
                    "severity": AlertSeverity.WARNING,
                    "trigger_type": AlertTriggerType.ABANDONMENT,
                    "elapsed_minutes": elapsed_minutes,
                    "answers_completed": answers_count,
                    "expected_answers": expected_count,
                }

        return {"triggered": False}


class InactivityDetector:
    """
    Detects extended periods of student inactivity.
    """

    def __init__(self, inactivity_threshold_days: int = 7):
        self.inactivity_threshold_days = inactivity_threshold_days

    def detect(self, last_login: datetime) -> Dict[str, Any]:
        """
        Detect inactivity beyond threshold.

        Args:
            last_login: Datetime of last student login

        Returns:
            Detection result
        """
        from datetime import datetime, timezone

        if isinstance(last_login, str):
            last_login = datetime.fromisoformat(last_login.replace("Z", "+00:00"))

        days_inactive = (datetime.now(timezone.utc) - last_login).days

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
    """
    Generates pedagogical alerts with appropriate messages and recipients.
    """

    def __init__(self):
        self._alert_cache: set = set()  # Track recent alerts to avoid duplicates

    def generate(
        self,
        student_id: UUID,
        detection: Dict[str, Any],
        existing_alert_ids: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Generate an alert from detection result.

        Args:
            student_id: Student UUID
            detection: Detection result from a detector
            existing_alert_ids: IDs of existing alerts to avoid duplicates

        Returns:
            Alert data or None if duplicate/no alert needed
        """
        if not detection.get("triggered"):
            return None

        # Check for duplicates
        alert_key = f"{student_id}:{detection['trigger_type']}"
        if alert_key in self._alert_cache:
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

        # Cache to prevent duplicates
        self._alert_cache.add(alert_key)

        return alert

    def _generate_messages(self, detection: Dict[str, Any]) -> Dict[str, str]:
        """Generate appropriate messages for parent and expert."""
        trigger_type = detection["trigger_type"]
        severity = detection["severity"]

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
            expert = (
                f"Declining response speed ({detection.get('average_response_time', 'N/A')}ms avg) "
                f"combined with low accuracy ({detection.get('accuracy', 'N/A'):.0%}) "
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
                f"Student failed post-remediation Passport assessment. "
                f"Remediation pathway was insufficient. "
                f"CRITICAL: May need in-person intervention or alternative teaching approach. "
                f"Current competency gap persists despite intervention."
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

    def _determine_recipients(self, severity: AlertSeverity) -> List[str]:
        """Determine alert recipients based on severity."""
        if severity == AlertSeverity.CRITICAL:
            return ["parent", "expert"]
        elif severity == AlertSeverity.WARNING:
            return ["parent", "expert"]
        else:  # INFO
            return ["parent"]  # INFO alerts primarily for parents

    def suggest_auto_grouping(
        self, students_with_same_error: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Suggest auto-grouping students with shared error patterns.

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
    """
    Main alert manager coordinating detection and generation.
    """

    def __init__(self):
        self.failure_detector = ConsecutiveFailureDetector()
        self.pattern_detector = ResponsePatternDetector()
        self.inactivity_detector = InactivityDetector()
        self.generator = AlertGenerator()

    def check_session_for_alerts(
        self,
        student_id: UUID,
        session_data: Dict[str, Any],
        answers: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Check a completed session for alert triggers.

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

    def check_inactivity(self, student_id: UUID, last_login: datetime) -> Optional[Dict[str, Any]]:
        """Check for inactivity alert."""
        detection = self.inactivity_detector.detect(last_login)
        if detection["triggered"]:
            return self.generator.generate(student_id, detection)
        return None


# Import for uuid generation
from uuid import uuid4
