#!/bin/bash

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

# Обновление main.py
cat << EOF > main.py
from flask import Flask, jsonify
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

if __name__ == '__main__':
    app.run(debug=True)
EOF

echo "Структура проекта обновлена для исправления ошибки регистрации blueprint."