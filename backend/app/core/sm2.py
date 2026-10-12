from typing import Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel


class SM2Result(BaseModel):
    ease_factor: float
    interval_days: int
    repetitions: int
    due_date: datetime


def calculate_sm2(
    rating: int,
    current_ease_factor: float = 2.5,
    current_repetitions: int = 0,
    current_interval: int = 0,
    review_date: Optional[datetime] = None
) -> SM2Result:
    """
    SuperMemo-2 (SM-2) Spaced Repetition Algorithm.
    Rating scale: 0-5.
    - 5: perfect response
    - 4: correct response after a hesitation
    - 3: correct response recalled with serious difficulty
    - 2: incorrect response; where the correct one seemed easy to recall
    - 1: incorrect response; the correct one remembered
    - 0: complete blackout
    """
    q = max(0, min(5, rating))
    now = review_date or datetime.now(timezone.utc)

    # 1. Update repetitions & interval
    if q < 3:
        # Failure: restart repetition cycle
        repetitions = 0
        interval = 1
    else:
        # Success: progress interval
        if current_repetitions == 0:
            interval = 1
        elif current_repetitions == 1:
            interval = 6
        else:
            interval = max(1, round(current_interval * current_ease_factor))
        repetitions = current_repetitions + 1

    # 2. Update Ease Factor (EF)
    # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    diff = 5 - q
    new_ef = current_ease_factor + (0.1 - diff * (0.08 + diff * 0.02))
    new_ef = max(1.3, round(new_ef, 2))

    due_date = now + timedelta(days=interval)

    return SM2Result(
        ease_factor=new_ef,
        interval_days=interval,
        repetitions=repetitions,
        due_date=due_date,
    )
