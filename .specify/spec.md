# Tracker Specification

## Personas
- **Self-Improver** — Builds good habits and breaks bad ones using the Atomic Habits system with gamified motivation.

## Core Entities

### Habit
| Field | Type | Description |
|-------|------|-------------|
| id | int | Primary key |
| name | str | "Morning Run" |
| category | str | health, work, learning, etc. |
| identity_statement | str | "I am a runner" |
| cue | str | When/where trigger — "After I finish my coffee" |
| craving | str | The want — "Feel energized" |
| response | str | The action — "Run 2km" |
| reward | str | Immediate satisfaction — "Check off calendar" |
| type | enum | build / break |
| xp_value | int | Default 10 |
| stacking_order | int? | Position in habit chain (null = not in chain) |

### Daily Log
| Field | Type | Description |
|-------|------|-------------|
| id | int | PK |
| date | date | Log date |
| habit_id | FK | Reference to habit |
| status | enum | done / not_done / skipped |
| reflection | str? | Optional notes |
| difficulty | int? | 1-5 rating |

### Player State
| Field | Type | Description |
|-------|------|-------------|
| id | int | PK |
| level | int | Current level |
| total_xp | int | Cumulative XP |
| streak_freezes | int | Free skips remaining |
| title | str | "Novice Builder", "Habit Knight", "Atomic Master" |

### Badges
| Field | Type |
|-------|------|
| id | int |
| name | str |
| description | str |
| earned_at | timestamp? |

### Daily Quests
| Field | Type |
|-------|------|
| id | int |
| date | date |
| description | str |
| xp_reward | int |
| completed | bool |

## Gamification System

### XP & Levels
- Habits have user-configurable XP value (default: 10 XP)
- Completing a habit → earn XP
- Level up = title changes
- "Never Miss Twice" bonus: 2x XP if yesterday was missed but today is completed

### Streak Multipliers
| Streak | Multiplier |
|--------|-----------|
| 7 days | 1.25x XP |
| 30 days | 1.5x XP |
| 90 days | 2x XP |
| Streak Freeze | 1 free skip per 30 days |

### Achievements (Badges)
| Badge | Trigger |
|-------|---------|
| First Step | Complete first habit |
| Week Warrior | 7-day streak on any habit |
| Iron Will | 30-day streak |
| Atomic | 90-day streak |
| Identity Shift | Reach level 10 |
| Jack of All | 5 habits across 3+ categories |
| Perfect Day | All habits done in a day |
| Bounce Back | Complete after a miss (never miss twice) |
| Habit Stacker | Chain 3+ habits in one day |
| Boss Slayer | Defeat a boss (all habits completed in one day) |

### Daily Quests
- 3 random mini-challenges per day
- Extra XP on completion
- Reset daily

### Boss Battles
- Completing ALL habits in a single day = boss defeated
- Reward: rare badge + 0.1x permanent XP multiplier (stackable)

## Functional Requirements

| # | Feature | Details |
|---|---------|---------|
| F1 | Create habit | Name, category, identity, 4-law fields, XP value, stacking order |
| F2 | List habits | Filter by category, type |
| F3 | Daily check-in | Mark habits done/not-done/skipped for today |
| F4 | Streak view | Current streak per habit (consecutive days done) |
| F5 | Habit stacking | Chain habits: complete one → next is suggested |
| F6 | Reflection journal | Add notes per habit per day |
| F7 | Progress stats | Completion rate (7-day, 30-day, all-time) |
| F8 | Identity tracker | Identity statement + milestone celebrations |
| F9 | XP & leveling | Earn XP, level up, title progression |
| F10 | Badges | Auto-awarded on milestone triggers |
| F11 | Daily quests | 3 random challenges, XP rewards |
| F12 | Boss battles | All-habits-done detection + rewards |
| F13 | Character sheet | `tracker me` → level, XP bar, title, badges, streaks |

## Non-Functional Requirements

| # | Requirement | Target |
|---|-------------|--------|
| NF1 | Offline-only | No network calls |
| NF2 | Zero setup | `uv run tracker init` → ready |
| NF3 | DB portability | Single SQLite file |
| NF4 | CLI speed | Any command < 200ms |
| NF5 | Test coverage | ≥ 80% |

## User Stories

1. **Create habit** — Define a habit with 4-law fields and gamification settings.
2. **Daily check-in** — Mark habits done/not-done in under 5 seconds.
3. **See streaks** — View consecutive completion days per habit.
4. **Habit stacking** — Chain habits so completing one prompts the next.
5. **Progress overview** — 7-day and 30-day completion rates.
6. **Identity growth** — See identity statement and level milestones.
7. **Earn XP** — XP on completion, streak multipliers, level progression.
8. **Unlock badges** — Achievement badges on milestones.
9. **Daily quests** — 3 random challenges for bonus XP.
10. **Boss battle** — All-habits day = boss defeat + permanent multiplier.
11. **Character view** — `tracker me` shows full player state.
12. **Never miss twice** — 2x XP bonus for bouncing back after a missed day.

**Version**: 1.0.0 | **Date**: 2025-05-10
