"""Tests for habit service."""

import pytest

from tracker.repository.habits import count
from tracker.services.habit_service import (
    create_habit,
    delete_habit,
    list_habits,
    update_habit,
)


class TestCreateHabit:
    def test_creates_with_minimal_fields(self, db_conn):
        h = create_habit(db_conn, name="Run")
        assert h.id == 1
        assert h.name == "Run"
        assert h.category == "general"
        assert h.xp_value == 10
        assert h.type == "build"

    def test_strips_name_whitespace(self, db_conn):
        h = create_habit(db_conn, name="  Run  ")
        assert h.name == "Run"

    def test_raises_on_empty_name(self, db_conn):
        with pytest.raises(ValueError, match="name is required"):
            create_habit(db_conn, name="")

    def test_raises_on_xp_below_1(self, db_conn):
        with pytest.raises(ValueError, match="XP value"):
            create_habit(db_conn, name="Run", xp_value=0)

    def test_creates_with_all_fields(self, db_conn):
        h = create_habit(
            db_conn,
            name="Morning Run",
            category="health",
            identity_statement="I am a runner",
            cue="After coffee",
            craving="Feel energized",
            response="Run 2km",
            reward="Check calendar",
            habit_type="build",
            xp_value=15,
            stacking_order=1,
        )
        assert h.identity_statement == "I am a runner"
        assert h.cue == "After coffee"
        assert h.stacking_order == 1
        assert h.xp_value == 15


class TestListHabits:
    def test_returns_all(self, db_conn):
        create_habit(db_conn, "Run")
        create_habit(db_conn, "Read")
        habits = list_habits(db_conn)
        assert len(habits) == 2

    def test_filters_by_category(self, db_conn):
        create_habit(db_conn, "Run", category="health")
        create_habit(db_conn, "Read", category="learning")
        habits = list_habits(db_conn, category="health")
        assert len(habits) == 1
        assert habits[0].name == "Run"


class TestUpdateHabit:
    def test_updates_single_field(self, db_conn):
        h = create_habit(db_conn, "Run")
        updated = update_habit(db_conn, h.id, name="Jog")
        assert updated.name == "Jog"

    def test_updates_multiple_fields(self, db_conn):
        h = create_habit(db_conn, "Run", xp_value=10)
        updated = update_habit(db_conn, h.id, name="Sprint", xp_value=20)
        assert updated.name == "Sprint"
        assert updated.xp_value == 20

    def test_raises_on_missing_habit(self, db_conn):
        with pytest.raises(ValueError, match="not found"):
            update_habit(db_conn, 999, name="X")

    def test_raises_on_invalid_xp(self, db_conn):
        h = create_habit(db_conn, "Run")
        with pytest.raises(ValueError, match="XP value"):
            update_habit(db_conn, h.id, xp_value=0)


class TestDeleteHabit:
    def test_deletes_existing(self, db_conn):
        h = create_habit(db_conn, "Run")
        delete_habit(db_conn, h.id)
        assert count(db_conn) == 0

    def test_raises_on_missing(self, db_conn):
        with pytest.raises(ValueError, match="not found"):
            delete_habit(db_conn, 999)
