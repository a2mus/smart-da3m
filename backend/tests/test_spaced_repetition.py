"""
Tests for Spaced Repetition (FR-16).
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.engines.diagnostic_engine import QuestionSelector
from app.engines.spaced_repetition import SpacedRepetitionScheduler
from app.models.spaced_repetition import SpacedRepetition


def test_spaced_repetition_scheduler_initial_failure():
    """Verify initial failure sets 1-day interval."""
    scheduler = SpacedRepetitionScheduler()
    now = datetime(2026, 8, 1, 12, 0, 0, tzinfo=timezone.utc)

    next_date, interval, ease = scheduler.calculate_next_review(
        current_interval=1, ease_factor=2.5, is_correct=False, current_time=now
    )

    assert interval == 1
    assert next_date == now + timedelta(days=1)
    assert ease == 2.3


def test_spaced_repetition_scheduler_correct_progression():
    """Verify correct answer progression: 1d -> 3d -> 7d -> (interval * ease)."""
    scheduler = SpacedRepetitionScheduler()
    now = datetime(2026, 8, 1, 12, 0, 0, tzinfo=timezone.utc)

    # 1 -> 3
    next_date1, int1, ease1 = scheduler.calculate_next_review(
        current_interval=1, ease_factor=2.5, is_correct=True, current_time=now
    )
    assert int1 == 3
    assert next_date1 == now + timedelta(days=3)

    # 3 -> 7
    next_date2, int2, ease2 = scheduler.calculate_next_review(
        current_interval=3, ease_factor=ease1, is_correct=True, current_time=now
    )
    assert int2 == 7
    assert next_date2 == now + timedelta(days=7)

    # 7 -> int(7 * 2.7) = 18
    next_date3, int3, ease3 = scheduler.calculate_next_review(
        current_interval=7, ease_factor=ease2, is_correct=True, current_time=now
    )
    assert int3 == int(7 * ease2)
    assert next_date3 == now + timedelta(days=int3)


def test_spaced_repetition_scheduler_incorrect_reset():
    """Verify incorrect answer resets interval back to 1 day."""
    scheduler = SpacedRepetitionScheduler()
    now = datetime(2026, 8, 1, 12, 0, 0, tzinfo=timezone.utc)

    next_date, interval, ease = scheduler.calculate_next_review(
        current_interval=7, ease_factor=2.5, is_correct=False, current_time=now
    )

    assert interval == 1
    assert next_date == now + timedelta(days=1)


def test_question_selector_includes_and_tags_due_review_items():
    """Verify QuestionSelector prioritizes due review questions and tags them with is_review=True."""
    selector = QuestionSelector()
    q1_id = str(uuid4())
    q2_id = str(uuid4())

    questions = [
        {"id": q1_id, "difficulty_level": 5},
        {"id": q2_id, "difficulty_level": 5},
    ]

    # Select with q2 as a due review item
    selected = selector.select_next_question(
        questions=questions,
        answered_question_ids=[],
        current_mastery=0.5,
        target_misconceptions=[],
        due_review_question_ids=[q2_id],
    )

    assert selected is not None
    assert selected["id"] == q2_id
    assert selected["is_review"] is True


def test_question_selector_non_review_item_tagged_false():
    """Verify non-review questions selected get is_review=False."""
    selector = QuestionSelector()
    q1_id = str(uuid4())

    questions = [{"id": q1_id, "difficulty_level": 5}]

    selected = selector.select_next_question(
        questions=questions,
        answered_question_ids=[],
        current_mastery=0.5,
        target_misconceptions=[],
        due_review_question_ids=[],
    )

    assert selected is not None
    assert selected["id"] == q1_id
    assert selected["is_review"] is False
