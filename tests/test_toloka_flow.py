import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import requests

from toloka2python import Toloka

EXAMPLES_DIR = Path(__file__).resolve().parent / "examples"
MAIN_HTML = (EXAMPLES_DIR / "main.html").read_text(encoding="utf-8")
MAIN_NOT_AUTH_HTML = (EXAMPLES_DIR / "main_not_auth.html").read_text(encoding="utf-8")
LOGIN_FORM_HTML = (EXAMPLES_DIR / "login_form.html").read_text(encoding="utf-8")
ACCOUNT_HTML = (EXAMPLES_DIR / "auth_profile.html").read_text(encoding="utf-8")
SEARCH_SINGLE_HTML = (EXAMPLES_DIR / "search_by_name_single_result.html").read_text(
    encoding="utf-8"
)
SEARCH_MULTIPLE_HTML = (EXAMPLES_DIR / "search_by_name_multiple_result.html").read_text(
    encoding="utf-8"
)
SEARCH_NO_RESULT_HTML = (EXAMPLES_DIR / "search_by_name_no_result.html").read_text(
    encoding="utf-8"
)
SEARCH_INITIAL_HTML = (
    EXAMPLES_DIR / "search_all_no_param_initial_state.html"
).read_text(encoding="utf-8")

TORRENT_HTML = """
<html>
  <head>
    <link rel="image_src" href="thumb.jpg"/>
  </head>
  <body>
    <div>Відео: Example video details MediaInfo</div>
    <a class="maintitle" href="/t123">Sample Torrent</a>
    <td class="nav"><h2>Ignore</h2><h2><a href="f100">Movies</a></h2></td>
    <td class="row1"><span class="name"><b><a>Uploader</a></b></span></td>
    <img alt="Sample Torrent" src="poster.jpg"/>
    <tr class="row6_to">\n  Sample Torrent Name  \n</tr>
    <table>
      <tr>
        <td>\u00a0Зареєстрований:\u00a0</td>
        <td>---2024-01-01</td>
      </tr>
      <tr>
        <td>\u00a0Розмір:\u00a0</td>
        <td><span>700\u00a0MB</span></td>
      </tr>
      <tr>
        <td>\u00a0Подякували:\u00a0</td>
        <td><span>11</span></td>
      </tr>
    </table>
    <span itemprop="ratingValue">4.5</span>
    <a>Ignore</a>
    <a href="/download.torrent">Завантажити</a>
    <div class="files-wrap">
      <tr>
        <td align="left">Sample Folder</td>
      </tr>
      <tr>
        <td>ignore</td>
        <td align="left">file1.mkv</td>
        <td align="right">700\u00a0MB</td>
      </tr>
    </div>
  </body>
</html>
"""


class FakeResponse:
    def __init__(self, text="", url="", content=b"", json_data=None):
        self.text = text
        self.url = url
        self.content = content
        self._json_data = json_data

    def json(self):
        return self._json_data

    def raise_for_status(self):
        return None


class FakeSession:
    def __init__(self, default_main_html=MAIN_HTML):
        self.headers = {}
        self.cookies = requests.cookies.RequestsCookieJar()
        self.default_main_html = default_main_html

    def post(self, url, data):
        self.cookies.set("session", "abc123")
        return FakeResponse(text="ok", url=url)

    def get(self, url):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        if url.endswith("/f50"):
            return FakeResponse(text="ok", url=url)
        if url.endswith("/api.php?search=magic"):
            return FakeResponse(
                url=url,
                json_data=[
                    {
                        "forum_name": "Forum",
                        "forum_parent": "forum-url",
                        "link": "https://toloka.to/t123",
                        "title": "Sample Torrent",
                        "size": "1 GB",
                        "seeders": 10,
                        "leechers": 2,
                        "comments": 4,
                    }
                ],
            )
        if parsed_url.path.endswith("/tracker.php"):
            nm_value = query_params.get("nm", [""])[0]
            if nm_value == "Sample Release":
                return FakeResponse(text=SEARCH_SINGLE_HTML, url=url)
            if nm_value == "Sample":
                return FakeResponse(text=SEARCH_MULTIPLE_HTML, url=url)
            if nm_value == "NoResults":
                return FakeResponse(text=SEARCH_NO_RESULT_HTML, url=url)
            if nm_value == "":
                return FakeResponse(text=SEARCH_INITIAL_HTML, url=url)
        if url.endswith("/download.torrent"):
            return FakeResponse(content=b"torrent-bytes", url=url)
        if parsed_url.path.startswith("/u"):
            return FakeResponse(text=ACCOUNT_HTML, url=url)
        if "spmode=full" in url:
            return FakeResponse(text=TORRENT_HTML, url=url)
        if url in {"https://toloka.to", "https://example.test"}:
            return FakeResponse(text=self.default_main_html, url=url)
        return FakeResponse(text="", url=url)


