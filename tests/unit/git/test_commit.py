# Run all:  pytest tests/unit/test_commit.py -v
# Run one:  pytest tests/unit/test_commit.py::test_no_message_returns_error -v

from unittest.mock import MagicMock, call, patch
from gitwrap.services.git.commands.commit import CommitCommand
from gitwrap.utils.confirm import POKEMON


def make_service(stdout="", exit_code=0, stderr=""):
    service = MagicMock()
    service.run_git.return_value = {"exit_code": exit_code, "stdout": stdout, "stderr": stderr}
    return service


def make_args(message=None, dry_run=False, force=False, yes=False):
    args = MagicMock()
    args.message = message
    args.dry_run = dry_run
    args.force = force
    args.yes = yes
    return args


def make_commit(service, typed_word):
    return CommitCommand(service, prompt_fn=lambda _: typed_word)


def test_no_message_returns_error():
    result = CommitCommand(make_service()).run(make_args())
    assert result["status"] == "error"
    assert "-m" in result["message"]


def test_no_flags_returns_error():
    result = CommitCommand(make_service()).run(make_args(message="msg"))
    assert result["status"] == "error"
    assert "requires" in result["message"]


def test_correct_word_runs_add_then_commit_and_returns_ok():
    word = POKEMON[0]
    service = make_service(stdout="[main abc1234] my message")
    with patch("random.choice", return_value=word):
        result = make_commit(service, word).run(make_args(message="my message", force=True))
    assert service.run_git.call_args_list == [
        call("add", "."),
        call("commit", "-m", "my message"),
    ]
    assert result["status"] == "ok"
    assert result["message"] == "my message"
    assert "abc1234" in result["output"]


def test_wrong_word_aborts():
    word = POKEMON[0]
    service = make_service()
    with patch("random.choice", return_value=word):
        result = make_commit(service, "wrong").run(make_args(message="msg", force=True))
    assert result["status"] == "aborted"
    service.run_git.assert_not_called()


def test_add_failure_propagates():
    word = POKEMON[0]
    service = MagicMock()
    service.run_git.return_value = {"exit_code": 1, "stdout": "", "stderr": "fatal: add failed"}
    with patch("random.choice", return_value=word):
        result = make_commit(service, word).run(make_args(message="msg", force=True))
    assert result["status"] == "error"
    assert "add failed" in result["message"]


def test_dry_run_requires_message():
    result = CommitCommand(make_service()).run(make_args(dry_run=True))
    assert result["status"] == "error"
    assert "-m" in result["message"]


def test_dry_run_shows_all_changed_files():
    stdout = " M src/main.py\n?? newfile.txt"
    result = CommitCommand(make_service(stdout=stdout)).run(make_args(message="msg", dry_run=True))
    assert result["status"] == "dry_run"
    assert "src/main.py" in result["files"]
    assert "newfile.txt" in result["files"]


def test_dry_run_nothing_to_commit():
    result = CommitCommand(make_service(stdout="")).run(make_args(message="msg", dry_run=True))
    assert result["files"] == []


def test_git_error_propagates():
    word = POKEMON[0]
    service = make_service(exit_code=1, stderr="nothing to commit")
    with patch("random.choice", return_value=word):
        result = make_commit(service, word).run(make_args(message="msg", force=True))
    assert result["status"] == "error"
