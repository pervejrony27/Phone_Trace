"""
PhoneOSINT - Phone Number Information Module
Analyzes phone number for carrier, country, timezone, number type.
Uses phonenumbers library and optional NumVerify API.
"""

import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import requests

try:
    from config import NUMVERIFY_API_KEY, REQUEST_TIMEOUT
except ImportError:
    NUMVERIFY_API_KEY = ""
    REQUEST_TIMEOUT = 15


class PhoneInfo:
    """Analyze a phone number for basic information."""

    def __init__(self, phone_number: str):
        self.phone_number = phone_number
        self.parsed = None
        self.info = {}

    def analyze(self) -> dict:
        """Run full phone number analysis and return results dict."""
        try:
            self.parsed = phonenumbers.parse(self.phone_number)
        except phonenumbers.NumberParseException as e:
            return {
                "error": f"Invalid phone number: {e}",
                "valid": False,
            }

        self.info = {
            "number": self.phone_number,
            "valid": phonenumbers.is_valid_number(self.parsed),
            "possible": phonenumbers.is_possible_number(self.parsed),
            "international_format": phonenumbers.format_number(
                self.parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            ),
            "national_format": phonenumbers.format_number(
                self.parsed, phonenumbers.PhoneNumberFormat.NATIONAL
            ),
            "e164_format": phonenumbers.format_number(
                self.parsed, phonenumbers.PhoneNumberFormat.E164
            ),
            "country_code": self.parsed.country_code,
            "national_number": str(self.parsed.national_number),
            "country": geocoder.description_for_number(self.parsed, "en"),
            "carrier": carrier.name_for_number(self.parsed, "en"),
            "timezone": list(timezone.time_zones_for_number(self.parsed)),
            "number_type": self._get_number_type(),
        }

        # Optional NumVerify API lookup
        numverify_data = self._numverify_lookup()
        if numverify_data:
            self.info["numverify"] = numverify_data

        return self.info

    def _get_number_type(self) -> str:
        """Determine the type of phone number."""
        num_type = phonenumbers.number_type(self.parsed)
        types = {
            0: "FIXED_LINE",
            1: "MOBILE",
            2: "FIXED_LINE_OR_MOBILE",
            3: "TOLL_FREE",
            4: "PREMIUM_RATE",
            5: "SHARED_COST",
            6: "VOIP",
            7: "PERSONAL_NUMBER",
            8: "PAGER",
            9: "UAN",
            10: "VOICEMAIL",
            27: "EMERGENCY",
            28: "SHORT_CODE",
            29: "STANDARD_RATE",
        }
        return types.get(num_type, "UNKNOWN")

    def _numverify_lookup(self) -> dict:
        """Query NumVerify API for additional phone data."""
        if not NUMVERIFY_API_KEY:
            return None
        try:
            url = "http://apilayer.net/api/validate"
            params = {
                "access_key": NUMVERIFY_API_KEY,
                "number": self.info.get("e164_format", self.phone_number),
            }
            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                if data.get("valid"):
                    return {
                        "valid": data.get("valid"),
                        "local_format": data.get("local_format"),
                        "international_format": data.get("international_format"),
                        "country_prefix": data.get("country_prefix"),
                        "country_code": data.get("country_code"),
                        "country_name": data.get("country_name"),
                        "location": data.get("location"),
                        "carrier": data.get("carrier"),
                        "line_type": data.get("line_type"),
                    }
        except Exception:
            pass
        return None