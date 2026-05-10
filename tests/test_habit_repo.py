"""Tests for habit repository."""

from tracker.models.habit import Habit
from tracker.repository.habits import (
    count,
    count_by_category,
    create,
    delete,
    get_all,
    get_by_id,
    update,
)


def test_create_habit(db_conn):
    h = Habit(name="Run", category="health")
    result = create(db_conn, h)
    assert result.id == 1
    assert result.created_at is not None
    assert result.name == "Run"


def test_get_all_empty(db_conn):
    assert get_all(db_conn) == []


def test_get_all_with_data(db_conn):
    create(db_conn, Habit(name="Run", category="health"))
    create(db_conn, Habit(name="Read", category="learning"))
    habits = get_all(db_conn)
    assert len(habits) == 2
    assert habits[0].name == "Run"


def test_get_all_filtered(db_conn):
    create(db_conn, Habit(name="Run", category="health"))
    create(db_conn, Habit(name="Read", category="learning"))
    habits = get_all(db_conn, category="health")
    assert len(habits) == 1
    assert habits[0].name == "Run"


def test_get_by_id_found(db_conn):
    create(db_conn, Habit(name="Run"))
    h = get_by_id(db_conn, 1)
    assert h is not None
    assert h.name == "Run"


def test_get_by_id_not_found(db_conn):
    assert get_by_id(db_conn, 999) is None


def test_update_habit(db_conn):
    h = create(db_conn, Habit(name="Run", category="health"))
    h.name = "Jog"
    h.category = "fitness"
    update(db_conn, h)
    fetched = get_by_id(db_conn, h.id)
    assert fetched.name == "Jog"
    assert fetched.category == "fitness"


def test_delete_habit(db_conn):
    h = create(db_conn, Habit(name="Run"))
    assert count(db_conn) == 1
    delete(db_conn, h.id)
    assert count(db_conn) == 0


def test_delete_cascades_logs(db_conn):
    h = create(db_conn, Habit(name="Run"))
    db_conn.execute(
        "INSERT INTO daily_logs (habit_id, date, status) VALUES (?, ?, ?)",
        (h.id, "2025-05-10", "done"),
    )
    delete(db_conn, h.id)
    log_count = db_conn.execute("SELECT COUNT(*) FROM daily_logs").fetchone()[0]
    assert log_count == 0


def test_count_by_category(db_conn):
    create(db_conn, Habit(name="Run", category="health"))
    create(db_conn, Habit(name="Swim", category="health"))
    create(db_conn, Habit(name="Read", category="learning"))
    cat_counts = count_by_category(db_conn)
    assert cat_counts == {"health": 2, "learning": 1}
