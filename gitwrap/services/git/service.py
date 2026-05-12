from ..base_service import BaseService


class GitService(BaseService):
    """Service wrapper for the git CLI.

    All git commands run through run_git(), which pins the working
    directory to repo_path so commands behave consistently regardless
    of the shell's cwd at invocation time.
    """

    def __init__(self, repo_path="."):
        """Args:
            repo_path: Path to the git repository root. Defaults to cwd.
        """
        self.repo_path = repo_path

    def run_git(self, *args) -> dict:
        """Run a git subcommand inside the repo.

        Args:
            *args: Git subcommand and flags, e.g. ("status", "--porcelain").

        Returns:
            Dict with exit_code, stdout, stderr.
        """
        return self.run("git", *args, cwd=self.repo_path)

    def is_repo(self) -> bool:
        """Return True if repo_path is inside a git working tree."""
        result = self.run("git", "rev-parse", "--is-inside-work-tree", cwd=self.repo_path)
        return result["exit_code"] == 0
