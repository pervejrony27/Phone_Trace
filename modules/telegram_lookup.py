"""
PhoneOSINT - Telegram Lookup Module
Uses Telethon to check if a phone number is on Telegram.
Retrieves username, name, profile picture, and bio.
Requires Telegram API credentials in config.py
"""

import asyncio
import os

try:
    from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, OUTPUT_DIR
except ImportError:
    TELEGRAM_API_ID = ""
    TELEGRAM_API_HASH = ""
    OUTPUT_DIR = "reports"


class TelegramLookup:
    """Lookup phone number on Telegram using Telethon."""

    def __init__(self, phone_number: str):
        self.phone_number = phone_number
        self.client = None

    async def _lookup(self) -> dict:
        """Async Telegram lookup function."""
        result = {
            "platform": "Telegram",
            "phone": self.phone_number,
            "exists": False,
            "username": None,
            "first_name": None,
            "last_name": None,
            "user_id": None,
            "profile_pic": None,
            "profile_link": None,
            "bio": None,
            "is_bot": None,
            "is_verified": None,
            "is_premium": None,
        }

        if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
            result["error"] = (
                "Telegram API credentials not configured. "
                "Set TELEGRAM_API_ID and TELEGRAM_API_HASH in config.py"
            )
            return result

        try:
            from telethon import TelegramClient
            from telethon.tl.functions.contacts import (
                ImportContactsRequest,
                DeleteContactsRequest,
            )
            from telethon.tl.types import InputPhoneContact
        except ImportError:
            result["error"] = "Telethon not installed. Run: pip install telethon"
            return result

        try:
            self.client = TelegramClient(
                "session",
                int(TELEGRAM_API_ID),
                TELEGRAM_API_HASH,
            )
            await self.client.connect()

            if not await self.client.is_user_authorized():
                phone = input(
                    "[Telegram] Enter YOUR phone number for auth: "
                )
                await self.client.send_code_request(phone)
                code = input("[Telegram] Enter the code you received: ")
                try:
                    await self.client.sign_in(phone, code)
                except Exception:
                    password = input("[Telegram] Enter 2FA password: ")
                    await self.client.sign_in(password=password)

            # Import contact temporarily to check
            contact = InputPhoneContact(
                client_id=0,
                phone=self.phone_number,
                first_name="Lookup",
                last_name="User",
            )
            contacts = await self.client(ImportContactsRequest([contact]))

            if contacts.users:
                user = contacts.users[0]
                result["exists"] = True
                result["username"] = user.username
                result["first_name"] = user.first_name
                result["last_name"] = user.last_name
                result["user_id"] = user.id
                result["is_bot"] = getattr(user, "bot", None)
                result["is_verified"] = getattr(user, "verified", None)
                result["is_premium"] = getattr(user, "premium", None)

                if user.username:
                    result["profile_link"] = f"https://t.me/{user.username}"

                # Download profile photo
                try:
                    os.makedirs(OUTPUT_DIR, exist_ok=True)
                    photo_path = await self.client.download_profile_photo(
                        user,
                        file=os.path.join(
                            OUTPUT_DIR, f"telegram_{user.id}.jpg"
                        ),
                    )
                    if photo_path:
                        result["profile_pic"] = str(photo_path)
                except Exception:
                    pass

                # Get bio/about
                try:
                    from telethon.tl.functions.users import GetFullUserRequest

                    full_user = await self.client(GetFullUserRequest(user))
                    if full_user and full_user.full_user:
                        result["bio"] = full_user.full_user.about
                except Exception:
                    pass

                # Clean up imported contact
                try:
                    await self.client(DeleteContactsRequest(id=[user.id]))
                except Exception:
                    pass

        except Exception as e:
            result["error"] = str(e)
        finally:
            if self.client and self.client.is_connected():
                await self.client.disconnect()

        return result

    def check(self) -> dict:
        """Synchronous wrapper for the async lookup."""
        try:
            import nest_asyncio
            nest_asyncio.apply()
        except ImportError:
            pass

        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self._lookup())