# Run all:  pytest tests/unit/test_push.py -v
# Run one:  pytest tests/unit/test_push.py::test_correct_word_pushes -v

from unittest.mock import MagicMock, patch
from gitwrap.services.git.commands.push import PushCommand
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


def make_push(service, typed_word):
    return PushCommand(service, prompt_fn=lambda _: typed_word)


def test_correct_word_pushes():
    word = POKEMON[0]
    service = make_service(stdout="pushed")
    with patch("random.choice", return_value=word):
        result = make_push(service, word).run(make_args())
    assert result["status"] == "ok"
    service.run_git.assert_called_once_with("push")


def test_correct_word_case_insensitive():
    word = POKEMON[0]
    service = make_service(stdout="pushed")
    with patch("random.choice", return_value=word):
        result = make_push(service, word.upper()).run(make_args())
    assert result["status"] == "ok"


def test_wrong_word_aborts():
    word = POKEMON[0]
    service = make_service()
    with patch("random.choice", return_value=word):
        result = make_push(service, "wrongword").run(make_args())
    assert result["status"] == "aborted"
    service.run_git.assert_not_called()


def test_wrong_word_message_shows_expected_and_got():
    word = "spatula"
    service = make_service()
    with patch("random.choice", return_value=word):
        result = make_push(service, "nope").run(make_args())
    assert "SPATULA" in result["message"]
    assert "NOPE" in result["message"]


def test_force_push_passes_flag():
    word = POKEMON[0]
    service = make_service(stdout="pushed")
    with patch("random.choice", return_value=word):
        make_push(service, word).run(make_args(force=True))
    service.run_git.assert_called_once_with("push", "--force")


def test_dry_run_skips_confirmation():
    service = make_service(stdout="Would push")
    result = PushCommand(service).run(make_args(dry_run=True))
    assert result["status"] == "dry_run"
    service.run_git.assert_called_once_with("push", "--dry-run")


def test_git_error_propagates():
    word = POKEMON[0]
    service = make_service(exit_code=1, stderr="fatal: no remote")
    with patch("random.choice", return_value=word):
        result = make_push(service, word).run(make_args())
    assert result["status"] == "error"
    assert "fatal" in result["message"]
