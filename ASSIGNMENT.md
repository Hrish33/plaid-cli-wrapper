# 📘 `gitwrap` — Safer Git CLI Wrapper

## 🧩 Overview

Create a `gitwrap` CLI tool that provides a safer interface to common git commands by:

- Preventing mistakes like cleaning untracked files without confirmation
- Providing a dry-run mode that shows **what will happen**, not just what did
- Giving consistent, machine-readable **YAML output** to make wrapping or scripting easier

This assignment is about building such a tool.

---

## ✅ Required Commands

### 1. `gitwrap clean`

A wrapper around `git clean -fd` with built-in safety.

- Prompt the user before deleting any files.
- Require a `--yes` flag to skip the prompt.
- In `--dry-run` mode, list the files that *would be* deleted (but don't delete them).

> ✅ Behavior:
>
> ```bash
> $ gitwrap clean
> This will delete 4 untracked files. Continue? [y/N]:
> ```
>
> ```bash
> $ gitwrap clean --dry-run
> dry_run: true
> action: clean
> files:
>   - tmp/debug.log
>   - out/old-build.tar
> ```

---

### 2. `gitwrap status`

A wrapper around `git status` that outputs key information in **YAML format**.

> ✅ Output format:
>
> ```yaml
> action: status
> branch: feature/new-ui
> staged_files:
>   - src/app.js
>   - styles/main.css
> unstaged_files:
>   - README.md
>   - .gitignore
> untracked_files:
>   - temp.txt
>   - notes.md
> ```

Only include files that exist under each category (empty lists should be omitted for brevity).

---

### 3. `--dry-run` (Global Flag)

All commands should accept a `--dry-run` flag that outputs what the tool *would* do, instead of doing it. For example:

> ```bash
> $ gitwrap clean --dry-run
> ```

...should output YAML like:

```yaml
dry_run: true
action: clean
files:
  - node_modules/debug.log
  - tmp/unused.txt
```

---

### Timeline

You should expect to work on this for no more than two hours. This is a guideline and if you find you finish sooner or a bit later, don't worry. The test is also not timed so as to be flexible if you need to start and stop. Please return this test at least 2 business days before your scheduled interview time.

### Submission

When you're done, please email your recruiter a zip file of your solution. You can then discuss your approach and thought process with an Infrastructure Engineer during your scheduled interview time. Please note that this interview is _not_ a live coding exercise and the code you submit will be reviewed as-is. If you have any other questions, please don't hesitate to reach out.

### Example of some of the questions we will ask you

- Q: "How would you ship this tool across your company so everyone can use it reliably?"
