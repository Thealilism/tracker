"""Tests for daily log repository."""

from datetime import date, timedelta

from tracker.models.habit import Habit
from tracker.repository.habits import create
from tracker.repository.logs import (
    count_done_in_range,
    get_all_today,
    get_by_date,
    get_streak,
    get_today,
    upsert,
)


def test_upsert_insert(db_conn):
    h = create(db_conn, Habit(name="Run"))
    today = date.today().isoformat()
    log = upsert(db_conn, h.id, today, "done")
    assert log.status == "done"
    assert log.habit_id == h.id
    assert log.date == today


def test_upsert_update(db_conn):
    h = create(db_conn, Habit(name="Run"))
    today = date.today().isoformat()
    upsert(db_conn, h.id, today, "done")
    log = upsert(db_conn, h.id, today, "not_done", reflection="Meh")
    assert log.status == "not_done"
    assert log.reflection == "Meh"


def test_get_today_found(db_conn):
    h = create(db_conn, Habit(name="Run"))
    today = date.today().isoformat()
    upsert(db_conn, h.id, today, "done")
    log = get_today(db_conn, h.id)
    assert log is not None
    assert log.status == "done"


def test_get_today_not_found(db_conn):
    h = create(db_conn, Habit(name="Run"))
    assert get_today(db_conn, h.id) is None


def test_get_all_today(db_conn):
    h1 = create(db_conn, Habit(name="Run"))
    h2 = create(db_conn, Habit(name="Read"))
    today = date.today().isoformat()
    upsert(db_conn, h1.id, today, "done")
    upsert(db_conn, h2.id, today, "not_done")
    logs = get_all_today(db_conn)
    assert len(logs) == 2


def test_get_by_date_specific(db_conn):
    h = create(db_conn, Habit(name="Run"))
    upsert(db_conn, h.id, "2025-05-01", "done")
    log = get_by_date(db_conn, h.id, "2025-05-01")
    assert log.status == "done"


def test_streak_zero_when_no_logs(db_conn):
    h = create(db_conn, Habit(name="Run"))
    assert get_streak(db_conn, h.id) == 0


def test_streak_counting(db_conn):
    h = create(db_conn, Habit(name="Run"))
    today = date.today()
    # 5 consecutive days
    for i in range(5):
        d = (today - timedelta(days=i)).isoformat()
        upsert(db_conn, h.id, d, "done")
    assert get_streak(db_conn, h.id) == 5


def test_streak_breaks_on_gap(db_conn):
    h = create(db_conn, Habit(name="Run"))
    today = date.today()
    upsert(db_conn, h.id, today.isoformat(), "done")
    upsert(db_conn, h.id, (today - timedelta(days=2)).isoformat(), "done")
    # Gap at yesterday → streak is 1 (only today)
    assert get_streak(db_conn, h.id) == 1


def test_streak_breaks_on_not_done(db_conn):
    h = create(db_conn, Habit(name="Run"))
    today = date.today()
    upsert(db_conn, h.id, today.isoformat(), "done")
    upsert(db_conn, h.id, (today - timedelta(days=1)).isoformat(), "not_done")
    assert get_streak(db_conn, h.id) == 1


def test_count_done_in_range(db_conn):
    h = create(db_conn, Habit(name="Run"))
    upsert(db_conn, h.id, "2025-05-01", "done")
    upsert(db_conn, h.id, "2025-05-02", "done")
    upsert(db_conn, h.id, "2025-05-03", "not_done")
    count = count_done_in_range(db_conn, h.id, "2025-05-01", "2025-05-03")
    assert count == 2
