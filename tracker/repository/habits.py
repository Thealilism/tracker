"""Habit CRUD operations."""

import sqlite3

from tracker.models.habit import Habit


def create(conn: sqlite3.Connection, habit: Habit) -> Habit:
    """Insert a new habit. Returns the habit with id and created_at set."""
    cursor = conn.execute(
        """INSERT INTO habits (name, category, identity_statement, cue, craving,
           response, reward, type, xp_value, stacking_order)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            habit.name, habit.category, habit.identity_statement,
            habit.cue, habit.craving, habit.response, habit.reward,
            habit.type, habit.xp_value, habit.stacking_order,
        ),
    )
    habit.id = cursor.lastrowid
    row = conn.execute("SELECT created_at FROM habits WHERE id = ?", (habit.id,)).fetchone()
    habit.created_at = row["created_at"]
    return habit


def get_all(conn: sqlite3.Connection, category: str | None = None) -> list[Habit]:
    """List all habits, optionally filtered by category."""
    if category:
        rows = conn.execute(
            "SELECT * FROM habits WHERE category = ? ORDER BY created_at", (category,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM habits ORDER BY created_at").fetchall()
    return [_row_to_habit(r) for r in rows]


def get_by_id(conn: sqlite3.Connection, habit_id: int) -> Habit | None:
    """Get a single habit by ID."""
    row = conn.execute("SELECT * FROM habits WHERE id = ?", (habit_id,)).fetchone()
    if row is None:
        return None
    return _row_to_habit(row)


def update(conn: sqlite3.Connection, habit: Habit) -> Habit:
    """Update all mutable fields of a habit."""
    conn.execute(
        """UPDATE habits SET name=?, category=?, identity_statement=?, cue=?,
           craving=?, response=?, reward=?, type=?, xp_value=?, stacking_order=?
           WHERE id=?""",
        (
            habit.name, habit.category, habit.identity_statement,
            habit.cue, habit.craving, habit.response, habit.reward,
            habit.type, habit.xp_value, habit.stacking_order, habit.id,
        ),
    )
    return habit


def delete(conn: sqlite3.Connection, habit_id: int) -> None:
    """Delete a habit. CASCADE deletes associated daily_logs."""
    conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))


def count(conn: sqlite3.Connection) -> int:
    """Return total number of habits."""
    return conn.execute("SELECT COUNT(*) FROM habits").fetchone()[0]


def count_by_category(conn: sqlite3.Connection) -> dict[str, int]:
    """Return category → habit count mapping."""
    rows = conn.execute(
        "SELECT category, COUNT(*) as cnt FROM habits GROUP BY category"
    ).fetchall()
    return {r["category"]: r["cnt"] for r in rows}


def _row_to_habit(row: sqlite3.Row) -> Habit:
    return Habit(
        id=row["id"],
        name=row["name"],
        category=row["category"],
        identity_statement=row["identity_statement"],
        cue=row["cue"],
        craving=row["craving"],
        response=row["response"],
        reward=row["reward"],
        type=row["type"],
        xp_value=row["xp_value"],
        stacking_order=row["stacking_order"],
        created_at=row["created_at"],
    )
