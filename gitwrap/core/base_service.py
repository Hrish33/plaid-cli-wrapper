import subprocess


class BaseService:
    """Base class for all service wrappers (git, docker, kubectl, etc.).

    Provides a single subprocess runner that captures stdout/stderr and
    normalises the result into a consistent dict. Subclasses add
    tool-specific methods on top of this.
    """

    def run(self, *args, cwd=None) -> dict:
        """Run an arbitrary shell command and return its output.

        Args:
            *args: Command and arguments, e.g. ("git", "status", "--porcelain").
            cwd: Working directory to run the command in.

        Returns:
            Dict with keys exit_code, stdout, stderr (all strings, stripped).
        """
        result = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
