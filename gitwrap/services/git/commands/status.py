from ....core.base_command import BaseCommand

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
        working_tree, staged_files, unstaged_files, untracked_files = self._working_tree()

        result = {
            "command": "status",
            "status": "ok",
            "branch": branch,
            "unpushed": unpushed,
            "unpulled": unpulled,
            "local_commits": local_commits,
            "working_tree": working_tree,
        }
        # Only include non-empty file lists (per spec)
        if staged_files:
            result["staged_files"] = staged_files
        if unstaged_files:
            result["unstaged_files"] = unstaged_files
        if untracked_files:
            result["untracked_files"] = untracked_files
        return result

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

        if ahead["exit_code"] == 0:
            unpushed = int(ahead["stdout"])
        else:
            unpushed = None

        if behind["exit_code"] == 0:
            unpulled = int(behind["stdout"])
        else:
            unpulled = None

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
            parts = line.split(" ", 1)
            hash_ = parts[0]
            message = parts[1] if len(parts) > 1 else ""
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
        """Return (working_tree_dict, staged_files, unstaged_files, untracked_files).

        Parses --porcelain once to populate all four values. The first column (X)
        is the index/staged status; the second (Y) is the working tree status.
        """
        result = self.service.run_git("status", "--porcelain")
        if result["exit_code"] != 0:
            return {"clean": False, "files": []}, [], [], []

        staged, unstaged, untracked, all_files = [], [], [], []
        for line in result["stdout"].splitlines():
            if not line.strip():
                continue
            x = line[0]
            y = line[1]
            path = line[3:].strip()
            if x == "?" and y == "?":
                untracked.append(path)
            else:
                if x != " ":
                    staged.append(path)
                if y != " ":
                    unstaged.append(path)
            all_files.append({"path": path, "state": _map_state(line[:2].strip())})

        return {"clean": len(all_files) == 0, "files": all_files}, staged, unstaged, untracked
