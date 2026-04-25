import requests
from cv_reporter.config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID


def send_message(text: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
    }
    response = requests.post(url, json=payload, timeout=15)
    response.raise_for_status()
