# Tracker Implementation Plan

## Tech Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Language | Python 3.11+ | Constitution requirement |
| Database | sqlite3 (stdlib) | Zero-dependency, single-file, portable |
| CLI | click | Nested commands, clean UX, battle-tested |
| Display | rich | Tables, colors, progress bars, XP bar rendering |
| ORM | None | Raw SQL + repository pattern (YAGNI) |
| Testing | pytest + pytest-cov | Constitution (≥80% coverage) |
| Linting | ruff + mypy (strict) | Constitution |
| Package mgr | uv | Constitution |

## Project Structure

```
tracker/
├── tracker/
│   ├── __init__.py
│   ├── cli.py              # Click command group + all subcommands
│   ├── db.py               # Connection manager, schema creation, migration runner
│   ├── models/
│   │   ├── __init__.py
│   │   ├── habit.py        # Habit dataclass
│   │   ├── log.py          # DailyLog dataclass
│   │   ├── player.py       # PlayerState dataclass
│   │   └── badge.py        # Badge dataclass + Quest dataclass
│   ├── repository/
│   │   ├── __init__.py
│   │   ├── habits.py       # Habit CRUD
│   │   ├── logs.py         # DailyLog CRUD + streak queries
│   │   ├── player.py       # PlayerState CRUD
│   │   └── badges.py       # Badge CRUD + quest CRUD
│   ├── services/
│   │   ├── __init__.py
│   │   ├── habit_service.py    # Habit creation, listing, validation
│   │   ├── gamification.py     # XP calc, leveling, badge triggers, quests, boss logic
│   │   └── streak_service.py   # Streak counting, multipliers, freeze logic
│   └── display.py             # Rich formatters: tables, XP bars, badge grid, character sheet
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Fixtures: in-memory DB, seeded data
│   ├── test_habit_service.py
│   ├── test_gamification.py
│   ├── test_streak_service.py
│   └── test_cli.py             # Integration tests via CliRunner
├── pyproject.toml
└── .specify/
```

## Database Schema

```sql
CREATE TABLE habits (
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

CREATE TABLE daily_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL REFERENCES habits(id),
    date TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('done', 'not_done', 'skipped')),
    reflection TEXT,
    difficulty INTEGER CHECK(difficulty BETWEEN 1 AND 5),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(habit_id, date)
);

CREATE TABLE player_state (
    id INTEGER PRIMARY KEY CHECK(id = 1),
    level INTEGER NOT NULL DEFAULT 1,
    total_xp INTEGER NOT NULL DEFAULT 0,
    streak_freezes INTEGER NOT NULL DEFAULT 1,
    title TEXT NOT NULL DEFAULT 'Novice Builder',
    permanent_xp_multiplier REAL NOT NULL DEFAULT 1.0
);

CREATE TABLE badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    icon TEXT,
    earned_at TEXT
);

CREATE TABLE daily_quests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    description TEXT NOT NULL,
    xp_reward INTEGER NOT NULL DEFAULT 25,
    completed INTEGER NOT NULL DEFAULT 0
);
```

## CLI Command Tree

```
tracker
├── init                    Create DB + seed badges/default quests
├── habit
│   ├── create              Interactive habit builder wizard
│   └── list [--category]   Table of habits
├── checkin                 Interactive daily check-in loop
├── streak                  Streak dashboard (table: habit, streak, multiplier)
├── stats [--period]        7d / 30d / all-time completion rates
├── quests                  Today's 3 quests + completion status
├── me                      Character sheet (level, XP bar, title, badges)
├── journal [habit]         Read/write reflections for a habit
└── stack                   Show/manage habit stacking chain
```

## Gamification Logic (Service Layer)

### XP Calculation
```
Base XP = habit.xp_value
Streak multiplier = 1.0 | 1.25 (7d) | 1.5 (30d) | 2.0 (90d)
Never-miss-twice bonus = 2.0 if yesterday status == 'not_done'
Boss multiplier = 1.0 + (0.1 × player.bosses_defeated)
Total = Base × streak × never_miss × boss
```

### Level Formula
`level = floor(sqrt(total_xp / 100)) + 1`

### Title Progression
| Level | Title |
|-------|-------|
| 1-4 | Novice Builder |
| 5-9 | Habit Squire |
| 10-19 | Discipline Knight |
| 20-34 | Atomic Master |
| 35+ | Identity Forged |

### Badge Trigger Checks (run after every check-in)
- Check streaks against badge thresholds
- Check total habits across categories
- Check all-habits-done for boss defeat
- Check never-miss-twice for bounce-back

### Daily Quests (generated on `tracker checkin` or `tracker quests`)
- Pool of 20+ quest templates, pick 3 random per day
- Examples: "Complete 2 health habits", "Write a reflection", "Chain 3 habits"

## Key Dependencies (pyproject.toml)

```toml
[project]
name = "tracker"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "click>=8.0",
    "rich>=13.0",
]

[project.scripts]
tracker = "tracker.cli:cli"

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.4",
    "mypy>=1.0",
]
```

**Version**: 1.0.0 | **Date**: 2025-05-10
