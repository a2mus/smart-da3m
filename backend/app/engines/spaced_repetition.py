"""
Stateless Spaced Repetition engine for FR-16.
Calculates review schedules and intervals for failed items.
"""

from datetime import datetime, timedelta, timezone
from typing import Tuple


class SpacedRepetitionScheduler:
    """
    Stateless scheduler for spaced re-surfacing of failed items.
    Default intervals: 1-day -> 3-day -> 7-day -> (interval * ease_factor).
    """

    def calculate_next_review(
        self,
        current_interval: int,
        ease_factor: float,
        is_correct: bool,
        current_time: datetime = None,
    ) -> Tuple[datetime, int, float]:
        """
        Calculate the next review date, interval days, and ease factor based on performance.
        Returns: (next_review_date, new_interval_days, new_ease_factor)
        """
        now = current_time or datetime.now(timezone.utc)

        if not is_correct:
            # Incorrect answer resets interval to 1 day
            new_interval = 1
            new_ease = max(1.3, ease_factor - 0.2)
        else:
            # Correct answer increases interval (1 -> 3 -> 7 -> interval * ease_factor)
            if current_interval <= 1:
                new_interval = 3
            elif current_interval <= 3:
                new_interval = 7
            else:
                new_interval = max(int(current_interval * ease_factor), current_interval + 1)

            new_ease = min(3.0, ease_factor + 0.1)

        next_review_date = now + timedelta(days=new_interval)
        return next_review_date, new_interval, new_ease
