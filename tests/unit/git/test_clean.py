# Run all:  pytest tests/unit/test_clean.py -v
# Run one:  pytest tests/unit/test_clean.py::test_no_flags_returns_error -v

from unittest.mock import MagicMock, patch
from gitwrap.services.git.commands.clean import CleanCommand
from gitwrap.confirm import POKEMON


def make_service(stdout="", exit_code=0, stderr=""):
    service = MagicMock()
    service.run_git.return_value = {"exit_code": exit_code, "stdout": stdout, "stderr": stderr}
    return service


def make_args(force=False, dry_run=False):
    args = MagicMock()
    args.force = force
    args.dry_run = dry_run
    return args


def make_clean(service, typed_word):
    return CleanCommand(service, prompt_fn=lambda _: typed_word)


def test_no_flags_returns_error():
    result = CleanCommand(make_service()).run(make_args())
    assert result["status"] == "error"
    assert "requires" in result["message"]


def test_dry_run_calls_nfd():
    service = make_service(stdout="Would remove foo.txt")
    CleanCommand(service).run(make_args(dry_run=True))
    service.run_git.assert_called_once_with("clean", "-nfd")


def test_dry_run_parses_files():
    stdout = "Would remove foo.txt\nWould remove bar/"
    result = CleanCommand(make_service(stdout=stdout)).run(make_args(dry_run=True))
    assert result["status"] == "dry_run"
    assert result["files"] == ["foo.txt", "bar/"]


def test_dry_run_empty():
    result = CleanCommand(make_service(stdout="")).run(make_args(dry_run=True))
    assert result["status"] == "dry_run"
    assert result["files"] == []


def test_correct_word_cleans_and_returns_ok():
    word = POKEMON[0]
    stdout = "Removing foo.txt\nRemoving bar/"
    service = make_service(stdout=stdout)
    with patch("random.choice", return_value=word):
        result = make_clean(service, word).run(make_args(force=True))
    service.run_git.assert_called_once_with("clean", "-fd")
    assert result["status"] == "ok"
    assert result["files"] == ["foo.txt", "bar/"]


def test_wrong_word_aborts():
    word = POKEMON[0]
    service = make_service()
    with patch("random.choice", return_value=word):
        result = make_clean(service, "wrong").run(make_args(force=True))
    assert result["status"] == "aborted"
    service.run_git.assert_not_called()


def test_git_error_propagates():
    word = POKEMON[0]
    service = make_service(exit_code=1, stderr="fatal: error")
    with patch("random.choice", return_value=word):
        result = make_clean(service, word).run(make_args(force=True))
    assert result["status"] == "error"
