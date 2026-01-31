"""Tests for HTTP error codes and status handling."""

import tempfile
import unittest
from unittest.mock import Mock, patch

import requests

from toloka2python import Toloka


def make_http_error_response(status_code: int, reason: str = "Error"):
    """Build a response-like object that raises HTTPError on raise_for_status()."""
    resp = Mock()
    resp.status_code = status_code
    resp.reason = reason
    resp.url = "https://example.test/"
    resp.text = ""
    resp.content = b""
    resp.headers = {}

    def raise_for_status():
        raise requests.exceptions.HTTPError(response=resp)

    resp.raise_for_status = raise_for_status
    return resp


# Common HTTP status codes to cover: client and server errors (incl. 429 rate limit)
HTTP_ERROR_STATUSES = [400, 401, 403, 404, 429, 500, 502, 503]


class TestLoginHttpErrors(unittest.TestCase):
    """Test that login (POST) propagates HTTP errors."""

    def test_perform_login_raises_on_4xx(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cookie_file = f"{tmp_dir}/cookies.json"
            with patch.object(Toloka, "toloka_url", "https://example.test"):
                with patch("toloka2python.requests.Session") as SessionMock:
                    session = SessionMock.return_value
                    session.headers = {}
                    session.cookies = requests.cookies.RequestsCookieJar()
                    session.post.return_value = make_http_error_response(
                        401, "Unauthorized"
                    )

                    with self.assertRaises(requests.exceptions.HTTPError) as ctx:
                        Toloka("user", "pass", file=cookie_file, login=True)
                    self.assertEqual(ctx.exception.response.status_code, 401)

    def test_perform_login_raises_on_429(self):
        """Rate limit (Too Many Requests) on login propagates as HTTPError."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            cookie_file = f"{tmp_dir}/cookies.json"
            with patch.object(Toloka, "toloka_url", "https://example.test"):
                with patch("toloka2python.requests.Session") as SessionMock:
                    session = SessionMock.return_value
                    session.headers = {}
                    session.cookies = requests.cookies.RequestsCookieJar()
                    session.post.return_value = make_http_error_response(
                        429, "Too Many Requests"
                    )

                    with self.assertRaises(requests.exceptions.HTTPError) as ctx:
                        Toloka("user", "pass", file=cookie_file, login=True)
                    self.assertEqual(ctx.exception.response.status_code, 429)

    def test_perform_login_raises_on_5xx(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cookie_file = f"{tmp_dir}/cookies.json"
            with patch.object(Toloka, "toloka_url", "https://example.test"):
                with patch("toloka2python.requests.Session") as SessionMock:
                    session = SessionMock.return_value
                    session.headers = {}
                    session.cookies = requests.cookies.RequestsCookieJar()
                    session.post.return_value = make_http_error_response(
                        503, "Service Unavailable"
                    )

                    with self.assertRaises(requests.exceptions.HTTPError) as ctx:
                        Toloka("user", "pass", file=cookie_file, login=True)
                    self.assertEqual(ctx.exception.response.status_code, 503)


class TestValidateCookiesHttpErrors(unittest.TestCase):
    """Test that validate_cookies propagates HTTP errors (during login)."""

    def test_validate_cookies_get_raises_during_login(self):
        """When cookie validation GET returns an error status, HTTPError propagates from login."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            cookie_file = f"{tmp_dir}/cookies.json"
            with patch.object(Toloka, "toloka_url", "https://example.test"):
                with patch("toloka2python.requests.Session") as SessionMock:
                    session = SessionMock.return_value
                    session.headers = {}
                    session.cookies = requests.cookies.RequestsCookieJar()
                    session.post.return_value = Mock(
                        status_code=200,
                        url="https://example.test/login.php",
                        text="ok",
                        raise_for_status=Mock(),
                    )
                    session.get.return_value = make_http_error_response(
                        502, "Bad Gateway"
                    )

                    with self.assertRaises(requests.exceptions.HTTPError) as ctx:
                        Toloka("user", "pass", file=cookie_file, login=True)
                    self.assertEqual(ctx.exception.response.status_code, 502)


class TestSearchHttpErrors(unittest.TestCase):
    """Test that search() propagates HTTP errors for various status codes."""

    def _toloka_with_session_get_success_then_error(self, error_response):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cookie_file = f"{tmp_dir}/cookies.json"
            with patch.object(Toloka, "toloka_url", "https://example.test"):
                with patch("toloka2python.requests.Session") as SessionMock:
                    session = SessionMock.return_value
                    session.headers = {}
                    session.cookies = requests.cookies.RequestsCookieJar()
                    session.post.return_value = Mock(
                        status_code=200,
                        url="https://example.test/login.php",
                        text="ok",
                        raise_for_status=Mock(),
                    )
                    ok_response = Mock(
                        status_code=200,
                        url="https://example.test/f50",
                        text="ok",
                        raise_for_status=Mock(),
                    )
                    session.get.side_effect = [ok_response, error_response]
                    return Toloka("user", "pass", file=cookie_file, login=True), session

    def test_search_raises_on_404(self):
        toloka, _ = self._toloka_with_session_get_success_then_error(
            make_http_error_response(404, "Not Found")
        )
        with self.assertRaises(requests.exceptions.HTTPError) as ctx:
            toloka.search("query")
        self.assertEqual(ctx.exception.response.status_code, 404)

    def test_search_raises_on_500(self):
        toloka, _ = self._toloka_with_session_get_success_then_error(
            make_http_error_response(500, "Internal Server Error")
        )
        with self.assertRaises(requests.exceptions.HTTPError) as ctx:
            toloka.search("query")
        self.assertEqual(ctx.exception.response.status_code, 500)

    def test_search_raises_on_429(self):
        """Rate limit (Too Many Requests) on search propagates as HTTPError."""
        toloka, _ = self._toloka_with_session_get_success_then_error(
            make_http_error_response(429, "Too Many Requests")
        )
        with self.assertRaises(requests.exceptions.HTTPError) as ctx:
            toloka.search("query")
        self.assertEqual(ctx.exception.response.status_code, 429)

    def test_search_raises_on_503(self):
        toloka, _ = self._toloka_with_session_get_success_then_error(
            make_http_error_response(503, "Service Unavailable")
        )
        with self.assertRaises(requests.exceptions.HTTPError) as ctx:
            toloka.search("query")
        self.assertEqual(ctx.exception.response.status_code, 503)


class TestSearchV2HttpErrors(unittest.TestCase):
    """Test that searchv2() propagates HTTP errors."""

    def test_searchv2_raises_on_4xx_and_5xx(self):
        for status_code in HTTP_ERROR_STATUSES:
            with self.subTest(status_code=status_code):
                with tempfile.TemporaryDirectory() as tmp_dir:
                    cookie_file = f"{tmp_dir}/cookies.json"
                    with patch.object(Toloka, "toloka_url", "https://example.test"):
                        with patch("toloka2python.requests.Session") as SessionMock:
                            session = SessionMock.return_value
                            session.headers = {}
                            session.cookies = requests.cookies.RequestsCookieJar()
                            session.post.return_value = Mock(
                                status_code=200,
                                url="https://example.test/login.php",
                                text="ok",
                                raise_for_status=Mock(),
                            )
                            ok_validate = Mock(
                                status_code=200,
                                url="https://example.test/f50",
                                text="ok",
                                raise_for_status=Mock(),
                            )
                            session.get.side_effect = [
                                ok_validate,
                                make_http_error_response(status_code),
                            ]
                            toloka = Toloka(
                                "user", "pass", file=cookie_file, login=True
                            )
                            with self.assertRaises(
                                requests.exceptions.HTTPError
                            ) as ctx:
                                toloka.searchv2("query")
                            self.assertEqual(
                                ctx.exception.response.status_code,
                                status_code,
                                f"Expected status {status_code}",
                            )


class TestHtmlPropertyHttpErrors(unittest.TestCase):
    """Test that html property propagates HTTP errors."""

    def test_html_raises_on_error_status(self):
        ok_validate = Mock(
            status_code=200,
            url="https://example.test/f50",
            text="ok",
            raise_for_status=Mock(),
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            cookie_file = f"{tmp_dir}/cookies.json"
            with patch.object(Toloka, "toloka_url", "https://example.test"):
                with patch("toloka2python.requests.Session") as SessionMock:
                    session = SessionMock.return_value
                    session.headers = {}
                    session.cookies = requests.cookies.RequestsCookieJar()
                    session.post.return_value = Mock(
                        status_code=200,
                        url="https://example.test/login.php",
                        text="ok",
                        raise_for_status=Mock(),
                    )
                    session.get.side_effect = [
                        ok_validate,
                        make_http_error_response(403, "Forbidden"),
                    ]

                    toloka = Toloka("user", "pass", file=cookie_file, login=True)
                    with self.assertRaises(requests.exceptions.HTTPError) as ctx:
                        _ = toloka.html
                    self.assertEqual(ctx.exception.response.status_code, 403)


class TestGetAccountHttpErrors(unittest.TestCase):
    """Test that get_account() propagates HTTP errors."""

    def test_get_account_raises_on_400_404_500(self):
        for status_code in (400, 404, 500):
            with self.subTest(status_code=status_code):
                with tempfile.TemporaryDirectory() as tmp_dir:
                    cookie_file = f"{tmp_dir}/cookies.json"
                    with patch.object(Toloka, "toloka_url", "https://example.test"):
                        with patch("toloka2python.requests.Session") as SessionMock:
                            session = SessionMock.return_value
                            session.headers = {}
                            session.cookies = requests.cookies.RequestsCookieJar()
                            session.post.return_value = Mock(
                                status_code=200,
                                url="https://example.test/login.php",
                                text="ok",
                                raise_for_status=Mock(),
                            )
                            ok_validate = Mock(
                                status_code=200,
                                url="https://example.test/f50",
                                text="ok",
                                raise_for_status=Mock(),
                            )
                            session.get.side_effect = [
                                ok_validate,
                                make_http_error_response(status_code),
                            ]
                            toloka = Toloka(
                                "user", "pass", file=cookie_file, login=True
                            )
                            with self.assertRaises(
                                requests.exceptions.HTTPError
                            ) as ctx:
                                toloka.get_account("https://example.test/u123")
                            self.assertEqual(
                                ctx.exception.response.status_code,
                                status_code,
                            )


class TestGetTorrentHttpErrors(unittest.TestCase):
    """Test that get_torrent() propagates HTTP errors."""

    def test_get_torrent_raises_on_502_503(self):
        for status_code in (502, 503):
            with self.subTest(status_code=status_code):
                ok_validate = Mock(
                    status_code=200,
                    url="https://example.test/f50",
                    text="ok",
                    raise_for_status=Mock(),
                )
                with tempfile.TemporaryDirectory() as tmp_dir:
                    cookie_file = f"{tmp_dir}/cookies.json"
                    with patch.object(Toloka, "toloka_url", "https://example.test"):
                        with patch("toloka2python.requests.Session") as SessionMock:
                            session = SessionMock.return_value
                            session.headers = {}
                            session.cookies = requests.cookies.RequestsCookieJar()
                            session.post.return_value = Mock(
                                status_code=200,
                                url="https://example.test/login.php",
                                text="ok",
                                raise_for_status=Mock(),
                            )
                            session.get.side_effect = [
                                ok_validate,
                                make_http_error_response(
                                    status_code,
                                    "Bad Gateway"
                                    if status_code == 502
                                    else "Service Unavailable",
                                ),
                            ]
                            toloka = Toloka(
                                "user", "pass", file=cookie_file, login=True
                            )
                            with self.assertRaises(
                                requests.exceptions.HTTPError
                            ) as ctx:
                                toloka.get_torrent("https://example.test/t123")
                            self.assertEqual(
                                ctx.exception.response.status_code,
                                status_code,
                            )


class TestDownloadTorrentHttpErrors(unittest.TestCase):
    """Test that download_torrent() propagates HTTP errors."""

    def test_download_torrent_raises_on_error_status(self):
        ok_validate = Mock(
            status_code=200,
            url="https://example.test/f50",
            text="ok",
            raise_for_status=Mock(),
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            cookie_file = f"{tmp_dir}/cookies.json"
            with patch.object(Toloka, "toloka_url", "https://example.test"):
                with patch("toloka2python.requests.Session") as SessionMock:
                    session = SessionMock.return_value
                    session.headers = {}
                    session.cookies = requests.cookies.RequestsCookieJar()
                    session.post.return_value = Mock(
                        status_code=200,
                        url="https://example.test/login.php",
                        text="ok",
                        raise_for_status=Mock(),
                    )
                    session.get.side_effect = [
                        ok_validate,
                        make_http_error_response(404, "Not Found"),
                    ]

                    toloka = Toloka("user", "pass", file=cookie_file, login=True)
                    with self.assertRaises(requests.exceptions.HTTPError) as ctx:
                        toloka.download_torrent("https://example.test/download.torrent")
                    self.assertEqual(ctx.exception.response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
