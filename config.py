"""
KMS Newsroom v2
Configuration
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

missing = []

if not TELEGRAM_BOT_TOKEN:
    missing.append("TELEGRAM_BOT_TOKEN")

if not OPENAI_API_KEY:
    missing.append("OPENAI_API_KEY")

if missing:
    print("❌ Missing environment variables:\n")
    for item in missing:
        print(f"   - {item}")
    print("\nConfigure them locally in .env or as Railway Variables.")
    sys.exit(1)