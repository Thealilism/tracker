"""Habit service — validation and orchestration for habit operations."""

import sqlite3

from tracker.models.habit import Habit, HabitType
from tracker.repository import habits as habit_repo


def create_habit(
    conn: sqlite3.Connection,
    name: str,
    category: str = "general",
    identity_statement: str | None = None,
    cue: str | None = None,
    craving: str | None = None,
    response: str | None = None,
    reward: str | None = None,
    habit_type: HabitType = "build",
    xp_value: int = 10,
    stacking_order: int | None = None,
) -> Habit:
    """Validate and create a new habit."""
    if not name.strip():
        raise ValueError("Habit name is required")
    if xp_value < 1:
        raise ValueError("XP value must be at least 1")

    habit = Habit(
        name=name.strip(),
        category=category.strip() or "general",
        identity_statement=identity_statement,
        cue=cue,
        craving=craving,
        response=response,
        reward=reward,
        type=habit_type,
        xp_value=xp_value,
        stacking_order=stacking_order,
    )
    return habit_repo.create(conn, habit)


def list_habits(conn: sqlite3.Connection, category: str | None = None) -> list[Habit]:
    """List habits, optionally filtered by category."""
    return habit_repo.get_all(conn, category)


def get_habit(conn: sqlite3.Connection, habit_id: int) -> Habit | None:
    """Get a single habit by ID."""
    return habit_repo.get_by_id(conn, habit_id)


def update_habit(
    conn: sqlite3.Connection,
    habit_id: int,
    **kwargs,
) -> Habit:
    """Update habit fields. Only provided kwargs are changed."""
    habit = habit_repo.get_by_id(conn, habit_id)
    if habit is None:
        raise ValueError(f"Habit {habit_id} not found")

    for field, value in kwargs.items():
        if hasattr(habit, field):
            setattr(habit, field, value)

    if "xp_value" in kwargs and kwargs["xp_value"] < 1:
        raise ValueError("XP value must be at least 1")

    return habit_repo.update(conn, habit)


def delete_habit(conn: sqlite3.Connection, habit_id: int) -> None:
    """Delete a habit (cascades logs)."""
    if habit_repo.get_by_id(conn, habit_id) is None:
        raise ValueError(f"Habit {habit_id} not found")
    habit_repo.delete(conn, habit_id)
