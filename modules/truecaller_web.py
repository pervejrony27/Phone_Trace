"""
PhoneOSINT - Truecaller Web Scraping Module
Works WITHOUT API token (limited results).
Scrapes Truecaller's public web search page.
"""

import requests
import json
from bs4 import BeautifulSoup

try:
    from config import USER_AGENT, REQUEST_TIMEOUT
except ImportError:
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    REQUEST_TIMEOUT = 15


class TruecallerWeb:
    """Scrape Truecaller's public web search page (no auth needed)."""

    # Country slug mapping for Truecaller URLs
    COUNTRY_SLUGS = {
        "1": "us", "44": "gb", "91": "in", "92": "pk",
        "880": "bd", "971": "ae", "966": "sa", "974": "qa",
        "965": "kw", "968": "om", "973": "bh", "962": "jo",
        "961": "lb", "20": "eg", "234": "ng", "254": "ke",
        "27": "za", "55": "br", "49": "de", "33": "fr",
        "39": "it", "34": "es", "81": "jp", "82": "kr",
        "86": "cn", "62": "id", "60": "my", "63": "ph",
        "66": "th", "84": "vn", "7": "ru", "380": "ua",
        "90": "tr", "48": "pl", "31": "nl", "61": "au",
    }

    def __init__(self, phone_number: str):
        self.phone_number = (
            phone_number.replace(" ", "").replace("-", "")
        )
        self.clean_number = self.phone_number.lstrip("+")

    def search(self) -> dict:
        """Search Truecaller via web scraping."""
        result = {
            "platform": "Truecaller (Web)",
            "phone": self.phone_number,
            "found": False,
            "name": None,
            "search_url": None,
            "profile_picture": None,
            "description": None,
        }

        country = self._detect_country_slug()
        result["search_url"] = (
            f"https://www.truecaller.com/search/"
            f"{country}/{self.clean_number}"
        )

        try:
            headers = {
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.truecaller.com/",
                "Connection": "keep-alive",
            }

            response = requests.get(
                result["search_url"],
                headers=headers,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                # Method 1: OpenGraph meta tags
                og_title = soup.find("meta", property="og:title")
                if og_title:
                    title = og_title.get("content", "")
                    if title and "truecaller" not in title.lower():
                        name = title.split("-")[0].strip()
                        if name and name != self.clean_number:
                            result["name"] = name
                            result["found"] = True

                og_desc = soup.find(
                    "meta", property="og:description"
                )
                if og_desc:
                    result["description"] = og_desc.get(
                        "content", ""
                    )

                og_image = soup.find("meta", property="og:image")
                if og_image:
                    img_url = og_image.get("content", "")
                    if img_url and "truecaller" in img_url:
                        result["profile_picture"] = img_url

                # Method 2: Next.js __NEXT_DATA__
                next_script = soup.find(
                    "script", id="__NEXT_DATA__"
                )
                if next_script and next_script.string:
                    try:
                        next_data = json.loads(next_script.string)
                        props = next_data.get("props", {}).get(
                            "pageProps", {}
                        )
                        if "data" in props:
                            user_data = props["data"]
                            result["found"] = True
                            result["name"] = user_data.get(
                                "name", result["name"]
                            )
                            result["profile_picture"] = user_data.get(
                                "image", result["profile_picture"]
                            )
                            result["carrier"] = user_data.get(
                                "carrier", ""
                            )
                            result["country"] = user_data.get(
                                "countryCode", ""
                            )
                    except (json.JSONDecodeError, KeyError):
                        pass

                # Method 3: JSON-LD structured data
                ld_scripts = soup.find_all(
                    "script", type="application/ld+json"
                )
                for script in ld_scripts:
                    try:
                        if script.string:
                            ld_data = json.loads(script.string)
                            if isinstance(ld_data, dict):
                                if ld_data.get("name"):
                                    result["name"] = ld_data["name"]
                                    result["found"] = True
                    except (json.JSONDecodeError, KeyError):
                        pass

            elif response.status_code == 404:
                result["found"] = False
                result["note"] = "Not found in Truecaller database"

        except requests.exceptions.Timeout:
            result["error"] = "Request timed out"
        except requests.exceptions.ConnectionError:
            result["error"] = "Connection failed"
        except Exception as e:
            result["error"] = str(e)

        return result

    def _detect_country_slug(self) -> str:
        """Get country slug for Truecaller URL."""
        phone = self.clean_number
        for length in [3, 2, 1]:
            prefix = phone[:length]
            if prefix in self.COUNTRY_SLUGS:
                return self.COUNTRY_SLUGS[prefix]
        return "in"