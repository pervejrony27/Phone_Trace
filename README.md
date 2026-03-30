# 📱 PhoneOSINT

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Linux%20|%20Windows%20|%20macOS-lightgrey?style=for-the-badge)

> Advanced Phone Number OSINT Tool — Find name, profile picture, social media 
> accounts (WhatsApp, Telegram, Facebook, Instagram), Truecaller data, carrier 
> info, spam score and publicly available information using just a phone number.

---

## ⚠️ Legal Disclaimer

This tool is for **educational and authorized security research only**.

- Only collects **publicly available** information
- Respect privacy laws (GDPR, CCPA, etc.)
- **Do NOT** use for stalking, harassment, or illegal purposes
- Check Terms of Service of each platform
- Get proper authorization before scanning numbers you don't own
- The developers are **not responsible** for misuse

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/pervejrony27PhoneOSINT.git
cd PhoneOSINT

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Setup configuration
cp config.example.py config.py
# Edit config.py with your API keys