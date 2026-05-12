from ..base_service import BaseService


class GitService(BaseService):
    def __init__(self, repo_path="."):
        self.repo_path = repo_path

    def run_git(self, *args) -> dict:
        return self.run("git", *args, cwd=self.repo_path)

    def is_repo(self) -> bool:
        result = self.run("git", "rev-parse", "--is-inside-work-tree", cwd=self.repo_path)
        return result["exit_code"] == 0
