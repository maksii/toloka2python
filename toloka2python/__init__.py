import os
import json
import logging
import re
import requests

from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from datetime import datetime
from toloka2python.models.torrent import TorrentElement, Torrent, TorrentFile
from toloka2python.account import get_account_info
from toloka2python.version import __version__

__all__ = [
    "__version__",
    "Toloka",
    "Torrent",
    "TorrentElement",
    "TorrentFile",
    "get_account_info",
]

logger = logging.getLogger(__name__)

class Toloka:
    """Class for interacting with the torrent tracker Toloka"""

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }

    toloka_url = "https://toloka.to"
    cookie_file = "cookie.txt"
    max_login_attempts = 2  # Limit to prevent infinite login attempts

    def __init__(
        self,
        username: str,
        password: str,
        ssl="on",
        file: str = None,
        login: bool = True,
    ):
        """Initialize the Toloka client.

        Set login=False to defer network authentication until login() is called.
        """
        self.username = username
        self.password = password
        self.ssl = ssl
        self.file = file or self.cookie_file
        self.session = requests.Session()
        self.session.headers = self.headers
        self.login_attempts = 0

        if login:
            self.login()

    def login(self):
        """Handle login and session management."""
        if not os.path.exists(self.file):
            logger.info("No cookie file found. Logging in.")
            self.perform_login()
        else:
            logger.info("Loading cookies from file.")
            if not self.load_cookies():
                logger.info("Cookie loading failed or expired, re-logging in.")
                self.perform_login()

    def perform_login(self):
        """Perform login to the site and save cookies."""
        self.login_attempts += 1
        try:
            response = self.session.post(
                f"{self.toloka_url}/login.php",
                {
                    "username": self.username,
                    "password": self.password,
                    "autologin": "on",
                    "ssl": self.ssl,
                    "login": "Вхід",
                },
            )
            response.raise_for_status()  # Check if the request was successful
            if self.validate_cookies():
                self.save_cookies()
                self.login_attempts = 0  # Reset login attempts after successful login
            else:
                if self.login_attempts < self.max_login_attempts:
                    logger.info("Initial cookie validation failed, trying again.")
                    os.remove(self.file)
                    self.session.cookies.clear()  # Clear session cookies before retry
                    self.perform_login()  # Retry login
                else:
                    logger.error("Maximum login attempts reached, raising exception.")
                    raise Exception("Failed to validate cookies after maximum retries.")
        except RequestException as e:
            logger.error(f"Failed to login: {e}")
            raise

    def load_cookies(self):
        """Load cookies from a local file and check if they are still valid."""
        try:
            with open(self.file, "r", encoding="utf-8") as f:
                cookies = json.load(f)
                self.session.cookies.update(requests.utils.cookiejar_from_dict(cookies))
            return self.validate_cookies()
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error loading cookies: {e}")
            return False

    def validate_cookies(self):
        """Validate the cookies by checking if a protected page can be accessed."""
        check_url = f"{self.toloka_url}/f50"
        response = self.session.get(check_url)
        response.raise_for_status()
        if "login.php?redirect=viewforum.php" in response.url:
            logger.info("Cookies are invalid or expired.")
            return False
        logger.info("Cookies are valid.")
        return True

    def save_cookies(self):
        """Save cookies to a local file."""
        try:
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump(requests.utils.dict_from_cookiejar(self.session.cookies), f)
        except IOError as e:
            logger.error(f"Failed to save cookies: {e}")

    def search(self, nm):
        """Пошук торрентів за запитом"""
        result = self.session.get(
            f"{self.toloka_url}/tracker.php?nm={nm}&pn=&send=Пошук"
        )
        result.raise_for_status()
        torrent_list = []
        soup = BeautifulSoup(result.text, "html.parser")
        for torrent in soup.find_all("tr", class_=["prow1", "prow2"]):
            torrent = torrent.find_all("td")

            input_date = torrent[12].text
            parsed_date = datetime.strptime(input_date, "%Y-%m-%d")
            output_date = parsed_date.strftime("%y-%m-%d %H:%M")

            torrent_list.append(
                TorrentElement(
                    forum=torrent[1].text,
                    forum_url=torrent[1].find("a", class_="gen")["href"],
                    url=torrent[2].find("a")["href"],
                    name=torrent[2].text,
                    author=torrent[3].text,
                    verify=True if torrent[4].text == "+" else False,
                    torrent_url=torrent[5].find("a")["href"],
                    size=torrent[6].text,
                    status=torrent[7]["title"],
                    seeders=torrent[9].text,
                    leechers=torrent[10].text,
                    answers=torrent[11].text,
                    date=output_date,
                )
            )
        return torrent_list

    def searchv2(self, nm):
        """Пошук торрентів за запитом в API"""
        result = self.session.get(f"{self.toloka_url}/api.php?search={nm}")
        result.raise_for_status()
        torrent_list = []

        data = result.json()

        torrent_list = []
        for item in data:
            torrent_element = TorrentElement(
                forum=item["forum_name"],
                forum_url=item["forum_parent"],
                url=item["link"],
                name=item["title"],
                author="",
                verify=False,
                torrent_url="",
                size=item["size"],
                status="",
                seeders=int(item["seeders"]),
                leechers=int(item["leechers"]),
                answers=int(item["comments"]),
                date="",
            )
            torrent_list.append(torrent_element)

        return torrent_list

    @property
    def html(self):
        """Отримати HTML головної сторінки"""
        response = self.session.get(self.toloka_url)
        response.raise_for_status()
        return response

    @property
    def me(self):
        """Отримати інформацію про себе"""
        # Get main page for get account url
        soup = BeautifulSoup(self.html.text, "html.parser")

        # Get request to account url
        profile_href = soup.find("a", string="Профіль")["href"]
        profile_url = (
            profile_href
            if profile_href.startswith("http")
            else f"{self.toloka_url}/{profile_href}"
        )
        profile_resp = self.session.get(profile_url)
        profile_resp.raise_for_status()
        return get_account_info(profile_resp.text)

    def get_account(self, url: str):
        """Отримати інформацію про користувача за посиланням"""
        resp = self.session.get(url)
        resp.raise_for_status()
        return get_account_info(resp.text)

    def get_torrent(self, url):
        """Отримати інформацію про торрент за посиланням"""
        resp = self.session.get(url + "?spmode=full&dl=names#torrent")
        resp.raise_for_status()
        content = resp.text
        # Remove extra whitespace, newline, and tab characters using regular expressions
        cleaned_content = re.sub(r"[\n\t]+", "", content)
        soup = BeautifulSoup(cleaned_content, "html.parser")
        if soup.find(string=re.compile("Такої теми чи такого повідомлення не існує")):
            raise ValueError("Torrent topic not found or inaccessible.")

        description = ""
        try:
            # TBD baseline for description of quality and content
            # format somehow?
            start_text = "Відео:"
            end_text = "MediaInfo"

            # Extract entire text from HTML
            text = soup.get_text()

            # Find start and end index
            start_idx = text.find(start_text)
            end_idx = text.find(end_text, start_idx)

            # Extract the relevant part
            data = text[start_idx:end_idx].strip()

            # Replace multiple whitespaces with a single space
            description = " ".join(data.split())
        except Exception as e:
            description = e

        maintitle = soup.find("a", class_="maintitle")
        if not maintitle:
            raise ValueError("Torrent page is missing expected title data.")

        name = maintitle.text
        url = maintitle["href"].replace("/", "")
        forum = soup.select_one("td[class='nav'] h2:nth-of-type(2) a").text
        forum_url = soup.select_one("td[class='nav'] h2:nth-of-type(2) a")[
            "href"
        ].replace("f", "tracker.php?f=")

        author = "Anonymous"
        author_tag = soup.select_one("span.name")
        if author_tag:
            author_text = author_tag.get_text(strip=True).replace("\xa0", " ").strip()
            if author_text:
                author = author_text
        thumb = soup.select_one("[rel=image_src]")["href"]
        img = soup.find("img", attrs={"alt": name})
        img_alt = soup.select_one(".postbody > [align=center] img")
        img = (
            img.get("src")
            if img
            else f"https:{img_alt.get('src')}" if img_alt else None
        )

        torrent_name = soup.find("tr", class_="row6_to").text
        registered_cell = soup.find("td", string=re.compile(r"Зареєстрований"))
        registered_date = (
            registered_cell.find_next("td").get_text(strip=True).lstrip("-")
            if registered_cell
            else ""
        )
        size = (
            soup.find("td", string=" Розмір: ")
            .find_next("span")
            .contents[0]
            .replace("\xa0", "")
        )
        thanks = soup.find("td", string=" Подякували: ").find_next("span").contents[0]
        rating = soup.find("span", attrs={"itemprop": "ratingValue"}).text
        torrent_url = soup.find("a", string="Завантажити")["href"]

        torrent_files = []
        torrent_files_table = soup.select(".files-wrap tr")
        folder_name = None
        rows_to_parse = torrent_files_table
        if torrent_files_table:
            first_row = torrent_files_table[0]
            first_cell = first_row.find("td")
            first_cell_text = first_cell.get_text(strip=True) if first_cell else ""
            if "Папка" in first_cell_text:
                folder_cell = first_row.select_one("td[align=left]")
                folder_name = folder_cell.get_text(strip=True) if folder_cell else None
                rows_to_parse = torrent_files_table[1:]

        for row in rows_to_parse:
            td_elements = row.find_all("td")
            if len(td_elements) >= 3:  # Ensure there are enough columns in this row
                name_align = td_elements[1].get("align")
                row_file_name = (
                    td_elements[1].get_text(strip=True)
                    if name_align in (None, "left")
                    else ""
                )
                size_align = td_elements[2].get("align")
                row_size = (
                    td_elements[2].get_text(strip=True).replace("\xa0", " ")
                    if size_align in (None, "right")
                    else ""
                )
                if (
                    row_file_name and row_size
                ):  # Make sure file_name and size are not empty
                    torrent_file = TorrentFile(folder_name, row_file_name, row_size)
                    torrent_files.append(torrent_file)

        return Torrent(
            forum=forum,
            forum_url=forum_url,
            author=author,
            name=name,
            url=url,
            img=img,
            thumbnail=thumb,
            torrent_name=torrent_name.replace("\xa0", " ").replace("\n", "")[1:-1],
            date=registered_date,
            size=size,
            thanks=int(thanks),
            rating=rating,
            torrent_url=torrent_url,
            files=torrent_files,
            description=description,
        )

    def download_torrent(self, torrent_url: str):
        resp = self.session.get(torrent_url)
        resp.raise_for_status()
        return resp.content
