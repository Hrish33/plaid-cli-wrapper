from .base_command import BaseCommand
from ....confirm import request_confirmation


class CommitCommand(BaseCommand):
    def __init__(self, service, prompt_fn=input):
        super().__init__(service)
        self.prompt_fn = prompt_fn

    def run(self, args) -> dict:
        if not args.message:
            return {
                "command": "commit",
                "status": "error",
                "message": "commit message required — use -m 'your message'",
            }

        if not args.force and not args.dry_run:
            return {
                "command": "commit",
                "status": "error",
                "message": "requires --force or --dry-run",
            }

        if args.dry_run:
            return self._dry_run()

        confirmed, word, typed = request_confirmation("Stage and commit all changes", self.prompt_fn)
        if not confirmed:
            return {
                "command": "commit",
                "status": "aborted",
                "message": f"expected '{word.upper()}', got '{typed.upper()}' — commit cancelled",
            }

        return self._run(args.message)

    def _dry_run(self) -> dict:
        result = self.service.run_git("status", "--porcelain")
        if result["exit_code"] != 0:
            return {"command": "commit", "status": "error", "message": result["stderr"]}

        files = [line[3:].strip() for line in result["stdout"].splitlines() if line.strip()]
        return {
            "command": "commit",
            "status": "dry_run",
            "files": files,
            "message": f"{len(files)} file(s) would be staged and committed",
        }

    def _run(self, message) -> dict:
        add_result = self.service.run_git("add", ".")
        if add_result["exit_code"] != 0:
            return {"command": "commit", "status": "error", "message": add_result["stderr"]}

        commit_result = self.service.run_git("commit", "-m", message)
        if commit_result["exit_code"] != 0:
            return {"command": "commit", "status": "error", "message": commit_result["stderr"]}

        lines = commit_result["stdout"].splitlines()
        return {
            "command": "commit",
            "status": "ok",
            "message": message,
            "output": lines[0] if lines else "",
        }
