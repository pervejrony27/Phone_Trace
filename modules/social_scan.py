"""
PhoneOSINT - Social Scan Module
Checks multiple additional platforms for phone number association.
Generates search URLs and deep links.
"""

try:
    from config import USER_AGENT, REQUEST_TIMEOUT
except ImportError:
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    REQUEST_TIMEOUT = 15


class SocialScan:
    """Check multiple platforms for phone number association."""

    def __init__(self, phone_number: str):
        self.phone_number = (
            phone_number.replace("+", "").replace(" ", "")
        )
        self.raw_number = phone_number

    def check_all(self) -> dict:
        """Run all platform checks and return combined results."""
        results = {}

        checks = {
            "viber": self._check_viber,
            "signal": self._check_signal,
            "skype": self._check_skype,
            "twitter": self._check_twitter,
            "linkedin": self._check_linkedin,
            "tiktok": self._check_tiktok,
            "snapchat": self._check_snapchat,
            "callerid_services": self._check_callerid_apps,
        }

        for platform, check_func in checks.items():
            try:
                results[platform] = check_func()
            except Exception as e:
                results[platform] = {
                    "platform": platform,
                    "error": str(e),
                }

        return results

    def _check_viber(self) -> dict:
        """Check Viber availability."""
        return {
            "platform": "Viber",
            "exists": None,
            "deep_link": (
                f"viber://chat?number=%2B{self.phone_number}"
            ),
            "note": (
                "Open deep link on device with "
                "Viber installed to verify"
            ),
        }

    def _check_signal(self) -> dict:
        """Signal doesn't allow public lookups."""
        return {
            "platform": "Signal",
            "exists": None,
            "note": (
                "Signal does not provide public "
                "number lookup (privacy by design)."
            ),
        }

    def _check_skype(self) -> dict:
        """Check Skype directory."""
        return {
            "platform": "Skype",
            "exists": None,
            "search_url": (
                f"https://www.skype.com/en/directory/"
                f"search/?query={self.phone_number}"
            ),
            "note": "Check search URL manually",
        }

    def _check_twitter(self) -> dict:
        """Check Twitter/X."""
        return {
            "platform": "Twitter/X",
            "exists": None,
            "search_url": (
                f"https://twitter.com/search?"
                f"q={self.raw_number}&src=typed_query"
            ),
            "note": (
                "Twitter removed phone-based lookup. "
                "Try Google dork instead."
            ),
        }

    def _check_linkedin(self) -> dict:
        """Check LinkedIn."""
        return {
            "platform": "LinkedIn",
            "exists": None,
            "search_url": (
                f"https://www.linkedin.com/search/results/"
                f"all/?keywords={self.raw_number}"
            ),
            "google_dork": (
                f'site:linkedin.com "{self.raw_number}"'
            ),
            "note": (
                "LinkedIn doesn't support direct phone "
                "lookup. Use Google dork."
            ),
        }

    def _check_tiktok(self) -> dict:
        """Check TikTok."""
        return {
            "platform": "TikTok",
            "exists": None,
            "search_url": (
                f"https://www.tiktok.com/search?"
                f"q={self.phone_number}"
            ),
            "note": (
                "TikTok doesn't support public phone lookup"
            ),
        }

    def _check_snapchat(self) -> dict:
        """Check Snapchat."""
        return {
            "platform": "Snapchat",
            "exists": None,
            "deep_link": (
                f"snapchat://add/{self.phone_number}"
            ),
            "note": (
                "Snapchat requires the app to "
                "look up by phone number"
            ),
        }

    def _check_callerid_apps(self) -> dict:
        """Generate links for various Caller ID services."""
        return {
            "platform": "Caller ID Services",
            "services": {
                "truecaller": (
                    f"https://www.truecaller.com/search/"
                    f"us/{self.phone_number}"
                ),
                "sync_me": (
                    f"https://sync.me/search/"
                    f"?number=%2B{self.phone_number}"
                ),
                "whocalledme": (
                    f"https://www.whocalledme.com/"
                    f"lookup/{self.phone_number}"
                ),
                "spy_dialer": (
                    f"https://www.spydialer.com/results.aspx?"
                    f"type=cell&q={self.phone_number}"
                ),
                "that_them": (
                    f"https://thatsthem.com/"
                    f"phone/{self.phone_number}"
                ),
                "white_pages": (
                    f"https://www.whitepages.com/"
                    f"phone/{self.phone_number}"
                ),
                "numberguru": (
                    f"https://www.numberguru.com/"
                    f"phone-number/lookup/{self.phone_number}"
                ),
            },
        }