# gitwrap skill

> Setup: see [INSTALL.md](INSTALL.md)

gitwrap is a CLI tool that wraps git commands with safety guardrails. All output is YAML. Must be run inside a git repository.

## Invocation

```
gitwrap <command> [flags]
```

## Confirmation prompt

All destructive commands require typing a randomly chosen legendary Pokémon name to confirm. `--dry-run` always skips the prompt.

```
Push to remote — type 'RAYQUAZA' to confirm: _
```

Wrong input returns `status: aborted`. Correct input proceeds.

---

## Commands

### status
Show repo state: branch, unpushed/unpulled commits with files, and working tree changes.

```
gitwrap status
```

Output:
```yaml
command: status
status: ok
branch: main
unpushed: 1
unpulled: 0
local_commits:
  - hash: aebb3e5
    message: "add feature"
    files:
      - path: src/main.py
        state: modified   # added | modified | deleted | renamed | untracked
working_tree:
  clean: false
  files:
    - path: notes.txt
      state: untracked
staged_files:
  - src/app.js
unstaged_files:
  - README.md
untracked_files:
  - notes.txt
```

`staged_files`, `unstaged_files`, `untracked_files` are omitted when empty.

---

### clean
Remove untracked files. Requires `--dry-run`, `--force`, or `--yes`. Both `--force` and `--yes` trigger the confirmation prompt.

```
gitwrap clean --dry-run
gitwrap clean --force
gitwrap clean --yes       # alias for --force
```

Output (`dry_run`):
```yaml
command: clean
status: dry_run
files:
  - foo.txt
message: 2 file(s) would be removed
```

Output (`ok`):
```yaml
command: clean
status: ok
files:
  - foo.txt
message: 1 file(s) removed
```

---

### reset
Reset tracked files to HEAD. Requires `--dry-run` or `--force`. `--force` triggers confirmation prompt.

```
gitwrap reset --dry-run
gitwrap reset --force
```

Output (`dry_run`):
```yaml
command: reset
status: dry_run
files:
  - path: src/main.py
    state: M
message: 1 file(s) would be reset to HEAD
```

---

### commit
Stage all changes and commit. Requires `-m` and `--dry-run` or `--force`. `--force` triggers confirmation prompt.

```
gitwrap commit -m "message" --dry-run
gitwrap commit -m "message" --force
```

Output (`dry_run`):
```yaml
command: commit
status: dry_run
files:
  - src/main.py
message: 2 file(s) would be staged and committed
```

Output (`ok`):
```yaml
command: commit
status: ok
message: "your commit message"
output: "[main abc1234] your commit message"
```

---

### push
Push to remote. Always triggers confirmation prompt unless `--dry-run`.

```
gitwrap push
gitwrap push --dry-run
gitwrap push --force
```

Output (`ok`):
```yaml
command: push
status: ok
message: "Everything up-to-date"
```

---

## Error and abort formats

```yaml
status: error
message: "not inside a git repository"
```

```yaml
command: push
status: aborted
message: "expected 'RAYQUAZA', got 'WRONG' — push cancelled"
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0    | success or dry_run |
| 1    | error or aborted |

## Status values

| Value    | Meaning |
|----------|---------|
| ok       | command executed successfully |
| dry_run  | simulated, nothing changed |
| error    | command failed |
| aborted  | wrong confirmation word typed |

## Legendary Pokémon confirmation words

Gen 1: articuno, zapdos, moltres, mewtwo, mew

Gen 2: lugia, hooh, raikou, entei, suicune, celebi

Gen 3: kyogre, groudon, rayquaza, latios, latias, regice, regirock, registeel, jirachi, deoxys
