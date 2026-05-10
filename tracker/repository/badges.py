"""Badge and quest repository operations."""

import random
import sqlite3
from datetime import date

from tracker.models.badge import Badge, Quest

QUEST_POOL = [
    ("Complete 2 health habits", 25),
    ("Write a reflection for any habit", 20),
    ("Complete 3 habits total today", 30),
    ("Do your first habit of the day", 15),
    ("Chain 2 habits in a row", 25),
    ("Complete a habit with difficulty 4+", 20),
    ("Complete habits in 2 different categories", 25),
    ("Write reflections for all completed habits", 35),
    ("Complete the habit you most often skip", 20),
    ("Earn 50 XP today", 25),
    ("Get a perfect day (all habits done)", 40),
    ("Complete a build and break habit on the same day", 30),
    ("Do your hardest habit first", 20),
    ("Complete 5 habits in one day", 35),
    ("Maintain yesterday's streak", 20),
]


def get_all(conn: sqlite3.Connection) -> list[Badge]:
    """Return all badges with earned status."""
    rows = conn.execute("SELECT * FROM badges ORDER BY id").fetchall()
    return [_row_to_badge(r) for r in rows]


def get_earned(conn: sqlite3.Connection) -> list[Badge]:
    """Return only earned badges."""
    rows = conn.execute(
        "SELECT * FROM badges WHERE earned_at IS NOT NULL ORDER BY earned_at"
    ).fetchall()
    return [_row_to_badge(r) for r in rows]


def get_by_name(conn: sqlite3.Connection, name: str) -> Badge | None:
    """Get a badge by name."""
    row = conn.execute("SELECT * FROM badges WHERE name = ?", (name,)).fetchone()
    return _row_to_badge(row) if row else None


def earn_badge(conn: sqlite3.Connection, name: str) -> bool:
    """Award a badge if not already earned. Returns True if newly earned."""
    badge = get_by_name(conn, name)
    if badge is None or badge.earned_at is not None:
        return False
    conn.execute(
        "UPDATE badges SET earned_at = datetime('now') WHERE name = ?",
        (name,),
    )
    return True


def get_quests_today(conn: sqlite3.Connection) -> list[Quest]:
    """Get quests for today, generating them if needed."""
    today = date.today().isoformat()
    quests = _get_quests_for_date(conn, today)
    if not quests:
        _generate_quests(conn, today)
        quests = _get_quests_for_date(conn, today)
    return quests


def complete_quest(conn: sqlite3.Connection, quest_id: int) -> None:
    """Mark a quest as completed."""
    conn.execute(
        "UPDATE daily_quests SET completed = 1 WHERE id = ?", (quest_id,)
    )


def get_completed_quests_today(conn: sqlite3.Connection) -> list[Quest]:
    """Return today's completed quests."""
    today = date.today().isoformat()
    rows = conn.execute(
        "SELECT * FROM daily_quests WHERE date = ? AND completed = 1", (today,)
    ).fetchall()
    return [_row_to_quest(r) for r in rows]


def _get_quests_for_date(conn: sqlite3.Connection, log_date: str) -> list[Quest]:
    rows = conn.execute(
        "SELECT * FROM daily_quests WHERE date = ?", (log_date,)
    ).fetchall()
    return [_row_to_quest(r) for r in rows]


def _generate_quests(conn: sqlite3.Connection, log_date: str) -> None:
    picked = random.sample(QUEST_POOL, min(3, len(QUEST_POOL)))
    for description, xp_reward in picked:
        conn.execute(
            "INSERT INTO daily_quests (date, description, xp_reward) VALUES (?, ?, ?)",
            (log_date, description, xp_reward),
        )


def _row_to_badge(row: sqlite3.Row) -> Badge:
    return Badge(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        icon=row["icon"],
        earned_at=row["earned_at"],
    )


def _row_to_quest(row: sqlite3.Row) -> Quest:
    return Quest(
        id=row["id"],
        date=row["date"],
        description=row["description"],
        xp_reward=row["xp_reward"],
        completed=bool(row["completed"]),
    )
