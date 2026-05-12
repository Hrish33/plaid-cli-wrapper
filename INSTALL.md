# Developer Setup

## Prerequisites

- Python 3.9+
- git

## Steps

**1. Clone the repo**
```bash
git clone <repo-url>
cd git_cli
```

**2. Create and activate a virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

**3. Install the package**
```bash
pip install -e .
```

This installs three CLI entry points into your venv:

| Command | Service |
|---------|---------|
| `gitwrap` | git |
| `dockerwrap` | docker (coming soon) |
| `kubewrap` | kubectl (coming soon) |

**4. Verify it works**

Navigate to any git repository and run:
```bash
gitwrap status
```

You should see YAML output with your branch, commits, and working tree state.

**5. Run the tests**
```bash
pip install pytest
pytest tests/ -v
```

## Notes

- `gitwrap` must be run from inside a git repository — it will error clearly if not
- The venv must be active for the `gitwrap` command to be available, or use the full path: `.venv/bin/gitwrap`
- See `README.md` for full command reference and `SKILL_GIT.md` for agent usage
