from .base_command import BaseCommand
from ....confirm import request_confirmation


class CleanCommand(BaseCommand):
    def __init__(self, service, prompt_fn=input):
        super().__init__(service)
        self.prompt_fn = prompt_fn

    def run(self, args) -> dict:
        if not args.force and not args.dry_run:
            return {
                "command": "clean",
                "status": "error",
                "message": "destructive command requires --force or --dry-run",
            }

        if args.dry_run:
            return self._dry_run()

        confirmed, word, typed = request_confirmation("Remove untracked files", self.prompt_fn)
        if not confirmed:
            return {
                "command": "clean",
                "status": "aborted",
                "message": f"expected '{word.upper()}', got '{typed.upper()}' — clean cancelled",
            }

        return self._run()

    def _dry_run(self) -> dict:
        result = self.service.run_git("clean", "-nfd")
        if result["exit_code"] != 0:
            return {"command": "clean", "status": "error", "message": result["stderr"]}

        files = [
            line.removeprefix("Would remove ").strip()
            for line in result["stdout"].splitlines()
            if line.startswith("Would remove")
        ]
        return {
            "command": "clean",
            "status": "dry_run",
            "files": files,
            "message": f"{len(files)} file(s) would be removed",
        }

    def _run(self) -> dict:
        result = self.service.run_git("clean", "-fd")
        if result["exit_code"] != 0:
            return {"command": "clean", "status": "error", "message": result["stderr"]}

        files = [
            line.removeprefix("Removing ").strip()
            for line in result["stdout"].splitlines()
            if line.startswith("Removing")
        ]
        return {
            "command": "clean",
            "status": "ok",
            "files": files,
            "message": f"{len(files)} file(s) removed",
        }
