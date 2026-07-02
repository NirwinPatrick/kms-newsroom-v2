"""
KMS Newsroom v2
Configuration Loader
"""

from dotenv import load_dotenv
import os
import sys

# Load .env file
load_dotenv()

# ==========================================================
# REQUIRED ENVIRONMENT VARIABLES
# ==========================================================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ==========================================================
# VALIDATION
# ==========================================================

missing = []

if not TELEGRAM_BOT_TOKEN:
    missing.append("TELEGRAM_BOT_TOKEN")

if not GEMINI_API_KEY:
    missing.append("GEMINI_API_KEY")

if missing:
    print("\n❌ Missing environment variables:")
    for item in missing:
        print(f"   - {item}")

    print("\nCreate a .env file in the project root.\n")
    sys.exit(1)