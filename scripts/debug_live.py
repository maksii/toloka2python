"""Run toloka2python against real Toloka with your credentials.

Uses TOLOKA_USER and TOLOKA_PASSWORD from the environment.
Use this script for debugging the library with real network requests.

  Set credentials (PowerShell):
    $env:TOLOKA_USER = "your_username"
    $env:TOLOKA_PASSWORD = "your_password"
  Run from repo root:
    python scripts/debug_live.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure repo root is on path when run as script
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from toloka2python import Toloka  # noqa: E402


def main() -> None:
    user = os.environ.get("TOLOKA_USER")
    password = os.environ.get("TOLOKA_PASSWORD")
    if not user or not password:
        print(
            "Set TOLOKA_USER and TOLOKA_PASSWORD in the environment.\n"
            "Example (PowerShell):\n"
            "  $env:TOLOKA_USER = \"your_username\"\n"
            "  $env:TOLOKA_PASSWORD = \"your_password\""
        )
        sys.exit(1)

    # Use a separate cookie file so debug sessions don't overwrite your main one
    cookie_file = REPO_ROOT / "debug_cookie.txt"
    t = Toloka(user, password, file=str(cookie_file), login=True)

    print("Logged in. Fetching profile (t.me)...")
    me = t.me
    print(f"  id: {me.id}")
    print(f"  last_login: {me.last_login}")
    print(f"  messages: {me.messages}")

    # Uncomment to exercise more code paths while debugging:
    # print("Search 'test'...")
    # for torrent in t.search("test")[:3]:
    #     print(f"  {torrent.name}")


if __name__ == "__main__":
    main()
