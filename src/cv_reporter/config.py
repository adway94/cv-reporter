import os
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY = os.environ["NVIDIA_API_KEY"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
DATABASE_URL = os.environ["DATABASE_URL"]

NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "moonshotai/kimi-k2-instruct")

TIMEZONE = os.getenv("TIMEZONE", "America/Argentina/Buenos_Aires")
