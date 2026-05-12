# gitwrap — Plan

## What it is

A CLI tool that wraps common git commands with safety guardrails, dry-run support, and YAML output by default. Git is the only supported service for now, but the architecture is layered so adding docker, kubectl, etc. is straightforward.

---

## CLI Interface

```
gitwrap <command> [flags]

gitwrap status
gitwrap clean --dry-run
gitwrap clean --force
gitwrap reset --dry-run
gitwrap reset --force
gitwrap push
gitwrap push --allow-force
gitwrap commit -m "message"
gitwrap commit --dry-run
```

Git is implicit — users don't type `gitwrap git status`. The service layer lives in the code structure only.

---

## Commands

| Command  | Wraps              | Dangerous? | dry-run | force flag     |
|----------|--------------------|------------|---------|----------------|
| status   | git status         | No         | N/A     | N/A            |
| clean    | git clean -fd      | Yes        | Yes     | --force        |
| reset    | git reset --hard   | Yes        | Yes     | --force        |
| push     | git push           | Moderate   | No      | --allow-force  |
| commit   | git commit         | No         | Yes     | N/A            |

**Dry-run behavior per command:**
- `clean --dry-run`: show files that *would* be deleted (git clean -nfd)
- `reset --dry-run`: show files that *would* be changed/lost vs HEAD
- `commit --dry-run`: show staged files that *would* be committed
- Destructive commands without `--force` and without `--dry-run`: exit with an error message asking the user to add one of the two flags

---

## Output Format

All output is YAML by default. Structure:

```yaml
command: clean
dry_run: true
status: ok          # ok | error | dry_run
files:
  - path/to/file.txt
  - path/to/other.txt
message: "2 files would be removed"
```

```yaml
command: commit
dry_run: false
status: ok
hash: "a1b2c3d"
message: "fix: update config"
files:
  - src/main.py
```

```yaml
command: reset
status: error
message: "Destructive command requires --force or --dry-run"
```

---

## Architecture

```
gitwrap/
  __main__.py           # entry point, argparse top-level dispatch
  output.py             # YAML formatter, single format() function
  services/
    base_service.py     # BaseService: subprocess runner, error handling
    git/
      service.py        # GitService(BaseService): git-specific subprocess calls
      commands/
        base_command.py # BaseCommand: run(), dry_run(), requires_force check
        status.py
        clean.py
        reset.py
        push.py
        commit.py
tests/
  unit/
    test_output.py
    test_status.py
    test_clean.py
    test_reset.py
    test_push.py
    test_commit.py
  integration/
    conftest.py         # pytest fixture: tmp real git repo
    test_git_integration.py
```

### Layer responsibilities

**`__main__.py`**
- Parses top-level args with argparse
- Detects git repo early (`git rev-parse --is-inside-work-tree`) — exits cleanly if not in one
- Routes to the correct command class

**`services/base_service.py`**
- Runs subprocess commands, captures stdout/stderr
- Returns structured result dict (exit code, stdout, stderr)
- Adding docker later = `services/docker/service.py` subclassing this

**`services/git/service.py`**
- Git-specific calls (wraps BaseService)
- Methods like `run_git(*args)`, `is_repo()`, `get_status()`, etc.

**`services/git/commands/base_command.py`**
- Abstract base with `execute(args)` entrypoint
- Enforces: if `is_destructive` and no `--force` and no `--dry-run` → error
- Calls `dry_run()` or `run()` depending on flags
- Passes result to `output.format()`

**`output.py`**
- Single `format(result: dict) -> str` that dumps YAML
- All commands produce the same dict shape, output layer doesn't care which command ran

---

## Adding a New Service (e.g. docker)

1. Create `services/docker/service.py` subclassing `BaseService`
2. Create `services/docker/commands/` with command classes
3. Register in `__main__.py` — one block of argparse subcommand wiring

No changes to existing code needed.

---

## Testing Strategy

**Unit tests** — mock `GitService`, test command logic in isolation:
- Does `clean` without `--force`/`--dry-run` return an error result?
- Does `commit` with empty `-m ""` return an error?
- Does `push --allow-force` pass the right flags through?
- Does `output.format()` produce valid YAML for all result shapes?

**Integration tests** — real temp git repo via pytest fixture in `conftest.py`:
- `git init` a tmpdir, make commits, stage files, add untracked files
- Run actual command classes against it
- Assert YAML output matches expected state
- Assert files were/weren't actually deleted after `clean`

---

## Dependencies

- `pyyaml` — YAML output
- `pytest` — tests
- stdlib only otherwise (`argparse`, `subprocess`, `pathlib`)

---

---

## Execution Plan

### Step 1 — Scaffold
- Create directory structure (all folders and empty `__init__.py` files)
- `pyproject.toml` with deps: `pyyaml`, `pytest`
- Verify `pip install -e .` works and `gitwrap` is invokable

### Step 2 — Base layer (no commands yet)
- `output.py` — `format(result: dict) -> str` using pyyaml
- `services/base_service.py` — `BaseService` with `run(*args)` wrapping subprocess
- `services/git/service.py` — `GitService(BaseService)` with `run_git(*args)` and `is_repo()`
- `services/git/commands/base_command.py` — `BaseCommand` abstract class with `execute()`, `run()`, `dry_run()`, force-guard logic

### Step 3 — Git repo detection in entry point
- `__main__.py` — argparse skeleton, calls `GitService.is_repo()` on startup, exits cleanly with YAML error if not in a repo

### Step 4 — First command: `status` (fully functional)
- `status.py` — implements `run()` calling `git status --porcelain`
- Parses porcelain output into a list of `{path, state}` dicts
- Returns `clean: true` if no files, `clean: false` otherwise
- Wire `gitwrap status` into `__main__.py`

### Step 5 — Unit tests for `status`
Mock `GitService` entirely. Test these cases:
- Clean repo (empty stdout) → `clean: true`, empty files list
- Modified file → correct path and state in files list
- Untracked file (`??`) → correct state
- Git returns non-zero → error result propagated correctly
- `output.render()` produces valid YAML for each result shape

---

## What We're NOT doing (to keep scope tight)

- No config file
- No color output
- No interactive prompts (--force flag instead)
- No support for git flags we don't explicitly handle
- No push to PyPI / packaging
