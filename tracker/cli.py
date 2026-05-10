"""Tracker CLI — Atomic Habits gamified habit tracker."""

from datetime import date, timedelta

import click

from tracker import display
from tracker.db import get_db
from tracker.db import init as db_init
from tracker.repository import badges as badge_repo
from tracker.repository import logs as log_repo
from tracker.repository import player as player_repo
from tracker.services import gamification, habit_service, streak_service


@click.group()
@click.pass_context
def cli(ctx):
    """🎯 Tracker — Atomic Habits, gamified. Build better habits, one day at a time."""
    ctx.ensure_object(dict)
    conn = get_db()
    # Check if DB is initialized
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='habits'"
    )
    if cursor.fetchone() is None:
        # No tables — only `init` command should proceed
        if ctx.invoked_subcommand != "init":
            display.error("Database not initialized. Run: tracker init")
            conn.close()
            ctx.exit(1)
    ctx.obj["conn"] = conn


@cli.command()
def init():
    """Initialize tracker database."""
    conn = get_db()
    db_init(conn)
    conn.close()
    display.success("Tracker initialized! Start building habits with: tracker habit create")


@cli.group()
def habit():
    """Manage your habits."""


@habit.command("create")
@click.pass_context
def habit_create(ctx):
    """Create a new habit (interactive wizard)."""
    display.console.print("\n[bold]✨ Create a New Habit[/]\n")

    name = display.prompt_text("Name")
    if not name:
        display.error("Name is required")
        return

    category = display.prompt_text("Category", "general")
    identity = display.prompt_text("Identity statement (I am...)", "")
    identity = identity if identity else None

    display.console.print("\n[bold]The 4 Laws of Behavior Change:[/]")
    cue = display.prompt_text("  1. Cue (when/where)", "")
    cue = cue if cue else None
    craving = display.prompt_text("  2. Craving (the want)", "")
    craving = craving if craving else None
    response = display.prompt_text("  3. Response (the action)", "")
    response = response if response else None
    reward = display.prompt_text("  4. Reward (immediate satisfaction)", "")
    reward = reward if reward else None

    display.console.print("")
    habit_type = display.prompt_text("Type (build/break)", "build")
    xp_str = display.prompt_text("XP value", "10")
    xp_value = int(xp_str) if xp_str else 10

    try:
        h = habit_service.create_habit(
            ctx.obj["conn"],
            name=name,
            category=category,
            identity_statement=identity,
            cue=cue,
            craving=craving,
            response=response,
            reward=reward,
            habit_type=habit_type,
            xp_value=xp_value,
        )
        ctx.obj["conn"].commit()
        display.success(f"Habit '{h.name}' created! (ID: {h.id})")
    except ValueError as e:
        display.error(str(e))


@habit.command("list")
@click.option("--category", "-c", help="Filter by category")
@click.pass_context
def habit_list(ctx, category):
    """List your habits."""
    habits = habit_service.list_habits(ctx.obj["conn"], category)
    if not habits:
        display.info("No habits yet. Create one with: tracker habit create")
        return
    display.console.print(display.habit_table(habits))


@habit.command("delete")
@click.argument("habit_id", type=int)
@click.pass_context
def habit_delete(ctx, habit_id):
    """Delete a habit."""
    try:
        h = habit_service.get_habit(ctx.obj["conn"], habit_id)
        if h is None:
            display.error(f"Habit {habit_id} not found")
            return
        if display.confirm(f"Delete '{h.name}'? This cannot be undone."):
            habit_service.delete_habit(ctx.obj["conn"], habit_id)
            ctx.obj["conn"].commit()
            display.success(f"Deleted '{h.name}'")
    except ValueError as e:
        display.error(str(e))


@cli.command()
@click.pass_context
def checkin(ctx):
    """Daily habit check-in. Mark each habit done/skipped/not-done."""
    habits = habit_service.list_habits(ctx.obj["conn"])
    if not habits:
        display.info("No habits to check in. Create one with: tracker habit create")
        return

    display.console.print(f"\n[bold]📋 Daily Check-in — {date.today().isoformat()}[/]\n")

    total_xp = 0
    new_badges_all = []

    for h in habits:
        # Check if already logged today
        today_log = log_repo.get_today(ctx.obj["conn"], h.id)

        if today_log:
            display.console.print(f"  {h.name}: already [{today_log.status}] — skipping")
            continue

        display.console.print(f"[bold cyan]{h.name}[/]")
        if h.identity_statement:
            display.console.print(f"   {h.identity_statement}", style="italic dim")

        choice = display.prompt_text("  [d]one / [s]kipped / [n]ot done", "d").lower()

        status_map = {"d": "done", "s": "skipped", "n": "not_done"}
        status = status_map.get(choice, "done")

        reflection = None
        difficulty = None
        if status == "done":
            ref = display.prompt_text("  Reflection (optional)", "")
            reflection = ref if ref else None
            diff_str = display.prompt_text("  Difficulty 1-5 (optional)", "")
            difficulty = int(diff_str) if diff_str else None

        result = gamification.process_checkin(
            ctx.obj["conn"], h.id, status, reflection, difficulty
        )
        total_xp += result.get("xp_earned", 0)
        for badge in result.get("new_badges", []):
            if badge not in new_badges_all:
                new_badges_all.append(badge)

        if status == "done":
            display.success(f"Done! +{result.get('xp_earned', 0)} XP")
        else:
            display.info(f"Marked as {status}")

        display.console.print("")

    ctx.obj["conn"].commit()

    if new_badges_all:
        display.console.print("[bold yellow]🏅 New Badges Earned:[/]")
        for b in new_badges_all:
            display.success(b)

    if total_xp > 0:
        player = player_repo.get_state(ctx.obj["conn"])
        display.console.print(f"\n  ⚡ Total XP earned today: {total_xp}")
        display.console.print(f"  📊 Level {player.level} — {player.title}")


