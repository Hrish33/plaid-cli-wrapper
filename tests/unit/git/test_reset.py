# Run all:  pytest tests/unit/test_reset.py -v
# Run one:  pytest tests/unit/test_reset.py::test_no_flags_returns_error -v

from unittest.mock import MagicMock, patch
from gitwrap.services.git.commands.reset import ResetCommand
from gitwrap.utils.confirm import POKEMON


def make_service(stdout="", exit_code=0, stderr=""):
    service = MagicMock()
    service.run_git.return_value = {"exit_code": exit_code, "stdout": stdout, "stderr": stderr}
    return service


def make_args(force=False, dry_run=False, yes=False):
    args = MagicMock()
    args.force = force
    args.dry_run = dry_run
    args.yes = yes
    return args


def make_reset(service, typed_word):
    return ResetCommand(service, prompt_fn=lambda _: typed_word)


def test_no_flags_returns_error():
    result = ResetCommand(make_service()).run(make_args())
    assert result["status"] == "error"
    assert "requires" in result["message"]


def test_dry_run_calls_diff():
    service = make_service(stdout="")
    ResetCommand(service).run(make_args(dry_run=True))
    service.run_git.assert_called_once_with("diff", "--name-status", "HEAD")


def test_dry_run_parses_files():
    stdout = "M\tsrc/main.py\nD\told.txt"
    result = ResetCommand(make_service(stdout=stdout)).run(make_args(dry_run=True))
    assert result["status"] == "dry_run"
    assert result["files"] == [{"state": "M", "path": "src/main.py"}, {"state": "D", "path": "old.txt"}]


def test_dry_run_clean_repo():
    result = ResetCommand(make_service(stdout="")).run(make_args(dry_run=True))
    assert result["status"] == "dry_run"
    assert result["files"] == []


def test_correct_word_resets_and_returns_ok():
    word = POKEMON[0]
    service = make_service(stdout="HEAD is now at abc1234 msg")
    with patch("random.choice", return_value=word):
        result = make_reset(service, word).run(make_args(force=True))
    service.run_git.assert_called_once_with("reset", "--hard", "HEAD")
    assert result["status"] == "ok"


def test_wrong_word_aborts():
    word = POKEMON[0]
    service = make_service()
    with patch("random.choice", return_value=word):
        result = make_reset(service, "wrong").run(make_args(force=True))
    assert result["status"] == "aborted"
    service.run_git.assert_not_called()


def test_git_error_propagates():
    word = POKEMON[0]
    service = make_service(exit_code=1, stderr="fatal: error")
    with patch("random.choice", return_value=word):
        result = make_reset(service, word).run(make_args(force=True))
    assert result["status"] == "error"
