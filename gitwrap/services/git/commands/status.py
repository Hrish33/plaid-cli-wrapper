from .base_command import BaseCommand

# Maps git's single-character porcelain state codes to human-readable strings.
STATE_MAP = {
    "A": "added",
    "M": "modified",
    "D": "deleted",
    "R": "renamed",
    "C": "copied",
    "U": "unmerged",
    "?": "untracked",
}


def _map_state(raw: str) -> str:
    """Convert a raw git state code to a readable string.

    Falls back to lowercasing the raw value for unknown codes.
    """
    return STATE_MAP.get(raw[0], raw.lower())


class StatusCommand(BaseCommand):
    """Show a full snapshot of the repo: branch, unpushed commits, and working tree state.

    Combines output from several git commands into a single YAML-friendly dict
    so callers get everything they need in one shot.
    """

    def run(self, args) -> dict:
        """Build and return the full status snapshot."""
        branch = self._branch()
        if isinstance(branch, dict):
            return branch  # propagate error from _branch()

        unpushed, unpulled = self._sync_counts()
        local_commits = self._local_commits(unpushed)
        working_tree = self._working_tree()

        return {
            "command": "status",
            "status": "ok",
            "branch": branch,
            "unpushed": unpushed,
            "unpulled": unpulled,
            "local_commits": local_commits,
            "working_tree": working_tree,
        }

    def _branch(self):
        """Return the current branch name, or an error dict on failure."""
        result = self.service.run_git("branch", "--show-current")
        if result["exit_code"] != 0:
            return {"command": "status", "status": "error", "message": result["stderr"]}
        return result["stdout"]

    def _sync_counts(self):
        """Return (unpushed, unpulled) commit counts relative to the remote tracking branch.

        Returns None for either value if no remote tracking branch is configured,
        e.g. a brand new local branch that has never been pushed.
        """
        ahead = self.service.run_git("rev-list", "--count", "@{u}..HEAD")
        behind = self.service.run_git("rev-list", "--count", "HEAD..@{u}")
        unpushed = int(ahead["stdout"]) if ahead["exit_code"] == 0 else None
        unpulled = int(behind["stdout"]) if behind["exit_code"] == 0 else None
        return unpushed, unpulled

    def _local_commits(self, unpushed):
        """Return a list of unpushed commits, each with hash, message, and files changed."""
        if not unpushed or unpushed == 0:
            return []

        log = self.service.run_git("log", f"-{unpushed}", "--format=%H %s")
        if log["exit_code"] != 0 or not log["stdout"]:
            return []

        commits = []
        for line in log["stdout"].splitlines():
            hash_, _, message = line.partition(" ")
            files = self._commit_files(hash_)
            commits.append({"hash": hash_[:7], "message": message, "files": files})
        return commits

    def _commit_files(self, hash_):
        """Return the list of files changed in a given commit, with readable state labels."""
        result = self.service.run_git("diff-tree", "--no-commit-id", "-r", "--name-status", hash_)
        if result["exit_code"] != 0 or not result["stdout"]:
            return []

        files = []
        for line in result["stdout"].splitlines():
            if line.strip():
                parts = line.split("\t", 1)
                files.append({"path": parts[1].strip(), "state": _map_state(parts[0].strip())})
        return files

    def _working_tree(self):
        """Return working tree state: whether it's clean and a list of changed files.

        Uses --porcelain for stable, script-friendly output format.
        """
        result = self.service.run_git("status", "--porcelain")
        if result["exit_code"] != 0:
            return {"clean": False, "files": []}

        files = []
        for line in result["stdout"].splitlines():
            if line.strip():
                raw_state = line[:2].strip()
                path = line[3:].strip()
                files.append({"path": path, "state": _map_state(raw_state)})

        return {"clean": len(files) == 0, "files": files}