@cli.command()
@click.pass_context
def streak(ctx):
    """View your habit streaks."""
    streaks = streak_service.get_all_streaks(ctx.obj["conn"])
    if not streaks:
        display.info("No habits tracked yet.")
        return
    display.console.print(display.streak_dashboard(streaks))


@cli.command()
@click.option("--period", "-p", type=click.Choice(["7", "30", "all"]), default="7")
@click.pass_context
def stats(ctx, period):
    """View completion statistics."""
    habits = habit_service.list_habits(ctx.obj["conn"])
    if not habits:
        display.info("No habits to show stats for.")
        return

    today = date.today()
    if period == "7":
        days = 7
    elif period == "30":
        days = 30
    else:
        days = 365 * 10  # effectively all-time

    start = (today - timedelta(days=days - 1)).isoformat()
    end = today.isoformat()

    display.console.print(f"\n[bold]📈 Completion Rates ({period}d)[/]\n")

    from rich.table import Table
    table = Table(box=display.box.ROUNDED)
    table.add_column("Habit", style="bold cyan")
    table.add_column("Done", justify="right", style="green")
    table.add_column("Total", justify="right")
    table.add_column("Rate", justify="right", style="yellow")

    done_all = 0
    total_all = 0

    for h in habits:
        done = log_repo.count_done_in_range(ctx.obj["conn"], h.id, start, end)
        total = max(done, days)  # approximate — could be actual count of days tracked
        rate = done / total if total > 0 else 0
        table.add_row(h.name, str(done), str(total), f"{int(rate * 100)}%")
        done_all += done
        total_all += total

    rate_all = done_all / total_all if total_all > 0 else 0
    table.add_section()
    table.add_row("[bold]Overall[/]", str(done_all), str(total_all), f"[bold]{int(rate_all * 100)}%[/]")

    display.console.print(table)


@cli.command()
@click.pass_context
def quests(ctx):
    """View today's daily quests."""
    quest_list = badge_repo.get_quests_today(ctx.obj["conn"])
    display.console.print(display.quest_list(quest_list))


@cli.command()
@click.pass_context
def me(ctx):
    """View your character sheet."""
    player = player_repo.get_state(ctx.obj["conn"])
    badges = badge_repo.get_all(ctx.obj["conn"])
    display.console.print(display.character_sheet(player, badges))


@cli.command()
@click.argument("habit_name", required=False)
@click.pass_context
def journal(ctx, habit_name):
    """View or add reflections for a habit."""
    habits = habit_service.list_habits(ctx.obj["conn"])

    if habit_name:
        # Find habit by name (partial match)
        matches = [h for h in habits if habit_name.lower() in h.name.lower()]
        if not matches:
            display.error(f"No habit matching '{habit_name}'")
            return
        h = matches[0]
    else:
        # Interactive pick
        if not habits:
            display.info("No habits yet.")
            return
        display.console.print("\n[bold]Select a habit:[/]")
        for i, h in enumerate(habits, 1):
            display.console.print(f"  {i}. {h.name}")
        choice = display.prompt_text("Number", "1")
        idx = int(choice) - 1
        if idx < 0 or idx >= len(habits):
            display.error("Invalid choice")
            return
        h = habits[idx]

    # Show recent entries
    end = date.today().isoformat()
    start = (date.today() - timedelta(days=30)).isoformat()
    entries = log_repo.get_date_range(ctx.obj["conn"], h.id, start, end)
    entry_tuples = [(e.date, e.status, e.reflection, e.difficulty) for e in entries]
    display.console.print(display.journal_entries(h.name, entry_tuples))


@cli.command()
@click.pass_context
def stack(ctx):
    """View your habit stacking chain."""
    habits = habit_service.list_habits(ctx.obj["conn"])
    chained = sorted(
        [h for h in habits if h.stacking_order is not None],
        key=lambda h: h.stacking_order or 999,
    )

    if not chained:
        display.info("No habits in stack. Set stacking_order when creating/editing habits.")
        return

    display.console.print("\n[bold]⛓️  Habit Stack[/]\n")
    for i, h in enumerate(chained):
        arrow = "  ↓" if i < len(chained) - 1 else ""
        display.console.print(f"  {i + 1}. [bold cyan]{h.name}[/] — {h.cue or 'No cue set'}{arrow}")


if __name__ == "__main__":
    cli()
