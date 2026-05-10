# 🎯 Tracker

**Atomic Habits gamified habit tracker.** Build better habits using the 4 Laws of Behavior Change, powered by XP, levels, badges, and daily quests.

---

## Quick Start

```bash
# Install
cd ~/projects/tracker
uv sync --dev

# Initialize database
uv run tracker init

# Create your first habit (interactive wizard)
uv run tracker habit create

# Daily check-in (mark habits done/skipped)
uv run tracker checkin

# View your progress
uv run tracker me
```

---

## How It Works

Tracker is built on James Clear's **Atomic Habits** framework. Every habit has:

| Law | Field | Meaning |
|-----|-------|---------|
| 1. Make it Obvious | **Cue** | When/where trigger |
| 2. Make it Attractive | **Craving** | The motivating want |
| 3. Make it Easy | **Response** | The action itself |
| 4. Make it Satisfying | **Reward** | Immediate payoff |

### Gamification

| System | How it works |
|--------|-------------|
| **XP & Levels** | Earn XP for completing habits. Level up = new title |
| **Streak Multipliers** | 7-day → 1.25x XP, 30-day → 1.5x, 90-day → 2x |
| **Badges** | 10 achievements auto-awarded on milestones |
| **Daily Quests** | 3 random challenges per day for bonus XP |
| **Boss Battles** | Complete ALL habits in a day → permanent XP boost |
| **Never Miss Twice** | Miss yesterday? Get 2x XP today for bouncing back |

### Level Titles

| Level | Title |
|-------|-------|
| 1–4 | Novice Builder |
| 5–9 | Habit Squire |
| 10–19 | Discipline Knight |
| 20–34 | Atomic Master |
| 35+ | Identity Forged |

### Badges

| Badge | How to Earn |
|-------|------------|
| 🌟 First Step | Complete your first habit |
| 🔥 Week Warrior | 7-day streak on any habit |
| 💪 Iron Will | 30-day streak |
| ⚛️ Atomic | 90-day streak |
| 🔄 Identity Shift | Reach level 10 |
| 🎯 Jack of All | 5 habits across 3+ categories |
| ✨ Perfect Day | All habits done in a day |
| 🦘 Bounce Back | Complete after missing yesterday |
| ⛓️ Habit Stacker | Chain 3+ habits in one day |
| 👑 Boss Slayer | Defeat a boss (all habits done) |

---

## All Commands

| Command | Description |
|---------|-------------|
| `tracker init` | Create database + seed badges |
| `tracker habit create` | Interactive habit builder (name, category, 4 laws, XP) |
| `tracker habit list` | Table of all habits, filter with `--category` |
| `tracker habit delete <id>` | Delete a habit (cascades logs) |
| `tracker checkin` | Daily check-in loop — mark each habit done/skipped/not-done |
| `tracker streak` | Streak dashboard with multipliers and freeze status |
| `tracker stats [--period 7\|30\|all]` | Completion rate stats |
| `tracker me` | Character sheet — level, XP bar, title, badge collection |
| `tracker quests` | Today's 3 daily quests with completion status |
| `tracker journal [habit]` | View reflections for a habit (last 30 days) |
| `tracker stack` | View your habit stacking chain order |

---

## Example Session

```bash
$ uv run tracker init
✅ Tracker initialized!

$ uv run tracker habit create
✨ Create a New Habit

Name []: Morning Run
Category []: health
Identity statement (I am...) []: I am a runner

The 4 Laws of Behavior Change:
  1. Cue (when/where) []: After coffee
  2. Craving (the want) []: Feel energized
  3. Response (the action) []: Run 2km
  4. Reward (immediate satisfaction) []: Check calendar

Type (build/break) []: build
XP value [10]: 15
✅ Habit 'Morning Run' created! (ID: 1)

$ uv run tracker checkin
📋 Daily Check-in — 2026-05-10

Morning Run
   I am a runner
  [d]one / [s]kipped / [n]ot done []: d
  Reflection (optional) []: Felt amazing!
  Difficulty 1-5 (optional) []: 3
  ✅ Done! +15 XP

🏅 New Badges Earned:
  ✅ First Step

$ uv run tracker me
╭──────────────────── ⚔️  Character Sheet ────────────────────╮
│                                                              │
│   🏷️  Novice Builder                                         │
│   📊 Level 1                                                 │
│   [██████████████████████████████░░] 88/100 XP               │
│   ❄️  Freezes: 1                                             │
│   ⚡ Boss multiplier: 1.0x                                   │
│                                                              │
│   🏅 Badges Earned: 5/10                                     │
│      🌟  🔥  ✨  ⛓️  👑                                      │
│   🔒 Locked: Iron Will, Atomic, Identity Shift, ...          │
╰──────────────────────────────────────────────────────────────╯
```

---

## Tech Stack

| Layer | Choice |
|-------|--------|
| Language | Python 3.11+ |
| Database | SQLite (single-file, zero setup) |
| CLI | Click |
| Display | Rich (tables, panels, progress bars) |
| Package | uv |
| Tests | pytest (110 tests, ≥80% coverage) |
| Linting | ruff + mypy (strict) |

---

## Development

```bash
# Run all tests
uv run pytest

# With coverage
uv run pytest --cov=tracker --cov-report=term

# Lint
uv run ruff check .

# Type check
uv run mypy tracker/

# Reset database
rm ~/tracker.db && uv run tracker init
```

---

## Project Status

- [x] Habit CRUD with 4-law framework
- [x] Daily check-in with reflections
- [x] Streak tracking with multipliers
- [x] XP system with level progression
- [x] 10 achievement badges
- [x] Daily quests (3 random per day)
- [x] Boss battle system
- [x] Character sheet (`tracker me`)
- [x] Statistics dashboard
- [x] Habit stacking
- [x] Journal / reflections
- [ ] Web dashboard (future)
- [ ] Habit templates/presets (future)
- [ ] Data export/import (future)

---

Built with [GitHub Spec-Kit](https://github.com/github/spec-kit) · Spec-driven development
