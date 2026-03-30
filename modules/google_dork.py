"""
PhoneOSINT - Google Dorking Module
Generates Google search queries (dorks) to find
phone number appearances across the internet.
"""

from urllib.parse import quote


class GoogleDork:
    """Generate Google dork queries for phone number OSINT."""

    def __init__(self, phone_number: str):
        self.phone_number = phone_number
        self.formats = self._generate_formats()

    def _generate_formats(self) -> list:
        """Generate different phone number format variations."""
        num = (
            self.phone_number.replace("+", "")
            .replace(" ", "")
            .replace("-", "")
        )
        formats = set()

        formats.add(self.phone_number)
        formats.add(num)
        formats.add(f"+{num}")

        if len(num) >= 10:
            last10 = num[-10:]
            formats.add(
                f"{last10[:3]}-{last10[3:6]}-{last10[6:]}"
            )
            formats.add(
                f"({last10[:3]}) {last10[3:6]}-{last10[6:]}"
            )
            formats.add(
                f"{last10[:3]}.{last10[3:6]}.{last10[6:]}"
            )
            formats.add(
                f"{last10[:3]} {last10[3:6]} {last10[6:]}"
            )

        return list(formats)

    def search(self) -> dict:
        """Generate all dork queries and search URLs."""
        result = {
            "platform": "Google OSINT",
            "phone": self.phone_number,
            "dork_urls": [],
            "social_media_dorks": {},
            "phone_formats": self.formats,
        }

        dorks = {
            "facebook": (
                f'site:facebook.com "{self.phone_number}"'
            ),
            "instagram": (
                f'site:instagram.com "{self.phone_number}"'
            ),
            "linkedin": (
                f'site:linkedin.com "{self.phone_number}"'
            ),
            "twitter": (
                f'site:twitter.com OR site:x.com '
                f'"{self.phone_number}"'
            ),
            "tiktok": (
                f'site:tiktok.com "{self.phone_number}"'
            ),
            "youtube": (
                f'site:youtube.com "{self.phone_number}"'
            ),
            "reddit": (
                f'site:reddit.com "{self.phone_number}"'
            ),
            "github": (
                f'site:github.com "{self.phone_number}"'
            ),
            "general": (
                f'"{self.phone_number}"'
            ),
            "documents": (
                f'"{self.phone_number}" '
                f"filetype:pdf OR filetype:doc OR "
                f"filetype:docx OR filetype:xlsx OR "
                f"filetype:csv"
            ),
            "paste_sites": (
                f'site:pastebin.com OR site:ghostbin.com '
                f'OR site:paste.ee "{self.phone_number}"'
            ),
            "data_leaks": (
                f'"{self.phone_number}" '
                f"leak OR dump OR breach OR database"
            ),
            "forums": (
                f'"{self.phone_number}" '
                f"site:forum.* OR inurl:forum OR inurl:thread"
            ),
            "classified_ads": (
                f'"{self.phone_number}" '
                f"site:craigslist.org OR site:olx.com OR "
                f"site:gumtree.com"
            ),
        }

        for platform, query in dorks.items():
            search_url = (
                f"https://www.google.com/search?q={quote(query)}"
            )
            result["social_media_dorks"][platform] = {
                "query": query,
                "search_url": search_url,
            }

        result["dork_urls"] = [
            d["search_url"]
            for d in result["social_media_dorks"].values()
        ]

        return result