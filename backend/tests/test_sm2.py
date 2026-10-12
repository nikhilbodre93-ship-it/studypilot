from datetime import datetime, timezone, timedelta
from app.core.sm2 import calculate_sm2


def test_sm2_first_repetition_success():
    res = calculate_sm2(rating=4, current_ease_factor=2.5, current_repetitions=0, current_interval=0)
    assert res.repetitions == 1
    assert res.interval_days == 1
    assert res.ease_factor == 2.5


def test_sm2_second_repetition_success():
    res = calculate_sm2(rating=4, current_ease_factor=2.5, current_repetitions=1, current_interval=1)
    assert res.repetitions == 2
    assert res.interval_days == 6


def test_sm2_third_repetition_success():
    res = calculate_sm2(rating=5, current_ease_factor=2.5, current_repetitions=2, current_interval=6)
    assert res.repetitions == 3
    assert res.interval_days == 15  # 6 * 2.5 = 15
    assert res.ease_factor >= 2.6   # Rating 5 increases ease factor


def test_sm2_failure_resets_interval():
    # User had 4 repetitions, but failed (rating 2)
    res = calculate_sm2(rating=2, current_ease_factor=2.5, current_repetitions=4, current_interval=30)
    assert res.repetitions == 0
    assert res.interval_days == 1
    assert res.ease_factor < 2.5


def test_sm2_minimum_ease_factor_floor():
    ef = 1.4
    for _ in range(5):
        res = calculate_sm2(rating=0, current_ease_factor=ef)
        ef = res.ease_factor
    assert ef == 1.3, f"Ease factor floor must be 1.3, got {ef}"


def test_sm2_due_date_calculation():
    now = datetime(2026, 10, 15, 12, 0, 0, tzinfo=timezone.utc)
    res = calculate_sm2(rating=4, current_repetitions=1, current_interval=1, review_date=now)
    expected_due = now + timedelta(days=6)
    assert res.due_date == expected_due
