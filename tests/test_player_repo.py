"""Tests for player repository."""

from tracker.repository.player import (
    add_boss_defeat,
    add_xp,
    get_state,
    level_to_title,
    replenish_freezes,
    use_freeze,
    xp_to_level,
)


def test_get_state_defaults(seeded_db):
    state = get_state(seeded_db)
    assert state.level == 1
    assert state.total_xp == 0
    assert state.streak_freezes == 1
    assert state.title == "Novice Builder"
    assert state.permanent_xp_multiplier == 1.0


def test_add_xp_levels_up(seeded_db):
    # Level 2 requires 100 XP: sqrt(100/100)+1 = 2
    state = add_xp(seeded_db, 100)
    assert state.level == 2
    assert state.total_xp == 100


def test_add_xp_multiple_levels(seeded_db):
    # Level 5 requires 1600 XP: sqrt(1600/100)+1 = 5
    state = add_xp(seeded_db, 1600)
    assert state.level == 5


def test_add_xp_updates_title(seeded_db):
    state = add_xp(seeded_db, 1600)  # level 5
    assert state.title == "Habit Squire"


def test_add_boss_defeat(seeded_db):
    add_boss_defeat(seeded_db)
    state = get_state(seeded_db)
    assert state.permanent_xp_multiplier == 1.1
    add_boss_defeat(seeded_db)
    state = get_state(seeded_db)
    assert state.permanent_xp_multiplier == 1.2


def test_use_freeze_success(seeded_db):
    assert use_freeze(seeded_db) is True
    state = get_state(seeded_db)
    assert state.streak_freezes == 0


def test_use_freeze_fails_when_empty(seeded_db):
    use_freeze(seeded_db)  # 1→0
    assert use_freeze(seeded_db) is False
    state = get_state(seeded_db)
    assert state.streak_freezes == 0


def test_replenish_freezes(seeded_db):
    use_freeze(seeded_db)
    replenish_freezes(seeded_db)
    state = get_state(seeded_db)
    assert state.streak_freezes == 1


def test_xp_to_level():
    assert xp_to_level(0) == 1
    assert xp_to_level(100) == 2
    assert xp_to_level(900) == 4
    assert xp_to_level(1600) == 5
    assert xp_to_level(8100) == 10


def test_level_to_title():
    assert level_to_title(1) == "Novice Builder"
    assert level_to_title(5) == "Habit Squire"
    assert level_to_title(10) == "Discipline Knight"
    assert level_to_title(20) == "Atomic Master"
    assert level_to_title(35) == "Identity Forged"
