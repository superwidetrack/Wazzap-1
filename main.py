from flask import Flask, jsonify
from config import Config
from api_wazzup.routes import wazzup_bp
from api_openai.routes import openai_bp
from user_interface import create_ui
from database.database import db, init_db
from handlers.message_handler import MessageHandler
import os

app = Flask(__name__)
app.config.from_object(Config)

# Инициализация базы данных
init_db(app)

# Регистрация blueprints
app.register_blueprint(wazzup_bp, url_prefix='/wazzup')
app.register_blueprint(openai_bp, url_prefix='/openai')

# Создание пользовательского интерфейса
create_ui(app)

# Инициализация MessageHandler
message_handler = MessageHandler()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 8080)),
        debug=True
    )