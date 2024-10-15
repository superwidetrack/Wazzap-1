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
