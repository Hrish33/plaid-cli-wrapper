from .base_command import BaseCommand
from ....confirm import request_confirmation


class PushCommand(BaseCommand):
    def __init__(self, service, prompt_fn=input):
        super().__init__(service)
        self.prompt_fn = prompt_fn

    def run(self, args) -> dict:
        if args.dry_run:
            return self._dry_run()

        confirmed, word, typed = request_confirmation("Push to remote", self.prompt_fn)
        if not confirmed:
            return {
                "command": "push",
                "status": "aborted",
                "message": f"expected '{word.upper()}', got '{typed.upper()}' — push cancelled",
            }

        git_args = ["push"]
        if args.force:
            git_args.append("--force")

        result = self.service.run_git(*git_args)
        if result["exit_code"] != 0:
            return {"command": "push", "status": "error", "message": result["stderr"]}

        return {
            "command": "push",
            "status": "ok",
            "message": result["stdout"] or result["stderr"],
        }

    def _dry_run(self) -> dict:
        result = self.service.run_git("push", "--dry-run")
        if result["exit_code"] != 0:
            return {"command": "push", "status": "error", "message": result["stderr"]}

        return {
            "command": "push",
            "status": "dry_run",
            "message": result["stdout"] or result["stderr"],
        }
