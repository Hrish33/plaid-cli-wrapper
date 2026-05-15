import argparse
from gitwrap.services.git.commands.status import StatusCommand
from gitwrap.services.git.commands.clean import CleanCommand
from gitwrap.services.git.commands.reset import ResetCommand
from gitwrap.services.git.commands.commit import CommitCommand
from gitwrap.services.git.commands.push import PushCommand


def make_subparsers(cmd_class):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    cmd_class.register(subparsers)
    return parser


# --- status ---

def test_status_parser_no_flags():
    args = make_subparsers(StatusCommand).parse_args(["status"])
    assert args.command == "status"


# --- clean ---

def test_clean_parser_dry_run():
    args = make_subparsers(CleanCommand).parse_args(["clean", "--dry-run"])
    assert args.dry_run is True
    assert args.force is False
    assert args.yes is False


def test_clean_parser_force():
    args = make_subparsers(CleanCommand).parse_args(["clean", "--force"])
    assert args.force is True
    assert args.dry_run is False
    assert args.yes is False


def test_clean_parser_yes():
    args = make_subparsers(CleanCommand).parse_args(["clean", "--yes"])
    assert args.yes is True
    assert args.force is False
    assert args.dry_run is False


def test_clean_parser_defaults():
    args = make_subparsers(CleanCommand).parse_args(["clean"])
    assert args.dry_run is False
    assert args.force is False
    assert args.yes is False


# --- reset ---

def test_reset_parser_dry_run():
    args = make_subparsers(ResetCommand).parse_args(["reset", "--dry-run"])
    assert args.dry_run is True
    assert args.force is False
    assert args.yes is False


def test_reset_parser_force():
    args = make_subparsers(ResetCommand).parse_args(["reset", "--force"])
    assert args.force is True
    assert args.dry_run is False
    assert args.yes is False


def test_reset_parser_yes():
    args = make_subparsers(ResetCommand).parse_args(["reset", "--yes"])
    assert args.yes is True
    assert args.force is False
    assert args.dry_run is False


# --- commit ---

def test_commit_parser_message():
    args = make_subparsers(CommitCommand).parse_args(["commit", "-m", "my message"])
    assert args.message == "my message"
    assert args.dry_run is False
    assert args.force is False
    assert args.yes is False


def test_commit_parser_dry_run():
    args = make_subparsers(CommitCommand).parse_args(["commit", "-m", "msg", "--dry-run"])
    assert args.dry_run is True
    assert args.force is False


def test_commit_parser_force():
    args = make_subparsers(CommitCommand).parse_args(["commit", "-m", "msg", "--force"])
    assert args.force is True
    assert args.dry_run is False
    assert args.yes is False


def test_commit_parser_yes():
    args = make_subparsers(CommitCommand).parse_args(["commit", "-m", "msg", "--yes"])
    assert args.yes is True
    assert args.force is False
    assert args.dry_run is False


# --- push ---

def test_push_parser_defaults():
    args = make_subparsers(PushCommand).parse_args(["push"])
    assert args.dry_run is False
    assert args.force is False
    assert args.yes is False


def test_push_parser_dry_run():
    args = make_subparsers(PushCommand).parse_args(["push", "--dry-run"])
    assert args.dry_run is True
    assert args.force is False


def test_push_parser_force():
    args = make_subparsers(PushCommand).parse_args(["push", "--force"])
    assert args.force is True
    assert args.dry_run is False
    assert args.yes is False


def test_push_parser_yes():
    args = make_subparsers(PushCommand).parse_args(["push", "--yes"])
    assert args.yes is True
    assert args.force is False
    assert args.dry_run is False
