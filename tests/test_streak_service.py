"""Tests for streak service."""

from datetime import date, timedelta

from tracker.models.habit import Habit
from tracker.repository.habits import create
from tracker.repository.logs import upsert
from tracker.services.streak_service import (
    _streak_multiplier,
    apply_streak_freeze,
    check_streak_milestones,
    get_all_streaks,
)


class TestStreakMultiplier:
    def test_no_streak(self):
        assert _streak_multiplier(0) == 1.0
        assert _streak_multiplier(3) == 1.0

    def test_7_day(self):
        assert _streak_multiplier(7) == 1.25

    def test_30_day(self):
        assert _streak_multiplier(30) == 1.5

    def test_90_day(self):
        assert _streak_multiplier(90) == 2.0


class TestGetAllStreaks:
    def test_empty(self, seeded_db):
        assert get_all_streaks(seeded_db) == []

    def test_returns_streak_info(self, seeded_db):
        h = create(seeded_db, Habit(name="Run"))
        today = date.today().isoformat()
        upsert(seeded_db, h.id, today, "done")
        streaks = get_all_streaks(seeded_db)
        assert len(streaks) == 1
        assert streaks[0].streak == 1
        assert streaks[0].multiplier == 1.0
        assert streaks[0].can_freeze is True


class TestFreeze:
    def test_uses_freeze(self, seeded_db):
        assert apply_streak_freeze(seeded_db, 1) is True

    def test_fails_when_empty(self, seeded_db):
        apply_streak_freeze(seeded_db, 1)
        assert apply_streak_freeze(seeded_db, 1) is False


class TestMilestones:
    def test_no_milestone_at_3_days(self, seeded_db):
        h = create(seeded_db, Habit(name="Run"))
        today = date.today()
        for i in range(3):
            upsert(seeded_db, h.id, (today - timedelta(days=i)).isoformat(), "done")
        badges = check_streak_milestones(seeded_db, h.id)
        assert badges == []

    def test_7_day_milestone(self, seeded_db):
        h = create(seeded_db, Habit(name="Run"))
        today = date.today()
        for i in range(7):
            upsert(seeded_db, h.id, (today - timedelta(days=i)).isoformat(), "done")
        badges = check_streak_milestones(seeded_db, h.id)
        assert "Week Warrior" in badges

    def test_multiple_milestones(self, seeded_db):
        h = create(seeded_db, Habit(name="Run"))
        today = date.today()
        for i in range(30):
            upsert(seeded_db, h.id, (today - timedelta(days=i)).isoformat(), "done")
        badges = check_streak_milestones(seeded_db, h.id)
        assert "Week Warrior" in badges
        assert "Iron Will" in badges
