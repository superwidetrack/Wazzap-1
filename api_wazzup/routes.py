from flask import Blueprint, request, jsonify
from .wazzup_api import WazzupAPI  # Убедитесь, что класс называется WazzupAPI

wazzup_bp = Blueprint('wazzup', __name__)  # Все названия теперь consistent с "wazzup"
wazzup_api = WazzupAPI()

@wazzup_bp.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        data = request.json
        message = wazzup_api.receive_message(data)
        # Здесь вы можете добавить логику обработки сообщения
        # Например, передать его в MessageHandler
        print(f"Received message: {message}")  # Для отладки
        return jsonify({"status": "success"}), 200
    else:
        # Обработка GET-запроса
        return jsonify({"status": "Webhook is active. Use POST to send data."}), 200

@wazzup_bp.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    chat_id = data.get('chat_id')
    message = data.get('message')
    if not chat_id or not message:
        return jsonify({"error": "Missing chat_id or message"}), 400
    response = wazzup_api.send_message(chat_id, message)
    return jsonify(response), 200
