import json
import tempfile
import unittest
from unittest.mock import patch

import requests

from toloka2python import Toloka


MAIN_HTML = """
<html>
  <body>
    <a href="u123456">Профіль</a>
  </body>
</html>
"""

ACCOUNT_HTML = """
<html>
  <body>
    <a href="u123456">Профіль</a>
    <span class="postdetails"><img src="avatar.png"/></span>
    <table>
      <tr>
        <td class="bodyline">ignore</td>
        <td class="bodyline">
          <font>(в мережі)</font>
          <table>
            <tr>
              <td class="row1">ignore row1 0</td>
              <td class="row1">
                <table>
                  <tr>
                    <td><span class="gen">First login</span><span class="gen">2023-01-01</span></td>
                  </tr>
                  <tr>
                    <td><span class="gen">Last login</span><span class="gen">2023-02-01</span></td>
                  </tr>
                  <tr>
                    <td><span class="gen">Messages</span><span class="gen">5</span></td>
                  </tr>
                </table>
              </td>
              <td class="row1">
                <table>
                  <tr>
                    <td><span class="gen">Email</span><span class="gen">user@example.com</span></td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td class="row2">
                <table>
                  <tr><td>header</td></tr>
                  <tr>
                    <td>
                      <span class="seed"><b>100 GB</b></span>
                      <span class="seed"><b>10 GB</b></span>
                      <span class="seed"><b>1 GB</b></span>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <span class="leech"><b>200 GB</b></span>
                      <span class="leech"><b>20 GB</b></span>
                      <span class="leech"><b>2 GB</b></span>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <span class="gen">Bonus</span>
                      <span class="gen">1000</span>
                      <span class="gen">ignore</span>
                      <span class="gen">100</span>
                      <span class="gen">10</span>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <span class="gen">Ratio</span>
                      <span class="gen">1.50 2.00x</span>
                    </td>
                  </tr>
                  <tr><td>ignore</td></tr>
                  <tr>
                    <td>
                      <span class="seed">3</span>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <span class="gen">Thanks</span>
                      <span class="gen">7</span>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <span class="leech"><b>500 GB</b></span>
                      <span class="seed"><b>250 GB</b></span>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <span class="gen">Passkey</span>
                      <span class="gen">passkey123</span>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>
          <table class="forumline"></table>
          <table class="forumline">
            <tr></tr>
            <tr></tr>
            <tr></tr>
            <tr></tr>
            <tr></tr>
            <tr></tr>
            <tr>
              <td><span class="gen">Forum</span></td>
              <td><a class="gen" href="forum-url">Forum</a></td>
              <td><a class="genmed" href="torrent-url">Torrent Name</a></td>
              <td><span class="seedmed">5</span></td>
              <td><span class="leechmed">2</span></td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""

SEARCH_HTML = """
<html>
  <body>
    <table>
      <tr class="prow1">
        <td>0</td>
        <td><a class="gen" href="forum-url">Forum Name</a></td>
        <td><a href="/t123">Sample Torrent</a></td>
        <td>Author</td>
        <td>+</td>
        <td><a href="/download.torrent">dl</a></td>
        <td>1 GB</td>
        <td title="Active">status</td>
        <td></td>
        <td>10</td>
        <td>2</td>
        <td>4</td>
        <td>2024-01-15</td>
      </tr>
    </table>
  </body>
</html>
"""

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
    def __init__(self):
        self.headers = {}
        self.cookies = requests.cookies.RequestsCookieJar()

    def post(self, url, data):
        self.cookies.set("session", "abc123")
        return FakeResponse(text="ok", url=url)

    def get(self, url):
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
        if url.endswith("/tracker.php?nm=Magic&pn=&send=Пошук"):
            return FakeResponse(text=SEARCH_HTML, url=url)
        if url.endswith("/download.torrent"):
            return FakeResponse(content=b"torrent-bytes", url=url)
        if url.endswith("/u123456"):
            return FakeResponse(text=ACCOUNT_HTML, url=url)
        if "spmode=full" in url:
            return FakeResponse(text=TORRENT_HTML, url=url)
        if url == "https://toloka.to":
            return FakeResponse(text=MAIN_HTML, url=url)
        return FakeResponse(text="", url=url)


class TestTolokaFlow(unittest.TestCase):
    def test_full_flow_with_mocked_session(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cookie_file = f"{tmp_dir}/cookies.json"
            with patch("toloka2python.requests.Session", return_value=FakeSession()):
                toloka = Toloka("user", "pass", file=cookie_file)

            torrents = toloka.search("Magic")
            self.assertEqual(len(torrents), 1)
            self.assertEqual(torrents[0].name, "Sample Torrent")

            api_torrents = toloka.searchv2("magic")
            self.assertEqual(api_torrents[0].seeders, 10)

            me = toloka.me
            self.assertEqual(me.id, "u123456")

            account = toloka.get_account("https://toloka.to/u123456")
            self.assertEqual(account.passkey, "passkey123")

            torrent = toloka.get_torrent("https://toloka.to/t123")
            self.assertEqual(torrent.forum, "Movies")
            self.assertEqual(torrent.files[0].file_name, "file1.mkv")

            content = toloka.download_torrent("https://toloka.to/download.torrent")
            self.assertEqual(content, b"torrent-bytes")

            with open(cookie_file, "r", encoding="utf-8") as handle:
                cookies = json.load(handle)
            self.assertEqual(cookies["session"], "abc123")


if __name__ == "__main__":
    unittest.main()
