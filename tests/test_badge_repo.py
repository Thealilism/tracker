"""Tests for badge and quest repository."""

from datetime import date

from tracker.repository.badges import (
    complete_quest,
    earn_badge,
    get_all,
    get_by_name,
    get_completed_quests_today,
    get_earned,
    get_quests_today,
)


class TestBadges:
    def test_get_all_returns_10(self, seeded_db):
        badges = get_all(seeded_db)
        assert len(badges) == 10

    def test_all_unearned_initially(self, seeded_db):
        badges = get_all(seeded_db)
        assert all(b.earned_at is None for b in badges)

    def test_get_earned_empty_initially(self, seeded_db):
        assert get_earned(seeded_db) == []

    def test_earn_badge(self, seeded_db):
        result = earn_badge(seeded_db, "First Step")
        assert result is True
        badge = get_by_name(seeded_db, "First Step")
        assert badge.earned_at is not None

    def test_earn_badge_idempotent(self, seeded_db):
        earn_badge(seeded_db, "First Step")
        result = earn_badge(seeded_db, "First Step")
        assert result is False

    def test_earn_badge_unknown_name(self, seeded_db):
        result = earn_badge(seeded_db, "NopeBadge")
        assert result is False

    def test_earned_appears_in_get_earned(self, seeded_db):
        earn_badge(seeded_db, "First Step")
        earned = get_earned(seeded_db)
        assert len(earned) == 1
        assert earned[0].name == "First Step"


class TestQuests:
    def test_generates_quests_on_first_call(self, seeded_db):
        quests = get_quests_today(seeded_db)
        assert len(quests) == 3
        assert all(q.date == date.today().isoformat() for q in quests)
        assert all(not q.completed for q in quests)

    def test_idempotent_if_already_generated(self, seeded_db):
        first = get_quests_today(seeded_db)
        second = get_quests_today(seeded_db)
        assert [q.id for q in first] == [q.id for q in second]

    def test_complete_quest(self, seeded_db):
        quests = get_quests_today(seeded_db)
        complete_quest(seeded_db, quests[0].id)
        completed = get_completed_quests_today(seeded_db)
        assert len(completed) == 1
        assert completed[0].id == quests[0].id
