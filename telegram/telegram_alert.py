import os
import requests
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class TelegramBot:
    def __init__(self):
        # Fetch keys securely from environment variables
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not self.bot_token or not self.chat_id:
            print("⚠️ Error: Telegram credentials not found in .env file!")

    def send_msg(self, message):
        """Sends a message to your Telegram via API"""
        if not self.bot_token or not self.chat_id:
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                print(f"⚠️ Telegram Failed: {response.text}")
        except Exception as e:
            print(f"⚠️ Telegram Connection Error: {e}")

# TEST BLOCK: Run this file directly to check if it works
if __name__ == "__main__":
    bot = TelegramBot()
    bot.send_msg("🔐 **Secure Alert:** Keys loaded from .env successfully!")