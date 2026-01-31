# Scripts

Scripts for local development and debugging against the real Toloka site. **Do not use in CI.** They require real credentials and are not part of the test suite (which uses mocks and fixtures).

## Prerequisites

- Install the package in editable mode from the repo root: `pip install -e .`
- Set credentials via environment variables (see below).

## Environment variables

| Variable          | Description        |
|-------------------|--------------------|
| `TOLOKA_USER`     | Your Toloka username |
| `TOLOKA_PASSWORD` | Your Toloka password |

**Example (PowerShell):**

```powershell
$env:TOLOKA_USER = "your_username"
$env:TOLOKA_PASSWORD = "your_password"
```

**Example (Bash):**

```bash
export TOLOKA_USER=your_username
export TOLOKA_PASSWORD=your_password
```

Optional: copy `.env.example` to `.env` in the repo root and fill in values. The `.env` file is gitignored. If you use `python-dotenv`, load it at the start of a script; `debug_live.py` does not load `.env` by default so that env vars remain the single source of truth for docs and launch configs.

## Scripts

### `debug_live.py`

Logs in to Toloka with your credentials and fetches your profile. Use it to debug the library with real HTTP requests (e.g. set breakpoints in `toloka2python/` and run this script under the debugger).

Run from the **repository root**:

```bash
python scripts/debug_live.py
```

Uses `debug_cookie.txt` in the repo root for the session (gitignored) so it does not overwrite a main `cookie.txt` if you use one elsewhere.

## Debugging in VS Code / Cursor

1. Open the repo in VS Code or Cursor.
2. Set breakpoints in `toloka2python/` (e.g. in `perform_login`, `get_account_info`).
3. Use the **"Debug toloka2python (live)"** launch configuration. It runs `scripts/debug_live.py` and injects `TOLOKA_USER` and `TOLOKA_PASSWORD` from the config.
4. Edit `.vscode/launch.json` and set your credentials in the `env` block for that configuration (do not commit real passwords; consider using a local override or environment).
