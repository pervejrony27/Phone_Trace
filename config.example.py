"""
PhoneOSINT - Configuration Template
════════════════════════════════════

SETUP INSTRUCTIONS:
  1. Copy this file:  cp config.example.py config.py
  2. Fill in your API keys below
  3. NEVER commit config.py to git (it's in .gitignore)

ALTERNATIVE: Use .env file
  1. Create .env file in project root
  2. Add: TELEGRAM_API_ID=your_id
  3. The tool will load from .env automatically
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ============================================
# TELEGRAM API CREDENTIALS
# Get from: https://my.telegram.org/apps
# ============================================
TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID", "")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")

# ============================================
# NUMVERIFY API KEY
# Get from: https://numverify.com/
# Free tier: 100 requests/month
# ============================================
NUMVERIFY_API_KEY = os.getenv("NUMVERIFY_API_KEY", "")

# ============================================
# TRUECALLER
# Token auto-saved by truecaller_auth.py
# Or set manually here / in .env
# ============================================
TRUECALLER_TOKEN = os.getenv("TRUECALLER_TOKEN", "")

# ============================================
# GENERAL SETTINGS
# ============================================
REQUEST_TIMEOUT = 15
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
OUTPUT_DIR = "reports"

# ============================================
# RATE LIMITING
# ============================================
DELAY_BETWEEN_REQUESTS = 2
MAX_RETRIES = 3