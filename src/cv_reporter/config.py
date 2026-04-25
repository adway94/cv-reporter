import os
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY = os.environ["NVIDIA_API_KEY"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
DATABASE_URL = os.environ["DATABASE_URL"]

NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "moonshotai/kimi-k2-instruct")

# Hora de cierre del período en horario local (la misma hora a la que corre el reporte)
REPORT_HOUR = int(os.getenv("REPORT_HOUR", "9"))
TIMEZONE = os.getenv("TIMEZONE", "America/Argentina/Buenos_Aires")
