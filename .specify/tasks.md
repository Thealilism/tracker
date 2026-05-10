# Tracker — Implementation Tasks

## Phase 1: Foundation

### T1 — Project Scaffolding
- [ ] Create `pyproject.toml` with dependencies (click, rich, pytest, ruff, mypy)
- [ ] Create `tracker/__init__.py`
- [ ] Create `tests/__init__.py` and `tests/conftest.py` (in-memory DB fixture)
- [ ] Run `uv sync` to install deps
- [ ] Verify: `uv run pytest` passes (0 tests)

### T2 — Database Layer (`tracker/db.py`)
- [ ] Connection manager: `get_db(path)` returns sqlite3 connection with row_factory
- [ ] `init_db(conn)` — runs all CREATE TABLE statements
- [ ] `seed_badges(conn)` — inserts the 10 achievement badges
- [ ] `seed_player(conn)` — inserts default player_state row
- [ ] **Tests:** `test_db.py` — schema exists, tables have correct columns, seed data present

### T3 — Models (`tracker/models/`)
- [ ] `habit.py` — Habit dataclass with all fields
- [ ] `log.py` — DailyLog dataclass
- [ ] `player.py` — PlayerState dataclass
- [ ] `badge.py` — Badge and Quest dataclasses
- [ ] **Tests:** `test_models.py` — field defaults, type enforcement

## Phase 2: Data Access

### T4 — Habit Repository (`tracker/repository/habits.py`)
- [ ] `create(conn, habit)` — insert habit
- [ ] `get_all(conn, category=None)` — list with optional filter
- [ ] `get_by_id(conn, id)` — single habit
- [ ] `delete(conn, id)` — remove habit + cascade logs
- [ ] `update(conn, habit)` — edit habit fields
- [ ] **Tests:** `test_habit_repo.py` — CRUD + cascade delete

### T5 — Log Repository (`tracker/repository/logs.py`)
- [ ] `log_today(conn, habit_id, status)` — upsert today's log entry
- [ ] `get_today(conn, habit_id)` — today's log if exists
- [ ] `get_all_today(conn)` — all habits' logs for today
- [ ] `get_streak(conn, habit_id)` — count consecutive 'done' days from today backwards
- [ ] `get_date_range(conn, habit_id, start, end)` — logs in date range
- [ ] **Tests:** `test_log_repo.py` — upsert, streak counting with gaps, edge cases

### T6 — Player Repository (`tracker/repository/player.py`)
- [ ] `get_state(conn)` — return PlayerState (always row 1)
- [ ] `add_xp(conn, amount)` — increment total_xp, recalculate level/title
- [ ] `add_boss_defeat(conn)` — increment permanent multiplier
- [ ] `use_freeze(conn)` — decrement streak_freezes
- [ ] `replenish_freezes(conn)` — reset to 1 (called monthly)
- [ ] **Tests:** `test_player_repo.py` — XP → level progression, title changes, freeze limits

### T7 — Badge Repository (`tracker/repository/badges.py`)
- [ ] `get_all(conn)` — all badges with earned status
- [ ] `earn_badge(conn, name)` — set earned_at = now()
- [ ] `get_earned(conn)` — earned badges only
- [ ] `get_quests_today(conn, date)` — quests for date
- [ ] `generate_quests(conn, date)` — pick 3 random from pool, insert
- [ ] `complete_quest(conn, quest_id)` — mark quest done
- [ ] **Tests:** `test_badge_repo.py` — earn, list, quest generation uniqueness

## Phase 3: Business Logic

### T8 — Habit Service (`tracker/services/habit_service.py`)
- [ ] `create_habit(...)` — validate 4-law fields, set defaults, delegate to repo
- [ ] `list_habits(category)` — delegate + format hints
- [ ] `delete_habit(id)` — with confirmation guard
- [ ] `update_habit(...)` — partial update
- [ ] **Tests:** `test_habit_service.py` — validation rules, required fields, defaults

### T9 — Streak Service (`tracker/services/streak_service.py`)
- [ ] `get_streaks(conn)` — all habits with current streak + multiplier
- [ ] `apply_streak_freeze(conn, habit_id)` — use freeze if available
- [ ] `check_streak_milestones(conn)` — detect 7/30/90 day thresholds → trigger badges
- [ ] **Tests:** `test_streak_service.py` — multiplier tiers, freeze logic, milestone detection

### T10 — Gamification Service (`tracker/services/gamification.py`)
- [ ] `calculate_xp(habit, streak_days, missed_yesterday, player)` — full XP formula
- [ ] `process_checkin(conn, habit_id, status)` — XP award, level up, badge checks
- [ ] `check_badges(conn)` — evaluate all 10 badge triggers, award new ones
- [ ] `check_boss_defeat(conn)` — all habits done today → boss badge + multiplier
- [ ] `apply_never_miss_twice(conn, habit_id)` — 2x bonus check
- [ ] `level_to_title(level)` — title lookup function
- [ ] `generate_daily_quests(conn)` — if none today, generate 3
- [ ] **Tests:** `test_gamification.py` — XP math, level boundaries, badge triggers, boss logic, quest generation

## Phase 4: Display

### T11 — Display Module (`tracker/display.py`)
- [ ] `habit_table(habits)` — rich Table
- [ ] `streak_dashboard(streaks)` — table with colored multipliers
- [ ] `xp_bar(current, needed, width=30)` — rich progress bar
- [ ] `character_sheet(player, badges)` — formatted panel
- [ ] `badge_grid(badges)` — earned vs locked visual
- [ ] `checkin_prompt(habits)` — interactive selection list
- [ ] `quest_list(quests)` — today's quests with checkmarks
- [ ] `stats_panel(stats)` — completion % with columns
- [ ] **Tests:** `test_display.py` — output is valid rich renderable (no crash)

## Phase 5: CLI

### T12 — CLI Commands (`tracker/cli.py`)
- [ ] `tracker init` — db init + seed, print success
- [ ] `tracker habit create` — interactive wizard (click prompts)
- [ ] `tracker habit list [--category]` — rich table
- [ ] `tracker checkin` — interactive: show habits one by one, mark done/skip
- [ ] `tracker streak` — streak dashboard
- [ ] `tracker stats [--period 7|30|all]` — completion rates
- [ ] `tracker quests` — today's quests
- [ ] `tracker me` — character sheet
- [ ] `tracker journal [habit_name]` — read/write reflections
- [ ] `tracker stack` — show chain order
- [ ] **Tests:** `test_cli.py` — CliRunner integration tests for each command

## Phase 6: Polish

### T13 — Final Integration & QA
- [ ] Full workflow test: init → create habits → checkin 7 days → verify streak + badge
- [ ] ruff check passes
- [ ] mypy strict passes
- [ ] pytest --cov ≥ 80%
- [ ] `uv run tracker --help` shows all commands

---

**Task Dependency Graph:**
```
T1 ──→ T2 ──→ T4 ──→ T8 ──→ T12
         │     │       │
         ├──→ T5 ──→ T9 ─┤
         │     │          │
         ├──→ T6 ──→ T10 ─┤
         │     │           │
         ├──→ T7 ─────────┤
         │                 │
         └──→ T3 ─────────┤
                          │
                    T11 ──┘
                     │
                     └──→ T13
```

**Version**: 1.0.0 | **Date**: 2025-05-10
