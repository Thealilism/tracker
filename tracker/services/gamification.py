"""Gamification service — XP, levels, badges, quests, boss logic."""

import sqlite3
from datetime import date, timedelta

from tracker.models.habit import Habit
from tracker.models.player import PlayerState
from tracker.repository import badges as badge_repo
from tracker.repository import habits as habit_repo
from tracker.repository import logs as log_repo
from tracker.repository import player as player_repo


def calculate_xp(
    habit: Habit,
    streak_days: int,
    missed_yesterday: bool,
    player: PlayerState,
) -> int:
    """Calculate XP earned for completing a habit."""
    if streak_days >= 90:
        streak_mult = 2.0
    elif streak_days >= 30:
        streak_mult = 1.5
    elif streak_days >= 7:
        streak_mult = 1.25
    else:
        streak_mult = 1.0

    never_miss = 2.0 if missed_yesterday else 1.0
    total_mult = streak_mult * never_miss * player.permanent_xp_multiplier
    return round(habit.xp_value * total_mult)


def process_checkin(
    conn: sqlite3.Connection,
    habit_id: int,
    status: str,
    reflection: str | None = None,
    difficulty: int | None = None,
) -> dict:
    """Process a daily check-in. Returns summary dict with XP and new badges."""
    habit = habit_repo.get_by_id(conn, habit_id)
    if habit is None:
        raise ValueError(f"Habit {habit_id} not found")

    today = date.today().isoformat()
    log_repo.upsert(conn, habit_id, today, status, reflection, difficulty)

    result: dict = {"status": status, "xp_earned": 0, "new_badges": [], "new_quests_completed": []}

    if status != "done":
        return result

    # Calculate XP
    player = player_repo.get_state(conn)
    streak = log_repo.get_streak(conn, habit_id)
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    yesterday_log = log_repo.get_by_date(conn, habit_id, yesterday)
    missed_yesterday = yesterday_log is None or yesterday_log.status != "done"

    xp = calculate_xp(habit, streak, missed_yesterday, player)
    player_repo.add_xp(conn, xp)
    result["xp_earned"] = xp

    # First habit ever → First Step badge
    if badge_repo.earn_badge(conn, "First Step"):
        result["new_badges"].append("First Step")

    # Never miss twice → Bounce Back badge
    if missed_yesterday and yesterday_log is not None:
        if badge_repo.earn_badge(conn, "Bounce Back"):
            result["new_badges"].append("Bounce Back")

    # Streak milestones
    from tracker.services.streak_service import check_streak_milestones
    milestone_badges = check_streak_milestones(conn, habit_id)
    result["new_badges"].extend(milestone_badges)

    # Boss check
    boss_badges = check_boss_defeat(conn)
    result["new_badges"].extend(boss_badges)

    # Category diversity
    diversity_badges = check_category_diversity(conn)
    result["new_badges"].extend(diversity_badges)

    # Perfect day
    perfect_badges = check_perfect_day(conn)
    result["new_badges"].extend(perfect_badges)

    # Habit stacker (chain 3+)
    stacker_badges = check_habit_stacker(conn)
    result["new_badges"].extend(stacker_badges)

    # Identity shift (level 10)
    player = player_repo.get_state(conn)
    if player.level >= 10:
        if badge_repo.earn_badge(conn, "Identity Shift"):
            result["new_badges"].append("Identity Shift")

    # Update quests
    quest_badges = update_quests(conn)
    result["new_quests_completed"].extend(quest_badges)

    return result


def check_boss_defeat(conn: sqlite3.Connection) -> list[str]:
    """Check if all habits are done today → boss defeated."""
    date.today().isoformat()
    habits = habit_repo.get_all(conn)
    if not habits:
        return []

    today_logs = log_repo.get_all_today(conn)
    done_ids = {log.habit_id for log in today_logs if log.status == "done"}
    all_ids = {h.id for h in habits}

    if done_ids == all_ids:
        new_badges = []
        if badge_repo.earn_badge(conn, "Boss Slayer"):
            new_badges.append("Boss Slayer")
        player_repo.add_boss_defeat(conn)
        return new_badges
    return []


