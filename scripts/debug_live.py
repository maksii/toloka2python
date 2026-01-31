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

SEARCH_QUERY = "JUJUTSU KAISEN"
MAX_SEARCH_RESULTS = 5
MAX_TORRENT_DETAILS = 1


def _full_url(toloka: Toloka, path: str) -> str:
    if path.startswith("http"):
        return path
    return f"{toloka.toloka_url}/{path.lstrip('/')}"


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

    cookie_file = REPO_ROOT / "debug_cookie.txt"
    t = Toloka(user, password, file=str(cookie_file), login=True)

    print("=" * 60)
    print("1. LOGIN")
    print("=" * 60)
    print("Logged in successfully (session stored in debug_cookie.txt).\n")

    print("=" * 60)
    print("2. MAIN PAGE (t.html)")
    print("=" * 60)
    html_resp = t.html
    print(f"  Status: {html_resp.status_code}")
    print(f"  URL: {html_resp.url}")
    print(f"  Content length: {len(html_resp.text)} chars\n")

    print("=" * 60)
    print("3. PROFILE (t.me)")
    print("=" * 60)
    me = t.me
    print(f"  id: {me.id}")
    print(f"  avatar: {me.avatar}")
    print(f"  online: {me.online}")
    print(f"  first_login: {me.first_login}")
    print(f"  last_login: {me.last_login}")
    print(f"  messages: {me.messages}")
    print(f"  uploaded: {me.uploaded}")
    print(f"  downloaded: {me.downloaded}")
    print(f"  releases: {me.releases}")
    print(f"  thanks: {me.thanks}")
    print(f"  passkey: {(me.passkey[:8] + '...') if me.passkey else 'N/A'}")
    upload_count = len(me.upload_torrent) if hasattr(me.upload_torrent, "__len__") else "N/A"
    print(f"  upload_torrent count: {upload_count}\n")

    print("=" * 60)
    print(f"4. SEARCH (t.search) query={SEARCH_QUERY!r}")
    print("=" * 60)
    search_results = t.search(SEARCH_QUERY)
    print(f"  Total results: {len(search_results)}")
    for i, e in enumerate(search_results[:MAX_SEARCH_RESULTS], 1):
        print(f"  [{i}] {e.name[:70]}{'...' if len(e.name) > 70 else ''}")
        print(f"      forum={e.forum} | size={e.size} | S:{e.seeders} L:{e.leechers} | {e.date}")
        print(f"      url={e.url}")
    print()

    print("=" * 60)
    print(f"5. SEARCH V2 / API (t.searchv2) query={SEARCH_QUERY!r}")
    print("=" * 60)
    searchv2_results = t.searchv2(SEARCH_QUERY)
    print(f"  Total results: {len(searchv2_results)}")
    for i, e in enumerate(searchv2_results[:MAX_SEARCH_RESULTS], 1):
        print(f"  [{i}] {e.name[:70]}{'...' if len(e.name) > 70 else ''}")
        print(f"      size={e.size} | seeders={e.seeders} leechers={e.leechers} | answers={e.answers}")
    print()

    if search_results:
        print("=" * 60)
        print("6. TORRENT DETAIL (t.get_torrent) — first search result")
        print("=" * 60)
        first = search_results[0]
        topic_url = _full_url(t, first.url)
        try:
            torrent = t.get_torrent(topic_url)
            print(f"  name: {torrent.name}")
            print(f"  forum: {torrent.forum}")
            print(f"  author: {torrent.author}")
            print(f"  size: {torrent.size}")
            print(f"  thanks: {torrent.thanks}")
            print(f"  rating: {torrent.rating}")
            print(f"  date: {torrent.date}")
            print(f"  files count: {len(torrent.files) if torrent.files else 0}")
            if torrent.files:
                for f in (torrent.files or [])[:5]:
                    print(f"    - {f.file_name} ({f.size})")
        except Exception as err:
            print(f"  Error: {err}")
        print()

    if search_results:
        print("=" * 60)
        print("7. DOWNLOAD TORRENT (t.download_torrent) — first result .torrent")
        print("=" * 60)
        first = search_results[0]
        if getattr(first, "torrent_url", None):
            dl_url = _full_url(t, first.torrent_url)
            content = t.download_torrent(dl_url)
            print(f"  Downloaded {len(content)} bytes")
        else:
            print("  (No torrent_url in search result; skipping)")
        print()

    print("=" * 60)
    print("8. GET ACCOUNT BY URL (t.get_account) — own profile")
    print("=" * 60)
    profile_url = me.id if me.id.startswith("http") else _full_url(t, me.id)
    other = t.get_account(profile_url)
    print(f"  id: {other.id}")
    print(f"  last_login: {other.last_login}")
    print("  (Same as t.me when using own profile URL)\n")

    print("=" * 60)
    print("Done. All actions completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
