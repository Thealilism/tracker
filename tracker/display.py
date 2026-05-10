"""Rich display helpers — tables, bars, panels, prompts."""


from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from tracker.models.badge import Badge, Quest
from tracker.models.habit import Habit
from tracker.models.player import PlayerState
from tracker.services.streak_service import StreakInfo

console = Console()


def habit_table(habits: list[Habit], title: str = "Habits") -> Table:
    """Render a rich table of habits."""
    table = Table(title=title, box=box.ROUNDED)
    table.add_column("#", style="dim", width=3)
    table.add_column("Name", style="bold cyan")
    table.add_column("Category", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Identity", style="italic")
    table.add_column("XP", justify="right")

    for h in habits:
        table.add_row(
            str(h.id),
            h.name,
            h.category,
            h.type,
            h.identity_statement or "—",
            str(h.xp_value),
        )
    return table


def streak_dashboard(streaks: list[StreakInfo]) -> Table:
    """Render streak info for all habits."""
    table = Table(title="🔥 Streaks", box=box.ROUNDED)
    table.add_column("Habit", style="bold cyan")
    table.add_column("Streak", justify="right")
    table.add_column("Multiplier", justify="right", style="yellow")
    table.add_column("Freeze", justify="center")

    for s in streaks:
        mult_color = ""
        if s.multiplier >= 2.0:
            mult_color = "[bold green]"
        elif s.multiplier >= 1.5:
            mult_color = "[green]"
        elif s.multiplier >= 1.25:
            mult_color = "[yellow]"

        mult_str = f"{mult_color}{s.multiplier}x[/]" if mult_color else f"{s.multiplier}x"

        freeze_icon = "❄️" if s.can_freeze else "—"
        table.add_row(
            s.habit.name,
            f"{s.streak} days",
            mult_str,
            freeze_icon,
        )
    return table


def xp_bar(current: int, needed: int, width: int = 30) -> str:
    """Render an XP progress bar string."""
    ratio = min(current / needed, 1.0) if needed > 0 else 1.0
    filled = int(ratio * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {current}/{needed} XP"


def character_sheet(player: PlayerState, badges: list[Badge]) -> Panel:
    """Render the full character sheet."""
    # Calculate XP needed for next level
    xp_for_current = 100 * ((player.level - 1) ** 2)
    xp_for_next = 100 * (player.level ** 2)
    current_level_xp = player.total_xp - xp_for_current
    needed = xp_for_next - xp_for_current

    earned = [b for b in badges if b.earned_at is not None]
    locked = [b for b in badges if b.earned_at is None]

    content = Group(
        Text(f"\n  🏷️  {player.title}", style="bold magenta"),
        Text(f"  📊 Level {player.level}"),
        Text(f"  {xp_bar(current_level_xp, needed)}"),
        Text(f"  ❄️  Freezes: {player.streak_freezes}"),
        Text(f"  ⚡ Boss multiplier: {player.permanent_xp_multiplier}x"),
        Text(""),
        Text(f"  🏅 Badges Earned: {len(earned)}/10", style="bold yellow"),
        Text(f"     {'  '.join(b.icon or '?' for b in earned) if earned else '     None yet'}"),
        Text(f"  🔒 Locked: {', '.join(b.name for b in locked[:5])}{'...' if len(locked) > 5 else ''}"),
    )
    return Panel(content, title="⚔️  Character Sheet", border_style="magenta")


def quest_list(quests: list[Quest]) -> Table:
    """Render today's daily quests."""
    table = Table(title="📋 Daily Quests", box=box.ROUNDED)
    table.add_column("Status", width=4, justify="center")
    table.add_column("Quest", style="bold")
    table.add_column("XP", justify="right", style="yellow")

    for q in quests:
        icon = "✅" if q.completed else "⬜"
        desc = Text(q.description, style="dim" if q.completed else "")
        table.add_row(icon, desc, str(q.xp_reward))
    return table


def stats_panel(completion_7d: float, completion_30d: float, completion_all: float) -> Panel:
    """Render completion rate stats."""
    content = Group(
        Text(f"\n  7-day:  {_rate_bar(completion_7d)}"),
        Text(f"  30-day: {_rate_bar(completion_30d)}"),
        Text(f"  All-time: {_rate_bar(completion_all)}"),
    )
    return Panel(content, title="📈 Progress", border_style="blue")


def _rate_bar(rate: float) -> str:
    """Mini bar for completion rate."""
    pct = int(rate * 100)
    filled = pct // 10
    bar = "█" * filled + "░" * (10 - filled)
    return f"{bar} {pct}%"


def journal_entries(habit_name: str, entries: list[tuple[str, str, str | None, int | None]]) -> Panel:
    """Render reflection journal entries."""
    lines = [Text("")]
    for date_str, status, reflection, difficulty in entries[-10:]:  # last 10
        diff_str = f" (difficulty: {difficulty}/5)" if difficulty else ""
        lines.append(Text(f"  {date_str} [{status}]{diff_str}"))
        if reflection:
            lines.append(Text(f"    💬 {reflection}", style="italic dim"))
    return Panel(Group(*lines), title=f"📓 {habit_name} Journal", border_style="green")


def confirm(message: str) -> bool:
    """Ask yes/no confirmation."""
    return console.input(f"{message} [y/N] ").strip().lower() == "y"


def prompt_text(message: str, default: str = "") -> str:
    """Prompt for text input."""
    result = console.input(f"{message} [{default}]: ").strip()
    return result if result else default


def prompt_int(message: str, default: int = 0) -> int:
    """Prompt for integer input."""
    raw = console.input(f"{message} [{default}]: ").strip()
    return int(raw) if raw else default


def success(message: str) -> None:
    console.print(f"  ✅ {message}", style="green")


def error(message: str) -> None:
    console.print(f"  ❌ {message}", style="red")


def info(message: str) -> None:
    console.print(f"  ℹ️  {message}", style="dim")


def level_up(old_title: str, new_title: str, new_level: int) -> None:
    console.print(f"\n  🎉 LEVEL UP! {old_title} → [bold magenta]{new_title}[/] (Level {new_level})")
