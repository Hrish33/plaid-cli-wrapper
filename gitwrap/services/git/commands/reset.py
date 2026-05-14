from ....core.base_command import BaseCommand
from ....utils.confirm import request_confirmation


class ResetCommand(BaseCommand):
    """Reset tracked files in the working tree back to HEAD.

    Only affects files git already tracks — untracked files are untouched.
    Use CleanCommand to remove untracked files. Requires --dry-run or --force.
    """

    def __init__(self, service, prompt_fn=input):
        """Args:
            service: GitService instance.
            prompt_fn: Injectable input function for testing without stdin.
        """
        super().__init__(service)
        self.prompt_fn = prompt_fn

    def run(self, args) -> dict:
        """Route to dry-run or confirmed execution based on flags."""
        if not args.force and not args.dry_run:
            return {
                "command": "reset",
                "status": "error",
                "message": "destructive command requires --force or --dry-run",
            }

        if args.dry_run:
            return self._dry_run()

        confirmed, word, typed = request_confirmation("Reset working tree to HEAD", self.prompt_fn)
        if not confirmed:
            return {
                "command": "reset",
                "status": "aborted",
                "message": f"expected '{word.upper()}', got '{typed.upper()}' — reset cancelled",
            }

        return self._run()

    def _dry_run(self) -> dict:
        """Show which tracked files would be reverted without changing anything.

        Uses git diff HEAD to list files that differ from the last commit.
        """
        result = self.service.run_git("diff", "--name-status", "HEAD")
        if result["exit_code"] != 0:
            return {"command": "reset", "status": "error", "message": result["stderr"]}

        files = []
        for line in result["stdout"].splitlines():
            if line.strip():
                parts = line.split("\t", 1)
                files.append({"state": parts[0].strip(), "path": parts[1].strip()})

        return {
            "command": "reset",
            "status": "dry_run",
            "files": files,
            "message": f"{len(files)} file(s) would be reset to HEAD",
        }

    def _run(self) -> dict:
        """Hard-reset the working tree and index to HEAD after confirmation."""
        result = self.service.run_git("reset", "--hard", "HEAD")
        if result["exit_code"] != 0:
            return {"command": "reset", "status": "error", "message": result["stderr"]}

        return {
            "command": "reset",
            "status": "ok",
            "message": result["stdout"],
        }
