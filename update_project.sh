#!/bin/bash

# Обновление api_wazzup/wazzup_api.py
cat << EOF > api_wazzup/wazzup_api.py
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
EOF

# Обновление api_wazzup/routes.py
cat << EOF > api_wazzup/routes.py
from flask import Blueprint, request, jsonify
from .wazzup_api import WazzupAPI

wazzup_bp = Blueprint('wazzup', __name__)
wazzup_api = WazzupAPI()

@wazzup_bp.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    message = wazzup_api.receive_message(data)
    # Здесь вы можете добавить логику обработки сообщения
    # Например, передать его в MessageHandler
    return jsonify({"status": "success"}), 200

@wazzup_bp.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    chat_id = data.get('chat_id')
    message = data.get('message')
    if not chat_id or not message:
        return jsonify({"error": "Missing chat_id or message"}), 400

    response = wazzup_api.send_message(chat_id, message)
    return jsonify(response), 200
EOF

# Обновление api_openai/openai_api.py
cat << EOF > api_openai/openai_api.py
import openai
from config import Config

class OpenAIAssistant:
    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY
        self.assistant_id = Config.OPENAI_ASSISTANT_ID
        openai.api_key = self.api_key

    def create_thread(self):
        thread = openai.beta.threads.create()
        return thread.id

    def add_message_to_thread(self, thread_id, message):
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )

    def run_assistant(self, thread_id):
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant_id
        )
        while run.status != 'completed':
            run = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        return messages.data[0].content[0].text.value
EOF

# Обновление api_openai/routes.py
cat << EOF > api_openai/routes.py
from flask import Blueprint, request, jsonify
from .openai_api import OpenAIAssistant

openai_bp = Blueprint('openai', __name__)
openai_assistant = OpenAIAssistant()

@openai_bp.route('/create_thread', methods=['POST'])
def create_thread():
    thread_id = openai_assistant.create_thread()
    return jsonify({"thread_id": thread_id}), 200

@openai_bp.route('/add_message', methods=['POST'])
def add_message():
    data = request.json
    thread_id = data.get('thread_id')
    message = data.get('message')
    if not thread_id or not message:
        return jsonify({"error": "Missing thread_id or message"}), 400

    openai_assistant.add_message_to_thread(thread_id, message)
    return jsonify({"status": "success"}), 200

@openai_bp.route('/run_assistant', methods=['POST'])
def run_assistant():
    data = request.json
    thread_id = data.get('thread_id')
    if not thread_id:
        return jsonify({"error": "Missing thread_id"}), 400

    response = openai_assistant.run_assistant(thread_id)
    return jsonify({"response": response}), 200
EOF

# Обновление handlers/message_handler.py
cat << EOF > handlers/message_handler.py
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
EOF

# Обновление main.py
cat << EOF > main.py
from flask import Flask, request, jsonify
from config import Config
from api_wazzup.routes import wazzup_bp
from api_openai.routes import openai_bp
from user_interface import create_ui
from database.database import db, init_db
from handlers.message_handler import MessageHandler

app = Flask(__name__)
app.config.from_object(Config)

# Инициализация базы данных
db.init_app(app)
with app.app_context():
    init_db()

# Регистрация blueprints
app.register_blueprint(wazzup_bp, url_prefix='/wazzup')
app.register_blueprint(openai_bp, url_prefix='/openai')

# Создание пользовательского интерфейса
create_ui(app)

# Инициализация MessageHandler
message_handler = MessageHandler()

# Обновляем route для вебхука, чтобы использовать MessageHandler
@wazzup_bp.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    message = wazzup_api.receive_message(data)
    message_handler.handle_incoming_message(message)
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(debug=True)
EOF

# Создание шаблона для пользовательского интерфейса
mkdir -p templates
cat << EOF > templates/index.html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wazzap Assistant Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        #messageLog { border: 1px solid #ccc; height: 400px; overflow-y: scroll; padding: 10px; margin-bottom: 20px; }
        .message { margin-bottom: 10px; }
        .client { color: blue; }
        .assistant { color: green; }
    </style>
</head>
<body>
    <h1>Wazzap Assistant Dashboard</h1>
    <div id="messageLog"></div>
    <button onclick="fetchMessages()">Обновить сообщения</button>

    <script>
        function fetchMessages() {
            fetch('/get_messages')
                .then(response => response.json())
                .then(data => {
                    const messageLog = document.getElementById('messageLog');
                    messageLog.innerHTML = '';
                    data.messages.forEach(msg => {
                        const messageDiv = document.createElement('div');
                        messageDiv.className = \`message \${msg.is_from_client ? 'client' : 'assistant'}\`;
                        messageDiv.textContent = \`\${msg.timestamp}: \${msg.content}\`;
                        messageLog.appendChild(messageDiv);
                    });
                })
                .catch(error => console.error('Error:', error));
        }

        // Обновляем сообщения каждые 5 секунд
        setInterval(fetchMessages, 5000);
        // Загружаем сообщения при загрузке страницы
        fetchMessages();
    </script>
</body>
</html>
EOF

# Обновление user_interface/__init__.py
cat << EOF > user_interface/__init__.py
from flask import render_template, jsonify
from database.database import Message

def create_ui(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/get_messages')
    def get_messages():
        messages = Message.query.order_by(Message.timestamp.desc()).limit(50).all()
        return jsonify({
            'messages': [
                {
                    'content': msg.content,
                    'timestamp': msg.timestamp.isoformat(),
                    'is_from_client': msg.is_from_client
                } for msg in messages
            ]
        })
EOF

echo "Проект обновлен и дополнен новыми компонентами."