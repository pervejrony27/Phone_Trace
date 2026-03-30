"""
PhoneOSINT - Truecaller API Lookup Module
Requires authentication token from truecaller_auth.py
Returns: name, profile picture, carrier, spam score, email, etc.
"""

import requests
import json
import os

try:
    from config import TRUECALLER_TOKEN, REQUEST_TIMEOUT, OUTPUT_DIR
except ImportError:
    TRUECALLER_TOKEN = ""
    REQUEST_TIMEOUT = 15
    OUTPUT_DIR = "reports"


class TruecallerLookup:
    """Lookup phone numbers using Truecaller's search API."""

    SEARCH_URL = "https://search5-noneu.truecaller.com/v2/search"

    # Country code mapping for API
    COUNTRY_CODES = {
        "1": "US", "7": "RU", "20": "EG", "27": "ZA",
        "30": "GR", "31": "NL", "32": "BE", "33": "FR",
        "34": "ES", "36": "HU", "39": "IT", "40": "RO",
        "41": "CH", "43": "AT", "44": "GB", "45": "DK",
        "46": "SE", "47": "NO", "48": "PL", "49": "DE",
        "51": "PE", "52": "MX", "53": "CU", "54": "AR",
        "55": "BR", "56": "CL", "57": "CO", "58": "VE",
        "60": "MY", "61": "AU", "62": "ID", "63": "PH",
        "64": "NZ", "65": "SG", "66": "TH", "81": "JP",
        "82": "KR", "84": "VN", "86": "CN", "90": "TR",
        "91": "IN", "92": "PK", "93": "AF", "94": "LK",
        "95": "MM", "98": "IR", "212": "MA", "213": "DZ",
        "216": "TN", "218": "LY", "220": "GM", "221": "SN",
        "234": "NG", "249": "SD", "251": "ET", "252": "SO",
        "254": "KE", "255": "TZ", "256": "UG", "260": "ZM",
        "263": "ZW", "353": "IE", "354": "IS", "358": "FI",
        "370": "LT", "371": "LV", "372": "EE", "380": "UA",
        "420": "CZ", "421": "SK", "852": "HK", "853": "MO",
        "855": "KH", "856": "LA", "880": "BD", "886": "TW",
        "960": "MV", "961": "LB", "962": "JO", "963": "SY",
        "964": "IQ", "965": "KW", "966": "SA", "967": "YE",
        "968": "OM", "971": "AE", "972": "IL", "973": "BH",
        "974": "QA", "977": "NP", "992": "TJ", "993": "TM",
        "994": "AZ", "995": "GE", "996": "KG", "998": "UZ",
    }

    def __init__(self, phone_number: str, token: str = None):
        self.phone_number = (
            phone_number.replace(" ", "").replace("-", "")
        )
        self.token = token or TRUECALLER_TOKEN or self._load_token()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "Truecaller/13.16.6 (Android;13)",
        }

    def _load_token(self) -> str:
        """Load token from saved credentials file."""
        creds_file = "truecaller_creds.json"
        if os.path.exists(creds_file):
            try:
                with open(creds_file, "r") as f:
                    creds = json.load(f)
                    return creds.get("token", "") or creds.get(
                        "installationId", ""
                    )
            except Exception:
                pass
        return ""

    def search(self) -> dict:
        """Main search — returns full Truecaller data."""
        result = {
            "platform": "Truecaller",
            "phone": self.phone_number,
            "found": False,
            "name": None,
            "first_name": None,
            "last_name": None,
            "gender": None,
            "email": None,
            "city": None,
            "carrier": None,
            "spam_score": None,
            "spam_type": None,
            "is_spammer": False,
            "profile_picture": None,
            "about": None,
            "job_title": None,
            "company": None,
            "address": None,
            "country": None,
            "number_type": None,
            "internet_addresses": [],
            "social_profiles": [],
        }

        if not self.token:
            result["error"] = (
                "No authentication token found. "
                "Run: python truecaller_auth.py"
            )
            return result

        try:
            phone = self.phone_number.lstrip("+")

            params = {
                "q": phone,
                "countryCode": self._detect_country_code(),
                "type": 4,
                "locAddr": "",
                "placement": "SEARCHRESULTS,HISTORY,DETAILS",
                "encoding": "json",
            }

            response = requests.get(
                self.SEARCH_URL,
                params=params,
                headers=self.headers,
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code == 200:
                data = response.json()
                result = self._parse_response(data, result)

            elif response.status_code == 401:
                result["error"] = (
                    "Authentication expired. "
                    "Re-run: python truecaller_auth.py"
                )
            elif response.status_code == 429:
                result["error"] = "Rate limited. Try again later."
            else:
                result["error"] = (
                    f"HTTP {response.status_code}: "
                    f"{response.text[:200]}"
                )

        except requests.exceptions.Timeout:
            result["error"] = "Request timed out"
        except requests.exceptions.ConnectionError:
            result["error"] = "Connection failed"
        except Exception as e:
            result["error"] = str(e)

        return result

    def _parse_response(self, data: dict, result: dict) -> dict:
        """Parse Truecaller API response into clean format."""
        results_data = data.get("data", [])

        if not results_data:
            result["found"] = False
            return result

        entry = results_data[0]
        result["found"] = True

        # Name
        name_info = entry.get("name", "")
        if isinstance(name_info, str):
            result["name"] = name_info
            parts = name_info.split(" ", 1)
            result["first_name"] = parts[0] if parts else ""
            result["last_name"] = parts[1] if len(parts) > 1 else ""
        elif isinstance(name_info, dict):
            result["first_name"] = name_info.get("first", "")
            result["last_name"] = name_info.get("last", "")
            result["name"] = (
                f"{result['first_name']} {result['last_name']}".strip()
            )

        # Gender
        result["gender"] = entry.get("gender", "Unknown")

        # Phone info
        phones = entry.get("phones", [])
        if phones:
            phone_data = phones[0]
            result["carrier"] = phone_data.get("carrier", "")
            result["number_type"] = phone_data.get("numberType", "")
            result["country"] = phone_data.get("countryCode", "")
            result["e164_format"] = phone_data.get("e164Format", "")
            result["national_format"] = phone_data.get(
                "nationalFormat", ""
            )

        # Addresses
        addresses = entry.get("addresses", [])
        if addresses:
            addr = addresses[0]
            result["city"] = addr.get("city", "")
            result["country"] = addr.get(
                "countryCode", result.get("country", "")
            )
            city = addr.get("city", "")
            cc = addr.get("countryCode", "")
            result["address"] = f"{city}, {cc}" if city else cc
            result["timezone"] = addr.get("timeZone", "")

        # Email / Internet addresses
        internet_addresses = entry.get("internetAddresses", [])
        if internet_addresses:
            result["internet_addresses"] = internet_addresses
            for ia in internet_addresses:
                if ia.get("service", "").lower() == "email":
                    result["email"] = ia.get("id", "")

        # Profile picture
        result["profile_picture"] = entry.get("image", "")

        # Spam info
        spam_info = entry.get("spamInfo", {})
        if spam_info:
            result["spam_score"] = spam_info.get("spamScore", 0)
            result["spam_type"] = spam_info.get("spamType", "")
            result["is_spammer"] = spam_info.get("spamScore", 0) > 5

        # Job / Company
        result["job_title"] = entry.get("jobTitle", "")
        result["company"] = entry.get("companyName", "")

        # About / Bio
        result["about"] = entry.get("about", "")

        # Social profiles
        social = entry.get("socialMediaProfiles", [])
        if social:
            result["social_profiles"] = social

        # Tags
        tags = entry.get("tags", [])
        if tags:
            result["tags"] = tags

        return result

    def _detect_country_code(self) -> str:
        """Detect 2-letter country code from phone number."""
        phone = self.phone_number.lstrip("+")
        for length in [3, 2, 1]:
            prefix = phone[:length]
            if prefix in self.COUNTRY_CODES:
                return self.COUNTRY_CODES[prefix]
        return "US"

    def download_profile_picture(self, output_dir: str = None) -> str:
        """Download profile picture if available."""
        output_dir = output_dir or OUTPUT_DIR

        result = self.search()
        pic_url = result.get("profile_picture")
        if not pic_url:
            return None

        try:
            os.makedirs(output_dir, exist_ok=True)
            clean_num = (
                self.phone_number.replace("+", "").replace(" ", "")
            )
            filename = os.path.join(
                output_dir, f"truecaller_{clean_num}.jpg"
            )

            response = requests.get(pic_url, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(response.content)
                return filename
        except Exception:
            pass

        return None

    def get_summary(self) -> str:
        """Get a human-readable text summary."""
        data = self.search()

        if not data.get("found"):
            return f"No Truecaller data found for {self.phone_number}"

        lines = [
            "",
            "  ╔══ Truecaller Results ══════════════════════╗",
            f"  ║ Name        : {data.get('name', 'N/A'):<30}║",
            f"  ║ Gender      : {data.get('gender', 'N/A'):<30}║",
            f"  ║ Carrier     : {data.get('carrier', 'N/A'):<30}║",
            f"  ║ City        : {data.get('city', 'N/A'):<30}║",
            f"  ║ Country     : {data.get('country', 'N/A'):<30}║",
            f"  ║ Email       : {data.get('email', 'N/A'):<30}║",
            f"  ║ Job Title   : {data.get('job_title', 'N/A'):<30}║",
            f"  ║ Company     : {data.get('company', 'N/A'):<30}║",
            f"  ║ Spam Score  : {str(data.get('spam_score', 'N/A')):<30}║",
            f"  ║ Profile Pic : {'Yes' if data.get('profile_picture') else 'No':<30}║",
            "  ╚═════════════════════════════════════════════╝",
        ]

        return "\n".join(lines)