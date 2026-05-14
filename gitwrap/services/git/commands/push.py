from ....core.base_command import BaseCommand
from ....utils.confirm import request_confirmation


class PushCommand(BaseCommand):
    """Push local commits to the remote repository.

    Unlike other destructive commands, push always requires a Pokemon
    confirmation — there is no --force-only gate, because any push to a
    shared remote is consequential. --dry-run skips the prompt and simulates
    the push without sending anything.
    """

    def __init__(self, service, prompt_fn=input):
        """Args:
            service: GitService instance.
            prompt_fn: Injectable input function for testing without stdin.
        """
        super().__init__(service)
        self.prompt_fn = prompt_fn

    def run(self, args) -> dict:
        """Route to dry-run or confirmed push based on flags."""
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
            # git writes push output to stderr even on success, so fall back to it
            "message": result["stdout"] or result["stderr"],
        }

    def _dry_run(self) -> dict:
        """Simulate a push without sending any data to the remote."""
        result = self.service.run_git("push", "--dry-run")
        if result["exit_code"] != 0:
            return {"command": "push", "status": "error", "message": result["stderr"]}

        return {
            "command": "push",
            "status": "dry_run",
            "message": result["stdout"] or result["stderr"],
        }
