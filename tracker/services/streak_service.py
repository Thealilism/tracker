"""Streak service — streak counting, multipliers, and freeze logic."""

import sqlite3
from dataclasses import dataclass

from tracker.models.habit import Habit
from tracker.repository import logs as log_repo
from tracker.repository import player as player_repo


@dataclass
class StreakInfo:
    habit: Habit
    streak: int
    multiplier: float
    can_freeze: bool


def get_all_streaks(conn: sqlite3.Connection) -> list[StreakInfo]:
    """Get streak info for all habits."""
    from tracker.repository import habits as habit_repo
    player = player_repo.get_state(conn)
    habits = habit_repo.get_all(conn)

    result = []
    for habit in habits:
        streak = log_repo.get_streak(conn, habit.id)
        multiplier = _streak_multiplier(streak)
        result.append(StreakInfo(
            habit=habit,
            streak=streak,
            multiplier=multiplier,
            can_freeze=player.streak_freezes > 0,
        ))
    return result


def get_habit_streak(conn: sqlite3.Connection, habit_id: int) -> StreakInfo | None:
    """Get streak info for a single habit."""
    from tracker.repository import habits as habit_repo
    habit = habit_repo.get_by_id(conn, habit_id)
    if habit is None:
        return None

    player = player_repo.get_state(conn)
    streak = log_repo.get_streak(conn, habit_id)
    return StreakInfo(
        habit=habit,
        streak=streak,
        multiplier=_streak_multiplier(streak),
        can_freeze=player.streak_freezes > 0,
    )


def apply_streak_freeze(conn: sqlite3.Connection, habit_id: int) -> bool:
    """Use a freeze to protect this habit's streak. Returns True if successful."""
    return player_repo.use_freeze(conn)


def check_streak_milestones(conn: sqlite3.Connection, habit_id: int) -> list[str]:
    """Check if a habit hit a milestone and award badges. Returns new badge names."""
    from tracker.repository import badges as badge_repo

    streak = log_repo.get_streak(conn, habit_id)
    new_badges = []

    milestones = [
        (7, "Week Warrior"),
        (30, "Iron Will"),
        (90, "Atomic"),
    ]
    for days, badge_name in milestones:
        if streak >= days:
            if badge_repo.earn_badge(conn, badge_name):
                new_badges.append(badge_name)

    return new_badges


def _streak_multiplier(days: int) -> float:
    if days >= 90:
        return 2.0
    if days >= 30:
        return 1.5
    if days >= 7:
        return 1.25
    return 1.0
