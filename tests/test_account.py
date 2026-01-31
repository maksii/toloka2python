import unittest

from toloka2python.account import get_account_info


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


class TestAccountInfo(unittest.TestCase):
    def test_get_account_info_parses_fields(self):
        account = get_account_info(ACCOUNT_HTML)

        self.assertEqual(account.id, "u123456")
        self.assertEqual(account.avatar, "avatar.png")
        self.assertTrue(account.online)
        self.assertEqual(account.email, "user@example.com")
        self.assertEqual(account.first_login, "2023-01-01")
        self.assertEqual(account.last_login, "2023-02-01")
        self.assertEqual(account.messages, 5)
        self.assertEqual(account.releases, 3)
        self.assertEqual(account.thanks, 7)
        self.assertEqual(account.passkey, "passkey123")
        self.assertEqual(len(account.upload_torrent), 0)


if __name__ == "__main__":
    unittest.main()
