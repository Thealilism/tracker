"""Badge and Quest models."""

from dataclasses import dataclass


@dataclass
class Badge:
    """An achievement badge that can be earned."""

    name: str
    description: str
    icon: str | None = None
    earned_at: str | None = None
    id: int | None = None


@dataclass
class Quest:
    """A daily quest with XP reward."""

    date: str
    description: str
    xp_reward: int = 25
    completed: bool = False
    id: int | None = None
