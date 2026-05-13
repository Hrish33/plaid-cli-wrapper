# Run all:      pytest tests/unit/test_status.py -v
# Run one:      pytest tests/unit/test_status.py::test_clean_repo -v

from unittest.mock import MagicMock, call
from gitwrap.services.git.commands.status import StatusCommand


def make_service(responses: list):
    """Feed ordered responses for each run_git call."""
    service = MagicMock()
    service.run_git.side_effect = responses
    return service


def ok(stdout=""):
    return {"exit_code": 0, "stdout": stdout, "stderr": ""}


def err(stderr="fatal: error"):
    return {"exit_code": 1, "stdout": "", "stderr": stderr}



def test_clean_repo_no_unpushed():
    service = make_service([ok("main"), ok("0"), ok("0"), ok("")])
    result = StatusCommand(service).run(None)
    assert result["status"] == "ok"
    assert result["branch"] == "main"
    assert result["unpushed"] == 0
    assert result["unpulled"] == 0
    assert result["local_commits"] == []
    assert result["working_tree"]["clean"] is True


def test_no_remote_returns_null_sync():
    service = make_service([ok("feature"), err(), err(), ok("")])
    result = StatusCommand(service).run(None)
    assert result["unpushed"] is None
    assert result["unpulled"] is None


def test_local_commits_listed():
    log_out = "abc1234def5678 add feature"
    diff_out = "A\tsrc/main.py"
    service = make_service([ok("main"), ok("1"), ok("0"), ok(log_out), ok(diff_out), ok("")])
    result = StatusCommand(service).run(None)
    assert len(result["local_commits"]) == 1
    assert result["local_commits"][0]["message"] == "add feature"
    assert result["local_commits"][0]["files"][0] == {"path": "src/main.py", "state": "added"}


def test_commit_file_states_spelled_out():
    log_out = "abc1234def5678 msg"
    diff_out = "M\tsrc/main.py\nD\told.py"
    service = make_service([ok("main"), ok("1"), ok("0"), ok(log_out), ok(diff_out), ok("")])
    result = StatusCommand(service).run(None)
    files = result["local_commits"][0]["files"]
    assert files[0]["state"] == "modified"
    assert files[1]["state"] == "deleted"


def test_working_tree_dirty():
    service = make_service([ok("main"), ok("0"), ok("0"), ok(" M src/main.py\n?? newfile.txt")])
    result = StatusCommand(service).run(None)
    wt = result["working_tree"]
    assert wt["clean"] is False
    assert {"path": "src/main.py", "state": "modified"} in wt["files"]
    assert {"path": "newfile.txt", "state": "untracked"} in wt["files"]
    assert result["unstaged_files"] == ["src/main.py"]
    assert result["untracked_files"] == ["newfile.txt"]
    assert "staged_files" not in result


def test_staged_files():
    service = make_service([ok("main"), ok("0"), ok("0"), ok("M  src/app.py\nA  new.py")])
    result = StatusCommand(service).run(None)
    assert result["staged_files"] == ["src/app.py", "new.py"]
    assert "unstaged_files" not in result
    assert "untracked_files" not in result


def test_mixed_staged_and_unstaged():
    # MM = staged modified + unstaged modified
    service = make_service([ok("main"), ok("0"), ok("0"), ok("MM src/app.py")])
    result = StatusCommand(service).run(None)
    assert result["staged_files"] == ["src/app.py"]
    assert result["unstaged_files"] == ["src/app.py"]


def test_clean_repo_omits_file_lists():
    service = make_service([ok("main"), ok("0"), ok("0"), ok("")])
    result = StatusCommand(service).run(None)
    assert "staged_files" not in result
    assert "unstaged_files" not in result
    assert "untracked_files" not in result


def test_branch_error_returns_error():
    service = make_service([err("fatal: not a repo")])
    result = StatusCommand(service).run(None)
    assert result["status"] == "error"
