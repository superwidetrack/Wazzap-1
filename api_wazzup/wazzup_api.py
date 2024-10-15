import requests
from config import Config

class WazzupAPI:
    def __init__(self):
        self.api_key = Config.WAZZUP_API_KEY
        self.base_url = "https://api.wazzup24.com/v3"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def send_message(self, chat_id, message):
        endpoint = f"{self.base_url}/send_message"
        payload = {
            "chatId": chat_id,
            "text": message
        }
        response = requests.post(endpoint, json=payload, headers=self.headers)
        return response.json()

    def receive_message(self, data):
        message = data.get('messages', [{}])[0]
        return {
            'chat_id': message.get('chatId'),
            'text': message.get('text'),
            'sender': message.get('fromMe', False)
        }
