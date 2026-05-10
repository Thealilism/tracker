"""Daily log CRUD and streak queries."""

import sqlite3
from datetime import date, timedelta

from tracker.models.log import DailyLog


def upsert(conn: sqlite3.Connection, habit_id: int, log_date: str, status: str,
           reflection: str | None = None, difficulty: int | None = None) -> DailyLog:
    """Insert or update a daily log entry."""
    conn.execute(
        """INSERT INTO daily_logs (habit_id, date, status, reflection, difficulty)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(habit_id, date)
           DO UPDATE SET status=excluded.status,
                         reflection=excluded.reflection,
                         difficulty=excluded.difficulty""",
        (habit_id, log_date, status, reflection, difficulty),
    )
    row = conn.execute(
        "SELECT * FROM daily_logs WHERE habit_id=? AND date=?",
        (habit_id, log_date),
    ).fetchone()
    return _row_to_log(row)


def get_today(conn: sqlite3.Connection, habit_id: int) -> DailyLog | None:
    """Get today's log entry for a habit."""
    today = date.today().isoformat()
    row = conn.execute(
        "SELECT * FROM daily_logs WHERE habit_id=? AND date=?",
        (habit_id, today),
    ).fetchone()
    return _row_to_log(row) if row else None


def get_all_today(conn: sqlite3.Connection) -> list[DailyLog]:
    """Get log entries for all habits for today."""
    today = date.today().isoformat()
    rows = conn.execute(
        "SELECT * FROM daily_logs WHERE date=?", (today,)
    ).fetchall()
    return [_row_to_log(r) for r in rows]


def get_by_date(conn: sqlite3.Connection, habit_id: int, log_date: str) -> DailyLog | None:
    """Get a log entry for a specific habit and date."""
    row = conn.execute(
        "SELECT * FROM daily_logs WHERE habit_id=? AND date=?",
        (habit_id, log_date),
    ).fetchone()
    return _row_to_log(row) if row else None


def get_streak(conn: sqlite3.Connection, habit_id: int) -> int:
    """Count consecutive 'done' days from today backwards."""
    today = date.today()
    streak = 0
    for i in range(365):  # safety cap
        check_date = (today - timedelta(days=i)).isoformat()
        row = conn.execute(
            "SELECT status FROM daily_logs WHERE habit_id=? AND date=?",
            (habit_id, check_date),
        ).fetchone()
        if row and row["status"] == "done":
            streak += 1
        else:
            break
    return streak


def get_date_range(conn: sqlite3.Connection, habit_id: int,
                   start: str, end: str) -> list[DailyLog]:
    """Get logs in a date range."""
    rows = conn.execute(
        "SELECT * FROM daily_logs WHERE habit_id=? AND date BETWEEN ? AND ? ORDER BY date",
        (habit_id, start, end),
    ).fetchall()
    return [_row_to_log(r) for r in rows]


def count_done_in_range(conn: sqlite3.Connection, habit_id: int,
                        start: str, end: str) -> int:
    """Count 'done' entries in a date range."""
    return conn.execute(
        "SELECT COUNT(*) FROM daily_logs WHERE habit_id=? AND date BETWEEN ? AND ? AND status='done'",
        (habit_id, start, end),
    ).fetchone()[0]


def _row_to_log(row: sqlite3.Row) -> DailyLog:
    return DailyLog(
        id=row["id"],
        habit_id=row["habit_id"],
        date=row["date"],
        status=row["status"],
        reflection=row["reflection"],
        difficulty=row["difficulty"],
        created_at=row["created_at"],
    )
