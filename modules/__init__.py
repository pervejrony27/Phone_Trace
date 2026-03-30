"""
PhoneOSINT - Modules Package
Each module handles lookup for a specific platform.
"""

__version__ = "1.0.0"
__author__ = "PhoneOSINT"

from .phone_info import PhoneInfo
from .whatsapp_lookup import WhatsAppLookup
from .telegram_lookup import TelegramLookup
from .facebook_lookup import FacebookLookup
from .instagram_lookup import InstagramLookup
from .truecaller_lookup import TruecallerLookup
from .truecaller_web import TruecallerWeb
from .social_scan import SocialScan
from .google_dork import GoogleDork
from .report_generator import ReportGenerator

__all__ = [
    "PhoneInfo",
    "WhatsAppLookup",
    "TelegramLookup",
    "FacebookLookup",
    "InstagramLookup",
    "TruecallerLookup",
    "TruecallerWeb",
    "SocialScan",
    "GoogleDork",
    "ReportGenerator",
]