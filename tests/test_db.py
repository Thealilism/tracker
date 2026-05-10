"""Tests for tracker.db — schema creation and seeding."""

from tracker.db import init, seed_badges, seed_player


def test_init_db_creates_all_tables(db_conn):
    """All 5 tables should exist after init_db."""
    tables = db_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    names = {r["name"] for r in tables} - {"sqlite_sequence"}
    assert names == {"habits", "daily_logs", "player_state", "badges", "daily_quests"}


def test_habits_table_columns(db_conn):
    """Verify habits table has all expected columns."""
    cols = db_conn.execute("PRAGMA table_info(habits)").fetchall()
    col_names = {c["name"] for c in cols}
    expected = {
        "id", "name", "category", "identity_statement",
        "cue", "craving", "response", "reward",
        "type", "xp_value", "stacking_order", "created_at",
    }
    assert col_names == expected


def test_daily_logs_has_foreign_key(db_conn):
    """daily_logs should have a foreign key to habits with CASCADE delete."""
    fks = db_conn.execute("PRAGMA foreign_key_list(daily_logs)").fetchall()
    assert len(fks) == 1
    assert fks[0]["table"] == "habits"
    assert fks[0]["on_delete"] == "CASCADE"


def test_seed_badges_inserts_10(db_conn):
    """10 badges should be seeded."""
    seed_badges(db_conn)
    count = db_conn.execute("SELECT COUNT(*) FROM badges").fetchone()[0]
    assert count == 10


def test_seed_badges_idempotent(db_conn):
    """Seeding twice should not duplicate."""
    seed_badges(db_conn)
    seed_badges(db_conn)
    count = db_conn.execute("SELECT COUNT(*) FROM badges").fetchone()[0]
    assert count == 10


def test_seed_player_creates_row(db_conn):
    """Player state row should exist after seeding."""
    seed_player(db_conn)
    row = db_conn.execute("SELECT * FROM player_state WHERE id = 1").fetchone()
    assert row is not None
    assert row["level"] == 1
    assert row["total_xp"] == 0
    assert row["title"] == "Novice Builder"


def test_seed_player_idempotent(db_conn):
    """Seeding player twice should not error."""
    seed_player(db_conn)
    seed_player(db_conn)
    count = db_conn.execute("SELECT COUNT(*) FROM player_state").fetchone()[0]
    assert count == 1


def test_init_runs_full_flow(db_conn):
    """init() should create schema and seed data."""
    init(db_conn)
    tables = db_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'"
    ).fetchall()
    assert len(tables) == 5
    assert db_conn.execute("SELECT COUNT(*) FROM badges").fetchone()[0] == 10
    assert db_conn.execute("SELECT COUNT(*) FROM player_state").fetchone()[0] == 1
