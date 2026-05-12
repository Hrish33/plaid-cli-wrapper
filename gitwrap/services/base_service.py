import subprocess


class BaseService:
    def run(self, *args, cwd=None) -> dict:
        result = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
