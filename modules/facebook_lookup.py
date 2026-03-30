"""
PhoneOSINT - Facebook Lookup Module
Checks if a phone number is linked to a Facebook account
using Facebook's account recovery page.
"""

import requests
from bs4 import BeautifulSoup

try:
    from config import USER_AGENT, REQUEST_TIMEOUT
except ImportError:
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    REQUEST_TIMEOUT = 15


class FacebookLookup:
    """Check if a phone number is associated with a Facebook account."""

    def __init__(self, phone_number: str):
        self.phone_number = phone_number

    def check(self) -> dict:
        """Run Facebook lookup and return results."""
        result = {
            "platform": "Facebook",
            "phone": self.phone_number,
            "exists": None,
            "profile_url": None,
            "name": None,
            "profile_pic": None,
            "search_url": (
                f"https://www.facebook.com/search/people/"
                f"?q={self.phone_number}"
            ),
        }

        # Check via password reset page
        reset_check = self._check_password_reset()
        result.update(reset_check)

        return result

    def _check_password_reset(self) -> dict:
        """
        Check Facebook's 'Find Your Account' page to see
        if a phone number is linked to any account.
        """
        info = {"exists": None}

        try:
            session = requests.Session()
            headers = {
                "User-Agent": USER_AGENT,
                "Accept": (
                    "text/html,application/xhtml+xml,"
                    "application/xml;q=0.9,*/*;q=0.8"
                ),
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            }

            # Step 1: Load the identify page to get form tokens
            url = "https://www.facebook.com/login/identify/"
            response = session.get(
                url, headers=headers, timeout=REQUEST_TIMEOUT
            )

            if response.status_code != 200:
                info["error"] = (
                    f"Could not access Facebook "
                    f"(HTTP {response.status_code})"
                )
                return info

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract hidden form tokens
            lsd = soup.find("input", {"name": "lsd"})
            jazoest = soup.find("input", {"name": "jazoest"})
            li = soup.find("input", {"name": "li"})

            if not lsd:
                info["error"] = "Could not extract Facebook form tokens"
                return info

            # Step 2: Submit the phone number
            data = {
                "lsd": lsd["value"] if lsd else "",
                "jazoest": jazoest["value"] if jazoest else "",
                "li": li["value"] if li else "",
                "email": self.phone_number,
                "did_submit": "Search",
            }

            response = session.post(
                "https://www.facebook.com/login/identify/",
                headers=headers,
                data=data,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
            )

            # Step 3: Analyze the response
            final_url = response.url
            response_text = response.text

            if "recover" in final_url or "reset" in final_url:
                info["exists"] = True

                soup = BeautifulSoup(response_text, "html.parser")

                # Try to extract masked name
                name_elem = soup.find(
                    "div", class_="fsl"
                ) or soup.find("td", class_="fsl")
                if name_elem:
                    info["name"] = name_elem.get_text(strip=True)

                # Try to extract profile picture
                profile_pic = soup.find(
                    "img", class_="img"
                ) or soup.find("img", {"width": "72"})
                if profile_pic:
                    info["profile_pic"] = profile_pic.get("src", "")

            elif "identify" in final_url:
                if (
                    "isn't linked" in response_text
                    or "not find" in response_text
                ):
                    info["exists"] = False
                else:
                    info["exists"] = None
                    info["note"] = (
                        "Could not determine — possible CAPTCHA or rate limit"
                    )
            else:
                info["exists"] = None

        except requests.exceptions.Timeout:
            info["error"] = "Request timed out"
        except requests.exceptions.ConnectionError:
            info["error"] = "Connection failed"
        except Exception as e:
            info["error"] = str(e)

        return info