class TestTolokaFlow(unittest.TestCase):
    def test_full_flow_with_mocked_session(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cookie_file = f"{tmp_dir}/cookies.json"
            with patch.object(Toloka, "toloka_url", "https://example.test"):
                with patch("toloka2python.requests.Session", return_value=FakeSession()):
                    toloka = Toloka("user", "pass", file=cookie_file)

            torrents = toloka.search("Sample Release")
            self.assertEqual(len(torrents), 1)
            self.assertEqual(torrents[0].name, "Sample Release")

            api_torrents = toloka.searchv2("magic")
            self.assertEqual(api_torrents[0].seeders, 10)

            me = toloka.me
            self.assertEqual(me.id, "https://example.test/u000001")

            account = toloka.get_account("https://example.test/u000001")
            self.assertEqual(account.passkey, "FAKEPASSKEY")

            torrent = toloka.get_torrent("https://example.test/t123")
            self.assertEqual(torrent.forum, "Movies")
            self.assertEqual(torrent.files[0].file_name, "file1.mkv")

            content = toloka.download_torrent("https://example.test/download.torrent")
            self.assertEqual(content, b"torrent-bytes")

            with open(cookie_file, "r", encoding="utf-8") as handle:
                cookies = json.load(handle)
            self.assertEqual(cookies["session"], "abc123")

    def test_search_multiple_results(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cookie_file = f"{tmp_dir}/cookies.json"
            with patch.object(Toloka, "toloka_url", "https://example.test"):
                with patch("toloka2python.requests.Session", return_value=FakeSession()):
                    toloka = Toloka("user", "pass", file=cookie_file)

            torrents = toloka.search("Sample")
            self.assertGreater(len(torrents), 1)
            self.assertTrue(all(torrent.name for torrent in torrents))

    def test_search_no_results(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cookie_file = f"{tmp_dir}/cookies.json"
            with patch.object(Toloka, "toloka_url", "https://example.test"):
                with patch("toloka2python.requests.Session", return_value=FakeSession()):
                    toloka = Toloka("user", "pass", file=cookie_file)

            torrents = toloka.search("NoResults")
            self.assertEqual(torrents, [])

    def test_search_initial_state(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cookie_file = f"{tmp_dir}/cookies.json"
            with patch.object(Toloka, "toloka_url", "https://example.test"):
                with patch("toloka2python.requests.Session", return_value=FakeSession()):
                    toloka = Toloka("user", "pass", file=cookie_file)

            torrents = toloka.search("")
            self.assertGreater(len(torrents), 0)
            self.assertEqual(torrents[0].date, "26-01-31 00:00")

    def test_validate_cookies_with_login_form(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cookie_file = f"{tmp_dir}/cookies.json"
            with patch.object(Toloka, "toloka_url", "https://example.test"):
                with patch(
                    "toloka2python.requests.Session",
                    return_value=FakeSession(default_main_html=MAIN_NOT_AUTH_HTML),
                ):
                    toloka = Toloka("user", "pass", file=cookie_file)

            login_response = FakeResponse(
                text=LOGIN_FORM_HTML,
                url="https://toloka.to/login.php?redirect=viewforum.php?f=50",
            )
            with patch.object(toloka.session, "get", return_value=login_response):
                self.assertFalse(toloka.validate_cookies())

    def test_main_not_authenticated_html(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cookie_file = f"{tmp_dir}/cookies.json"
            with patch.object(Toloka, "toloka_url", "https://example.test"):
                with patch(
                    "toloka2python.requests.Session",
                    return_value=FakeSession(default_main_html=MAIN_NOT_AUTH_HTML),
                ):
                    toloka = Toloka("user", "pass", file=cookie_file)

            self.assertIn("Вхід", toloka.html.text)

if __name__ == "__main__":
    unittest.main()
