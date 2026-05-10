"""Database connection, schema creation, and seeding."""

import sqlite3
from pathlib import Path

DEFAULT_DB_NAME = "tracker.db"


def get_db(path: str | None = None) -> sqlite3.Connection:
    """Open a connection to the tracker database. Creates file if missing."""
    db_path = path or str(Path.home() / DEFAULT_DB_NAME)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Create all tables if they don't exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'general',
            identity_statement TEXT,
            cue TEXT,
            craving TEXT,
            response TEXT,
            reward TEXT,
            type TEXT NOT NULL CHECK(type IN ('build', 'break')) DEFAULT 'build',
            xp_value INTEGER NOT NULL DEFAULT 10,
            stacking_order INTEGER,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS daily_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
            date TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('done', 'not_done', 'skipped')),
            reflection TEXT,
            difficulty INTEGER CHECK(difficulty BETWEEN 1 AND 5),
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(habit_id, date)
        );

        CREATE TABLE IF NOT EXISTS player_state (
            id INTEGER PRIMARY KEY CHECK(id = 1),
            level INTEGER NOT NULL DEFAULT 1,
            total_xp INTEGER NOT NULL DEFAULT 0,
            streak_freezes INTEGER NOT NULL DEFAULT 1,
            title TEXT NOT NULL DEFAULT 'Novice Builder',
            permanent_xp_multiplier REAL NOT NULL DEFAULT 1.0
        );

        CREATE TABLE IF NOT EXISTS badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL,
            icon TEXT,
            earned_at TEXT
        );

        CREATE TABLE IF NOT EXISTS daily_quests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            xp_reward INTEGER NOT NULL DEFAULT 25,
            completed INTEGER NOT NULL DEFAULT 0
        );
    """)


def seed_badges(conn: sqlite3.Connection) -> None:
    """Insert the 10 achievement badges if not already present."""
    badges = [
        ("First Step", "Complete your first habit", "🌟"),
        ("Week Warrior", "7-day streak on any habit", "🔥"),
        ("Iron Will", "30-day streak", "💪"),
        ("Atomic", "90-day streak", "⚛️"),
        ("Identity Shift", "Reach level 10", "🔄"),
        ("Jack of All", "5 habits across 3+ categories", "🎯"),
        ("Perfect Day", "All habits done in a day", "✨"),
        ("Bounce Back", "Complete after a miss (never miss twice)", "🦘"),
        ("Habit Stacker", "Chain 3+ habits in one day", "⛓️"),
        ("Boss Slayer", "Defeat a boss (all habits done)", "👑"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO badges (name, description, icon) VALUES (?, ?, ?)",
        badges,
    )


def seed_player(conn: sqlite3.Connection) -> None:
    """Insert default player state if not already present."""
    conn.execute(
        "INSERT OR IGNORE INTO player_state (id) VALUES (1)"
    )


def init(conn: sqlite3.Connection) -> None:
    """Full initialization: schema + seed data."""
    init_db(conn)
    seed_badges(conn)
    seed_player(conn)
    conn.commit()
