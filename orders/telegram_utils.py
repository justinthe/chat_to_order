import requests
import os

def send_telegram_reply(chat_id, text):
    """
    Sends a message back to the user via Telegram API.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: No TELEGRAM_BOT_TOKEN found in .env")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"  # Allows bolding text with *stars*
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Telegram Send Error: {response.text}")
    except Exception as e:
        print(f"Connection Error: {e}")