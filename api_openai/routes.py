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
