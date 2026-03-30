"""
PhoneOSINT - WhatsApp Lookup Module
Checks if a phone number is registered on WhatsApp.
"""

import requests

try:
    from config import USER_AGENT, REQUEST_TIMEOUT
except ImportError:
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    REQUEST_TIMEOUT = 15


class WhatsAppLookup:
    """Check if a phone number is registered on WhatsApp."""

    def __init__(self, phone_number: str):
        self.phone_number = (
            phone_number.replace("+", "")
            .replace(" ", "")
            .replace("-", "")
        )

    def check(self) -> dict:
        """Run WhatsApp lookup and return results."""
        result = {
            "platform": "WhatsApp",
            "phone": self.phone_number,
            "exists": None,
            "profile_pic": None,
            "chat_link": f"https://wa.me/{self.phone_number}",
            "api_link": f"https://api.whatsapp.com/send?phone={self.phone_number}",
        }

        # Method 1: wa.me link check
        result["exists"] = self._check_wa_link()

        # Method 2: API link fallback
        if result["exists"] is None:
            result["exists"] = self._check_api_link()

        return result

    def _check_wa_link(self) -> bool:
        """Check if wa.me link is valid."""
        try:
            headers = {"User-Agent": USER_AGENT}
            response = requests.head(
                f"https://wa.me/{self.phone_number}",
                headers=headers,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
            )
            if response.status_code == 200:
                return True
            return None
        except Exception:
            return None

    def _check_api_link(self) -> bool:
        """Check WhatsApp API link as fallback."""
        try:
            headers = {"User-Agent": USER_AGENT}
            response = requests.get(
                f"https://api.whatsapp.com/send?phone={self.phone_number}",
                headers=headers,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
            )
            if response.status_code == 200:
                if "invalid" in response.text.lower():
                    return False
                return True
            return None
        except Exception:
            return None