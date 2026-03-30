#!/usr/bin/env python3
"""
PhoneOSINT - Truecaller Authentication Script
Run this ONCE to get your Truecaller API token.
Token is saved to truecaller_creds.json (gitignored).

Usage:
    python truecaller_auth.py
"""

import requests
import json
import random
import string
import sys


class TruecallerAuth:
    """Authenticate with Truecaller to get API token."""

    BASE_URL = "https://account-asia-south1.truecaller.com/v2"

    def __init__(self):
        self.device_id = self._generate_device_id()
        self.installation_id = None
        self.token = None

    def _generate_device_id(self) -> str:
        """Generate a random device ID."""
        return "".join(
            random.choices(
                string.ascii_lowercase + string.digits, k=16
            )
        )

    def _parse_phone(self, phone_number: str) -> tuple:
        """Parse phone number into dialing code and national number."""
        phone_clean = phone_number.lstrip("+")

        known_codes = [
            "880", "971", "966", "974", "965", "968", "973",
            "962", "961", "234", "254", "353", "372", "380",
            "420", "421", "852", "855", "856", "886", "960",
            "963", "964", "967", "977", "992", "993", "994",
            "995", "996", "998", "212", "213", "216", "218",
            "220", "221", "249", "251", "252", "255", "256",
            "260", "263",
            "91", "92", "93", "94", "95", "98", "20", "27",
            "30", "31", "32", "33", "34", "36", "39", "40",
            "41", "43", "44", "45", "46", "47", "48", "49",
            "51", "52", "53", "54", "55", "56", "57", "58",
            "60", "61", "62", "63", "64", "65", "66", "81",
            "82", "84", "86", "90",
            "1", "7",
        ]

        for code in sorted(known_codes, key=len, reverse=True):
            if phone_clean.startswith(code):
                return code, phone_clean[len(code):]

        return phone_clean[:2], phone_clean[2:]

    def request_otp(self, phone_number: str) -> dict:
        """Request OTP to your phone number."""
        url = f"{self.BASE_URL}/sendOnboardingOtp"

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Truecaller/13.16.6 (Android;13)",
            "clientSecret": "lvc22mp3l1sfv6ujg83rd17btt",
        }

        dialing_code, national_number = self._parse_phone(
            phone_number
        )

        payload = {
            "countryCode": f"+{dialing_code}",
            "dialingCode": int(dialing_code),
            "installationDetails": {
                "app": {
                    "buildVersion": 5,
                    "majorVersion": 13,
                    "minorVersion": 16,
                    "store": "JEEVES",
                },
                "device": {
                    "deviceId": self.device_id,
                    "language": "en",
                    "manufacturer": "Google",
                    "model": "Pixel 6",
                    "osName": "Android",
                    "osVersion": "13",
                    "mobileServices": ["GMS"],
                },
                "language": "en",
            },
            "phoneNumber": national_number,
            "region": "region-2",
            "sequenceNo": 2,
        }

        try:
            response = requests.post(
                url, json=payload, headers=headers, timeout=15
            )
            print(f"[*] OTP Request Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print("[✓] OTP sent successfully!")
                print(
                    f"    Request ID: {data.get('requestId', 'N/A')}"
                )
                return data
            else:
                print(f"[✗] Failed: {response.text}")
                return {"error": response.text}
        except Exception as e:
            print(f"[✗] Error: {e}")
            return {"error": str(e)}

    def verify_otp(
        self, phone_number: str, request_id: str, otp: str
    ) -> dict:
        """Verify OTP and get authentication token."""
        url = f"{self.BASE_URL}/verifyOnboardingOtp"

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Truecaller/13.16.6 (Android;13)",
            "clientSecret": "lvc22mp3l1sfv6ujg83rd17btt",
        }

        dialing_code, national_number = self._parse_phone(
            phone_number
        )

        payload = {
            "countryCode": f"+{dialing_code}",
            "dialingCode": int(dialing_code),
            "phoneNumber": national_number,
            "requestId": request_id,
            "token": otp,
        }

        try:
            response = requests.post(
                url, json=payload, headers=headers, timeout=15
            )

            if response.status_code in [200, 201]:
                data = response.json()
                self.installation_id = data.get(
                    "installationId", ""
                )
                self.token = data.get("token", "")

                print("[✓] Authentication Successful!")
                print(
                    f"    Installation ID: {self.installation_id}"
                )

                creds = {
                    "installationId": self.installation_id,
                    "token": self.token,
                    "phones": data.get("phones", []),
                }

                with open("truecaller_creds.json", "w") as f:
                    json.dump(creds, f, indent=2)

                print(
                    "[✓] Credentials saved to "
                    "truecaller_creds.json"
                )
                print(
                    "    (This file is gitignored — "
                    "it won't be uploaded)"
                )
                return data
            else:
                print(f"[✗] Verification failed: {response.text}")
                return {"error": response.text}
        except Exception as e:
            print(f"[✗] Error: {e}")
            return {"error": str(e)}


def main():
    """Interactive Truecaller authentication setup."""
    print("=" * 55)
    print("  TRUECALLER AUTHENTICATION SETUP")
    print("  This is a one-time setup process.")
    print("  You need a phone number to receive OTP.")
    print("=" * 55)

    auth = TruecallerAuth()

    phone = input(
        "\nEnter YOUR phone number (e.g., +911234567890): "
    ).strip()

    if not phone.startswith("+"):
        phone = "+" + phone

    # Request OTP
    result = auth.request_otp(phone)

    if "error" in result:
        print("\n[!] Failed to send OTP. Please try again.")
        sys.exit(1)

    request_id = result.get("requestId", "")

    if not request_id:
        print("[!] No request ID received. Please try again.")
        sys.exit(1)

    # Get OTP
    otp = input(
        "\nEnter the OTP received on your phone: "
    ).strip()

    # Verify
    verify_result = auth.verify_otp(phone, request_id, otp)

    if "error" not in verify_result:
        print("\n" + "=" * 55)
        print("[✓] Setup complete!")
        print("    You can now use Truecaller lookup.")
        print("    Run: python main.py -n +XXXXXXXXXXXX")
        print("=" * 55)
    else:
        print("\n[!] Setup failed. Please try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()