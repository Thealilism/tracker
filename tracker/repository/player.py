"""Player state read/write operations."""

import math
import sqlite3

from tracker.models.player import PlayerState

TITLES = [
    (1, "Novice Builder"),
    (5, "Habit Squire"),
    (10, "Discipline Knight"),
    (20, "Atomic Master"),
    (35, "Identity Forged"),
]


def get_state(conn: sqlite3.Connection) -> PlayerState:
    """Return the player state (single row, id=1)."""
    row = conn.execute("SELECT * FROM player_state WHERE id = 1").fetchone()
    return PlayerState(
        level=row["level"],
        total_xp=row["total_xp"],
        streak_freezes=row["streak_freezes"],
        title=row["title"],
        permanent_xp_multiplier=row["permanent_xp_multiplier"],
    )


def add_xp(conn: sqlite3.Connection, amount: int) -> PlayerState:
    """Add XP, recalculate level and title. Returns updated state."""
    conn.execute(
        "UPDATE player_state SET total_xp = total_xp + ? WHERE id = 1",
        (amount,),
    )
    # Recalculate level
    row = conn.execute("SELECT total_xp FROM player_state WHERE id = 1").fetchone()
    new_level = xp_to_level(row["total_xp"])
    new_title = level_to_title(new_level)
    conn.execute(
        "UPDATE player_state SET level = ?, title = ? WHERE id = 1",
        (new_level, new_title),
    )
    return get_state(conn)


def add_boss_defeat(conn: sqlite3.Connection) -> None:
    """Increment permanent XP multiplier by 0.1."""
    conn.execute(
        "UPDATE player_state SET permanent_xp_multiplier = ROUND(permanent_xp_multiplier + 0.1, 1) WHERE id = 1"
    )


def use_freeze(conn: sqlite3.Connection) -> bool:
    """Use one streak freeze. Returns True if successful, False if none left."""
    state = get_state(conn)
    if state.streak_freezes <= 0:
        return False
    conn.execute(
        "UPDATE player_state SET streak_freezes = streak_freezes - 1 WHERE id = 1"
    )
    return True


def replenish_freezes(conn: sqlite3.Connection) -> None:
    """Reset streak freezes to 1 (called monthly)."""
    conn.execute("UPDATE player_state SET streak_freezes = 1 WHERE id = 1")


def xp_to_level(total_xp: int) -> int:
    """Level formula: floor(sqrt(xp / 100)) + 1."""
    return math.floor(math.sqrt(total_xp / 100)) + 1


def level_to_title(level: int) -> str:
    """Map level to a title."""
    current = "Novice Builder"
    for threshold, title in TITLES:
        if level >= threshold:
            current = title
    return current
