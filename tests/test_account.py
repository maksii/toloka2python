import unittest
from pathlib import Path

from toloka2python.account import get_account_info

EXAMPLES_DIR = Path(__file__).resolve().parent / "examples"


class TestAccountInfo(unittest.TestCase):
    def test_get_account_info_parses_fields(self):
        account_html = (EXAMPLES_DIR / "auth_profile.html").read_text(encoding="utf-8")
        account = get_account_info(account_html)

        self.assertEqual(account.id, "https://example.test/u000001")
        self.assertEqual(account.avatar, "/assets/hurtom.gif")
        self.assertTrue(account.online)
        self.assertEqual(account.email, "")
        self.assertEqual(account.first_login, "14.08.20")
        self.assertEqual(account.last_login, "31.01.26")
        self.assertEqual(account.messages, 12)
        self.assertEqual(account.releases, 0)
        self.assertEqual(account.thanks, 0)
        self.assertEqual(account.passkey, "FAKEPASSKEY")
        self.assertEqual(len(account.upload_torrent), 2)


if __name__ == "__main__":
    unittest.main()
