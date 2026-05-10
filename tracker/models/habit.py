"""Habit model."""

from dataclasses import dataclass
from typing import Literal

HabitType = Literal["build", "break"]


@dataclass
class Habit:
    """A habit following the Atomic Habits 4-law framework."""

    name: str
    category: str = "general"
    identity_statement: str | None = None
    cue: str | None = None
    craving: str | None = None
    response: str | None = None
    reward: str | None = None
    type: HabitType = "build"
    xp_value: int = 10
    stacking_order: int | None = None

    # Set by DB on insert
    id: int | None = None
    created_at: str | None = None
