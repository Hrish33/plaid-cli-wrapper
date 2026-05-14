from ....core.base_command import BaseCommand
from ....core.registry import command
from ....utils.confirm import request_confirmation


@command("clean")


class CleanCommand(BaseCommand):
    """Remove untracked files from the working tree.

    Requires --dry-run (preview), --yes (skip prompt, execute immediately), or
    --force (Pokemon confirmation then execute). Without one of these flags the
    command errors immediately without touching the filesystem.
    """

    @classmethod
    def register(cls, subparsers):
        p = subparsers.add_parser("clean", help="Remove untracked files")
        p.add_argument("--dry-run", action="store_true", help="Show what would be removed")
        p.add_argument("--force", action="store_true", help="Actually remove files (with Pokemon confirmation)")
        p.add_argument("--yes", action="store_true", help="Actually remove files (skip prompt)")

    def __init__(self, service, prompt_fn=input):
        """Args:
            service: GitService instance.
            prompt_fn: Injectable input function for testing without stdin.
        """
        super().__init__(service)
        self.prompt_fn = prompt_fn

    def run(self, args) -> dict:
        """Route to dry-run, prompt-skipped, or confirmed execution based on flags."""
        yes = getattr(args, "yes", False)
        if not args.force and not args.dry_run and not yes:
            return {
                "command": "clean",
                "status": "error",
                "message": "destructive command requires --force, --yes, or --dry-run",
            }

        if args.dry_run:
            return self._dry_run()

        if yes:
            return self._run()

        confirmed, word, typed = request_confirmation("Remove untracked files", self.prompt_fn)
        if not confirmed:
            return {
                "command": "clean",
                "status": "aborted",
                "message": f"expected '{word.upper()}', got '{typed.upper()}' — clean cancelled",
            }

        return self._run()

    def _dry_run(self) -> dict:
        """Show which untracked files would be removed without deleting anything.

        Uses git clean -nfd (n = dry-run, f = force, d = directories).
        """
        result = self.service.run_git("clean", "-nfd")
        if result["exit_code"] != 0:
            return {"command": "clean", "status": "error", "message": result["stderr"]}

        files = []
        for line in result["stdout"].splitlines():
            if line.startswith("Would remove "):
                files.append(line.replace("Would remove ", "", 1).strip())
        return {
            "command": "clean",
            "status": "dry_run",
            "files": files,
            "message": f"{len(files)} file(s) would be removed",
        }

    def _run(self) -> dict:
        """Delete all untracked files and directories after confirmation."""
        result = self.service.run_git("clean", "-fd")
        if result["exit_code"] != 0:
            return {"command": "clean", "status": "error", "message": result["stderr"]}

        files = []
        for line in result["stdout"].splitlines():
            if line.startswith("Removing "):
                files.append(line.replace("Removing ", "", 1).strip())
        return {
            "command": "clean",
            "status": "ok",
            "files": files,
            "message": f"{len(files)} file(s) removed",
        }