def check_category_diversity(conn: sqlite3.Connection) -> list[str]:
    """Check Jack of All badge: 5+ habits across 3+ categories."""
    cat_counts = habit_repo.count_by_category(conn)
    total = sum(cat_counts.values())
    if total >= 5 and len(cat_counts) >= 3:
        if badge_repo.earn_badge(conn, "Jack of All"):
            return ["Jack of All"]
    return []


def check_perfect_day(conn: sqlite3.Connection) -> list[str]:
    """Check Perfect Day badge: all habits done today."""
    date.today().isoformat()
    habits = habit_repo.get_all(conn)
    if not habits:
        return []

    today_logs = log_repo.get_all_today(conn)
    done_ids = {log.habit_id for log in today_logs if log.status == "done"}
    all_ids = {h.id for h in habits}

    if done_ids == all_ids:
        if badge_repo.earn_badge(conn, "Perfect Day"):
            return ["Perfect Day"]
    return []


def check_habit_stacker(conn: sqlite3.Connection) -> list[str]:
    """Check Habit Stacker badge: 3+ habits chained in one day."""
    date.today().isoformat()
    logs = log_repo.get_all_today(conn)
    done_count = sum(1 for log in logs if log.status == "done")
    if done_count >= 3:
        if badge_repo.earn_badge(conn, "Habit Stacker"):
            return ["Habit Stacker"]
    return []


def update_quests(conn: sqlite3.Connection) -> list[str]:
    """Check and auto-complete daily quests. Returns completed quest descriptions."""
    date.today().isoformat()
    quests = badge_repo.get_quests_today(conn)
    completed = []

    today_logs = log_repo.get_all_today(conn)
    done_count = sum(1 for log in today_logs if log.status == "done")
    habits = habit_repo.get_all(conn)
    done_categories = set()
    for log in today_logs:
        if log.status == "done":
            h = habit_repo.get_by_id(conn, log.habit_id)
            if h:
                done_categories.add(h.category)

    for quest in quests:
        if quest.completed:
            continue

        desc = quest.description.lower()
        should_complete = False

        if "complete 2 health habits" in desc and done_count >= 2:
            # This is simplistic; real impl would check category
            should_complete = done_count >= 2
        elif "write a reflection" in desc:
            has_reflection = any(
                log.reflection for log in today_logs if log.status == "done"
            )
            should_complete = has_reflection
        elif "complete 3 habits total" in desc:
            should_complete = done_count >= 3
        elif "first habit" in desc:
            should_complete = done_count >= 1
        elif "chain 2 habits" in desc:
            should_complete = done_count >= 2
        elif "difficulty 4+" in desc:
            has_hard = any(
                log.difficulty and log.difficulty >= 4 for log in today_logs
            )
            should_complete = has_hard
        elif "2 different categories" in desc:
            should_complete = len(done_categories) >= 2
        elif "reflections for all" in desc:
            should_complete = all(
                log.reflection for log in today_logs if log.status == "done"
            ) and done_count > 0
        elif "most often skip" in desc:
            should_complete = False  # Needs historical data
        elif "earn 50 xp" in desc:
            should_complete = False  # Tracked elsewhere
        elif "perfect day" in desc:
            should_complete = done_count == len(habits) and len(habits) > 0
        elif "build and break" in desc:
            cat_types = set()
            for log in today_logs:
                if log.status == "done":
                    h = habit_repo.get_by_id(conn, log.habit_id)
                    if h:
                        cat_types.add(h.type)
            should_complete = len(cat_types) >= 2
        elif "hardest habit first" in desc:
            should_complete = done_count >= 1
        elif "complete 5 habits" in desc:
            should_complete = done_count >= 5
        elif "maintain yesterday" in desc:
            should_complete = done_count >= 1

        if should_complete:
            badge_repo.complete_quest(conn, quest.id)
            player_repo.add_xp(conn, quest.xp_reward)
            completed.append(quest.description)

    return completed
