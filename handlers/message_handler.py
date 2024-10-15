from api_wazzup.wazzup_api import WazzupAPI
from api_openai.openai_api import OpenAIAssistant
from database.database import db, Client, Message, Thread
from utils.utils import log_message
from datetime import datetime

class MessageHandler:
    def __init__(self):
        self.wazzup_api = WazzupAPI()
        self.openai_assistant = OpenAIAssistant()

    def handle_incoming_message(self, message):
        chat_id = message['chat_id']
        text = message['text']
        is_from_client = not message['sender']

        log_message(f"Received message from chat {chat_id}: {text}")

        client = self.get_or_create_client(chat_id)
        self.save_message(client.id, text, is_from_client)

        thread = self.get_or_create_thread(client.id)

        self.openai_assistant.add_message_to_thread(thread.openai_thread_id, text)

        response = self.generate_response(thread.openai_thread_id)

        self.send_response(chat_id, response)

        self.save_message(client.id, response, False)

    def generate_response(self, thread_id):
        return self.openai_assistant.run_assistant(thread_id)

    def send_response(self, chat_id, response):
        self.wazzup_api.send_message(chat_id, response)
        log_message(f"Sent response to chat {chat_id}: {response}")

    def get_or_create_client(self, chat_id):
        client = Client.query.filter_by(phone=chat_id).first()
        if not client:
            client = Client(phone=chat_id)
            db.session.add(client)
            db.session.commit()
        return client

    def get_or_create_thread(self, client_id):
        thread = Thread.query.filter_by(client_id=client_id).first()
        if not thread:
            openai_thread_id = self.openai_assistant.create_thread()
            thread = Thread(client_id=client_id, openai_thread_id=openai_thread_id)
            db.session.add(thread)
            db.session.commit()
        return thread

    def save_message(self, client_id, content, is_from_client):
        message = Message(client_id=client_id, content=content, timestamp=datetime.utcnow(), is_from_client=is_from_client)
        db.session.add(message)
        db.session.commit()
