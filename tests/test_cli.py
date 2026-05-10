"""Integration tests for CLI commands."""

import pytest
from click.testing import CliRunner

from tracker.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def cli_with_db(runner, tmp_path):
    """CliRunner that uses a temp database."""
    import sqlite3

    import tracker.cli as cli_mod

    db_path = str(tmp_path / "test_tracker.db")

    # Patch get_db to return our temp DB
    original_get_db = cli_mod.get_db

    def _get_db(path=None):
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    cli_mod.get_db = _get_db

    # Init the DB
    result = runner.invoke(cli, ["init"])
    assert result.exit_code == 0

    yield runner

    cli_mod.get_db = original_get_db


def test_init(cli_with_db):
    result = cli_with_db.invoke(cli, ["init"])
    assert result.exit_code == 0
    assert "initialized" in result.output.lower()


def test_habit_create_and_list(cli_with_db):
    # Create a habit via interactive prompts
    result = cli_with_db.invoke(cli, ["habit", "create"], input=(
        "Run\nhealth\nI am a runner\n\n\n\n\nbuild\n10\n"
    ))
    assert result.exit_code == 0
    assert "Run" in result.output

    # List habits
    result = cli_with_db.invoke(cli, ["habit", "list"])
    assert result.exit_code == 0
    assert "Run" in result.output
    assert "health" in result.output


def test_habit_list_empty(cli_with_db):
    result = cli_with_db.invoke(cli, ["habit", "list"])
    assert result.exit_code == 0
    assert "No habits" in result.output


def test_checkin_no_habits(cli_with_db):
    result = cli_with_db.invoke(cli, ["checkin"])
    assert result.exit_code == 0
    assert "No habits" in result.output


def test_full_checkin_flow(cli_with_db):
    # Create a habit
    cli_with_db.invoke(cli, ["habit", "create"], input=(
        "Meditate\nmindfulness\nI am calm\n\n\n\n\nbuild\n10\n"
    ))

    # Do checkin - mark as done
    result = cli_with_db.invoke(cli, ["checkin"], input="d\n\n3\n")
    assert result.exit_code == 0
    assert "XP" in result.output


def test_streak_empty(cli_with_db):
    result = cli_with_db.invoke(cli, ["streak"])
    assert result.exit_code == 0


def test_stats(cli_with_db):
    # Create a habit first
    cli_with_db.invoke(cli, ["habit", "create"], input=(
        "Read\nlearning\nI am a reader\n\n\n\n\nbuild\n10\n"
    ))
    result = cli_with_db.invoke(cli, ["stats"])
    assert result.exit_code == 0
    assert "Read" in result.output


def test_me(cli_with_db):
    result = cli_with_db.invoke(cli, ["me"])
    assert result.exit_code == 0
    assert "Character Sheet" in result.output or "Novice Builder" in result.output


def test_quests(cli_with_db):
    result = cli_with_db.invoke(cli, ["quests"])
    assert result.exit_code == 0
    assert "Quests" in result.output


def test_help(cli_with_db):
    result = cli_with_db.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "checkin" in result.output
    assert "habit" in result.output
    assert "streak" in result.output
    assert "me" in result.output


def test_habit_crud(cli_with_db):
    # Create
    cli_with_db.invoke(cli, ["habit", "create"], input=(
        "Jog\nfitness\n\n\n\n\n\nbuild\n15\n"
    ))
    # List
    result = cli_with_db.invoke(cli, ["habit", "list"])
    assert "Jog" in result.output

    # Delete (say yes)
    result = cli_with_db.invoke(cli, ["habit", "delete", "1"], input="y\n")
    assert result.exit_code == 0

    # Verify gone
    result = cli_with_db.invoke(cli, ["habit", "list"])
    assert "No habits" in result.output
