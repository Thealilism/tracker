"""Player state model."""

from dataclasses import dataclass


@dataclass
class PlayerState:
    """The player's gamification state (single row, id=1)."""

    level: int = 1
    total_xp: int = 0
    streak_freezes: int = 1
    title: str = "Novice Builder"
    permanent_xp_multiplier: float = 1.0
