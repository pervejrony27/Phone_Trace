"""
PhoneOSINT - Instagram Lookup Module
Checks if a phone number is linked to an Instagram account
using Instagram's account recovery endpoint.
"""

import requests

try:
    from config import USER_AGENT, REQUEST_TIMEOUT
except ImportError:
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    REQUEST_TIMEOUT = 15


class InstagramLookup:
    """Check if a phone number is registered on Instagram."""

    def __init__(self, phone_number: str):
        self.phone_number = phone_number

    def check(self) -> dict:
        """Run Instagram lookup and return results."""
        result = {
            "platform": "Instagram",
            "phone": self.phone_number,
            "exists": None,
            "username": None,
            "profile_url": None,
            "contact_point": None,
        }

        recovery_check = self._check_account_recovery()
        result.update(recovery_check)

        return result

    def _check_account_recovery(self) -> dict:
        """
        Use Instagram's account recovery endpoint to check
        if a phone number is registered.
        """
        info = {}

        try:
            session = requests.Session()
            headers = {
                "User-Agent": USER_AGENT,
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": (
                    "https://www.instagram.com/accounts/password/reset/"
                ),
            }

            # Step 1: Get CSRF token
            session.get(
                "https://www.instagram.com/accounts/password/reset/",
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )

            csrf_token = session.cookies.get("csrftoken", "")

            # Step 2: Submit phone number
            headers.update(
                {
                    "X-CSRFToken": csrf_token,
                    "X-Requested-With": "XMLHttpRequest",
                    "X-Instagram-AJAX": "1",
                    "Content-Type": "application/x-www-form-urlencoded",
                }
            )

            data = {
                "email_or_phone": self.phone_number,
                "recaptcha_challenge_field": "",
                "flow": "",
            }

            response = session.post(
                "https://www.instagram.com/accounts/"
                "account_recovery_send_ajax/",
                headers=headers,
                data=data,
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code == 200:
                try:
                    json_data = response.json()
                    if json_data.get("status") == "ok":
                        info["exists"] = True
                        info["contact_point"] = json_data.get(
                            "contact_point", ""
                        )
                        info["note"] = (
                            "Account found — recovery link sent"
                        )
                    elif json_data.get("status") == "fail":
                        info["exists"] = False
                        info["note"] = json_data.get(
                            "message", "Not found"
                        )
                    else:
                        info["exists"] = None
                except ValueError:
                    info["exists"] = None
                    info["note"] = "Could not parse response"
            else:
                info["exists"] = None
                info["note"] = f"HTTP {response.status_code}"

        except requests.exceptions.Timeout:
            info["error"] = "Request timed out"
        except requests.exceptions.ConnectionError:
            info["error"] = "Connection failed"
        except Exception as e:
            info["error"] = str(e)

        return info