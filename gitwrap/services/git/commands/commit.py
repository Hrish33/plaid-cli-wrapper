from ....core.base_command import BaseCommand
from ....core.registry import command
from ....utils.confirm import request_confirmation


@command("commit")


class CommitCommand(BaseCommand):
    """Stage all changes and create a commit in one step.

    Runs git add . followed by git commit -m, so the user doesn't need to
    stage files manually before committing. Requires -m and either --dry-run
    or --force.
    """

    @classmethod
    def register(cls, subparsers):
        p = subparsers.add_parser("commit", help="Stage all changes and commit")
        p.add_argument("-m", dest="message", help="Commit message")
        p.add_argument("--dry-run", action="store_true", help="Show what would be committed")
        p.add_argument("--force", action="store_true", help="Actually stage and commit (with Pokemon confirmation)")
        p.add_argument("--yes", action="store_true", help="Actually stage and commit (skip prompt)")

    def __init__(self, service, prompt_fn=input):
        """Args:
            service: GitService instance.
            prompt_fn: Injectable input function for testing without stdin.
        """
        super().__init__(service)
        self.prompt_fn = prompt_fn

    def run(self, args) -> dict:
        """Validate flags, then route to dry-run or confirmed execution."""
        if not args.message:
            return {
                "command": "commit",
                "status": "error",
                "message": "commit message required — use -m 'your message'",
            }

        yes = getattr(args, "yes", False)
        if not args.force and not args.dry_run and not yes:
            return {
                "command": "commit",
                "status": "error",
                "message": "requires --force, --yes, or --dry-run",
            }

        if args.dry_run:
            return self._dry_run()

        if yes:
            return self._run(args.message)

        confirmed, word, typed = request_confirmation("Stage and commit all changes", self.prompt_fn)
        if not confirmed:
            return {
                "command": "commit",
                "status": "aborted",
                "message": f"expected '{word.upper()}', got '{typed.upper()}' — commit cancelled",
            }

        return self._run(args.message)

    def _dry_run(self) -> dict:
        """Show all files that would be staged and committed without touching the repo.

        Uses git status --porcelain to capture both tracked and untracked changes,
        mirroring what git add . would pick up.
        """
        result = self.service.run_git("status", "--porcelain")
        if result["exit_code"] != 0:
            return {"command": "commit", "status": "error", "message": result["stderr"]}

        files = []
        for line in result["stdout"].splitlines():
            if line.strip():
                files.append(line[3:].strip())
        return {
            "command": "commit",
            "status": "dry_run",
            "files": files,
            "message": f"{len(files)} file(s) would be staged and committed",
        }

    def _run(self, message) -> dict:
        """Stage everything with git add . then commit with the given message."""
        add_result = self.service.run_git("add", ".")
        if add_result["exit_code"] != 0:
            return {"command": "commit", "status": "error", "message": add_result["stderr"]}

        commit_result = self.service.run_git("commit", "-m", message)
        if commit_result["exit_code"] != 0:
            return {"command": "commit", "status": "error", "message": commit_result["stderr"]}

        lines = commit_result["stdout"].splitlines()
        if lines:
            first_line = lines[0]
        else:
            first_line = ""

        return {
            "command": "commit",
            "status": "ok",
            "message": message,
            "output": first_line,
        }
