"""Tests for gamification service."""

from datetime import date

from tracker.models.habit import Habit
from tracker.models.player import PlayerState
from tracker.repository.habits import create
from tracker.repository.logs import upsert
from tracker.repository.player import get_state
from tracker.services.gamification import (
    calculate_xp,
    check_boss_defeat,
    check_category_diversity,
    check_habit_stacker,
    check_perfect_day,
    process_checkin,
)


class TestCalculateXP:
    def test_base_xp(self):
        h = Habit(name="Run", xp_value=10)
        p = PlayerState()
        xp = calculate_xp(h, streak_days=0, missed_yesterday=False, player=p)
        assert xp == 10

    def test_7_day_streak(self):
        h = Habit(name="Run", xp_value=10)
        p = PlayerState()
        xp = calculate_xp(h, streak_days=7, missed_yesterday=False, player=p)
        # 10 * 1.25 = 12.5 → round() with banker's rounding → 12
        assert xp == 12

    def test_never_miss_twice(self):
        h = Habit(name="Run", xp_value=10)
        p = PlayerState()
        xp = calculate_xp(h, streak_days=0, missed_yesterday=True, player=p)
        assert xp == 20  # 10 * 2.0

    def test_boss_multiplier(self):
        h = Habit(name="Run", xp_value=10)
        p = PlayerState(permanent_xp_multiplier=1.2)
        xp = calculate_xp(h, streak_days=0, missed_yesterday=False, player=p)
        assert xp == 12  # 10 * 1.2

    def test_combined_multipliers(self):
        h = Habit(name="Run", xp_value=10)
        p = PlayerState(permanent_xp_multiplier=1.2)
        xp = calculate_xp(h, streak_days=30, missed_yesterday=True, player=p)
        assert xp == 36  # 10 * 1.5 * 2.0 * 1.2 = 36


class TestProcessCheckin:
    def test_simple_done(self, seeded_db):
        h = create(seeded_db, Habit(name="Run", xp_value=10))
        result = process_checkin(seeded_db, h.id, "done")
        assert result["status"] == "done"
        assert result["xp_earned"] > 0
        assert "First Step" in result["new_badges"]

    def test_not_done_no_xp(self, seeded_db):
        h = create(seeded_db, Habit(name="Run"))
        result = process_checkin(seeded_db, h.id, "not_done")
        assert result["xp_earned"] == 0
        assert result["new_badges"] == []

    def test_skipped_no_xp(self, seeded_db):
        h = create(seeded_db, Habit(name="Run"))
        result = process_checkin(seeded_db, h.id, "skipped")
        assert result["xp_earned"] == 0

    def test_invalid_habit_raises(self, seeded_db):
        with __import__("pytest").raises(ValueError):
            process_checkin(seeded_db, 999, "done")

    def test_xp_levels_up_player(self, seeded_db):
        h = create(seeded_db, Habit(name="Run", xp_value=400))
        process_checkin(seeded_db, h.id, "done")
        player = get_state(seeded_db)
        assert player.total_xp >= 400  # quests may add bonus XP
        assert player.level >= 3  # sqrt(400/100) + 1 = 3


class TestBossDefeat:
    def test_all_done_triggers_boss(self, seeded_db):
        h1 = create(seeded_db, Habit(name="Run"))
        h2 = create(seeded_db, Habit(name="Read"))
        upsert(seeded_db, h1.id, date.today().isoformat(), "done")
        upsert(seeded_db, h2.id, date.today().isoformat(), "done")
        badges = check_boss_defeat(seeded_db)
        assert "Boss Slayer" in badges

    def test_not_all_done_no_boss(self, seeded_db):
        h1 = create(seeded_db, Habit(name="Run"))
        h2 = create(seeded_db, Habit(name="Read"))
        upsert(seeded_db, h1.id, date.today().isoformat(), "done")
        upsert(seeded_db, h2.id, date.today().isoformat(), "not_done")
        badges = check_boss_defeat(seeded_db)
        assert badges == []

    def test_no_habits_no_boss(self, seeded_db):
        assert check_boss_defeat(seeded_db) == []


class TestCategoryDiversity:
    def test_5_habits_3_categories(self, seeded_db):
        create(seeded_db, Habit(name="Run", category="health"))
        create(seeded_db, Habit(name="Swim", category="health"))
        create(seeded_db, Habit(name="Read", category="learning"))
        create(seeded_db, Habit(name="Meditate", category="mindfulness"))
        create(seeded_db, Habit(name="Code", category="work"))
        badges = check_category_diversity(seeded_db)
        assert "Jack of All" in badges

    def test_not_enough_categories(self, seeded_db):
        create(seeded_db, Habit(name="Run", category="health"))
        create(seeded_db, Habit(name="Swim", category="health"))
        create(seeded_db, Habit(name="Bike", category="health"))
        create(seeded_db, Habit(name="Lift", category="health"))
        create(seeded_db, Habit(name="Walk", category="health"))
        badges = check_category_diversity(seeded_db)
        assert badges == []


class TestPerfectDay:
    def test_all_done_today(self, seeded_db):
        h1 = create(seeded_db, Habit(name="Run"))
        h2 = create(seeded_db, Habit(name="Read"))
        upsert(seeded_db, h1.id, date.today().isoformat(), "done")
        upsert(seeded_db, h2.id, date.today().isoformat(), "done")
        badges = check_perfect_day(seeded_db)
        assert "Perfect Day" in badges

    def test_not_all_done(self, seeded_db):
        h1 = create(seeded_db, Habit(name="Run"))
        create(seeded_db, Habit(name="Read"))
        upsert(seeded_db, h1.id, date.today().isoformat(), "done")
        badges = check_perfect_day(seeded_db)
        assert badges == []


class TestHabitStacker:
    def test_3_done_triggers(self, seeded_db):
        h1 = create(seeded_db, Habit(name="Run"))
        h2 = create(seeded_db, Habit(name="Read"))
        h3 = create(seeded_db, Habit(name="Meditate"))
        upsert(seeded_db, h1.id, date.today().isoformat(), "done")
        upsert(seeded_db, h2.id, date.today().isoformat(), "done")
        upsert(seeded_db, h3.id, date.today().isoformat(), "done")
        badges = check_habit_stacker(seeded_db)
        assert "Habit Stacker" in badges

    def test_2_done_no_trigger(self, seeded_db):
        h1 = create(seeded_db, Habit(name="Run"))
        h2 = create(seeded_db, Habit(name="Read"))
        upsert(seeded_db, h1.id, date.today().isoformat(), "done")
        upsert(seeded_db, h2.id, date.today().isoformat(), "done")
        badges = check_habit_stacker(seeded_db)
        assert badges == []
