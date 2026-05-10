"""Tests for model dataclasses."""

from tracker.models.badge import Badge, Quest
from tracker.models.habit import Habit
from tracker.models.log import DailyLog
from tracker.models.player import PlayerState


class TestHabit:
    def test_defaults(self):
        h = Habit(name="Run")
        assert h.name == "Run"
        assert h.category == "general"
        assert h.type == "build"
        assert h.xp_value == 10
        assert h.id is None
        assert h.identity_statement is None
        assert h.stacking_order is None

    def test_full_fields(self):
        h = Habit(
            name="Morning Run",
            category="health",
            identity_statement="I am a runner",
            cue="After coffee",
            craving="Feel energized",
            response="Run 2km",
            reward="Check calendar",
            type="build",
            xp_value=15,
            stacking_order=1,
        )
        assert h.cue == "After coffee"
        assert h.reward == "Check calendar"
        assert h.type == "build"


class TestDailyLog:
    def test_defaults(self):
        log = DailyLog(habit_id=1, date="2025-05-10", status="done")
        assert log.habit_id == 1
        assert log.date == "2025-05-10"
        assert log.status == "done"
        assert log.reflection is None
        assert log.difficulty is None

    def test_with_reflection(self):
        log = DailyLog(
            habit_id=2,
            date="2025-05-10",
            status="done",
            reflection="Felt great!",
            difficulty=3,
        )
        assert log.reflection == "Felt great!"
        assert log.difficulty == 3


class TestPlayerState:
    def test_defaults(self):
        p = PlayerState()
        assert p.level == 1
        assert p.total_xp == 0
        assert p.streak_freezes == 1
        assert p.title == "Novice Builder"
        assert p.permanent_xp_multiplier == 1.0


class TestBadge:
    def test_earned_badge(self):
        b = Badge(name="First Step", description="Complete first habit", icon="🌟")
        assert b.earned_at is None
        assert b.icon == "🌟"


class TestQuest:
    def test_defaults(self):
        q = Quest(date="2025-05-10", description="Complete 2 health habits")
        assert q.xp_reward == 25
        assert q.completed is False
