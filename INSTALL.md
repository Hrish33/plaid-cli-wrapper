# Developer Setup

## Prerequisites

- Python 3.9+
- git

## Option A — Local development (venv)

Use this if you want to contribute or modify the code.

**1. Clone the repo**
```bash
git clone https://github.com/Hrish33/plaid-cli-wrapper.git gitwrap
cd gitwrap
```

**2. Create and activate a virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

**3. Install in editable mode**
```bash
pip install -e .
```

**4. Verify it works**

Navigate to any git repository and run:
```bash
gitwrap status
```

**5. Run the tests**
```bash
pytest tests/ -v
```

> The venv must be active for `gitwrap` to be available. To use it in a different shell session, re-run `source .venv/bin/activate` first.

---

## Option B — Global install (always available)

Use this if you just want the tool available everywhere without activating a venv each time.

**1. Clone the repo**
```bash
git clone https://github.com/Hrish33/plaid-cli-wrapper.git gitwrap
cd gitwrap
```

**2. Install globally**
```bash
pip install -e .
```

> Run this outside any venv and pip installs the entry points into your system Python's bin directory.

**3. Verify**
```bash
which gitwrap       # should point to your system Python's bin
gitwrap status
dockerwrap          # coming soon
kubewrap            # coming soon
```

---

## Entry points installed

`pip install -e .` registers three CLI commands regardless of install method:

| Command | Service |
|---------|---------|
| `gitwrap` | git |
| `dockerwrap` | docker (coming soon) |
| `kubewrap` | kubectl (coming soon) |

The binary name determines which service loads — no extra config needed.

---

## Notes

- `gitwrap` must be run from inside a git repository — it exits cleanly with a YAML error if not
- See [README.md](README.md) for full command reference
- See [SKILL_GIT.md](SKILL_GIT.md) for agent usage
