"""Daily log model."""

from dataclasses import dataclass
from typing import Literal

LogStatus = Literal["done", "not_done", "skipped"]


@dataclass
class DailyLog:
    """A single day's log entry for one habit."""

    habit_id: int
    date: str  # ISO format: YYYY-MM-DD
    status: LogStatus
    reflection: str | None = None
    difficulty: int | None = None  # 1-5

    id: int | None = None
    created_at: str | None = None
