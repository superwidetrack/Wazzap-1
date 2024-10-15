#!/bin/bash

# Обновление database/database.py
cat << EOF > database/database.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Client(db.Model):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    phone = Column(String, unique=True, nullable=False)
    name = Column(String)

class Message(db.Model):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    is_from_client = Column(Boolean, nullable=False)

class Thread(db.Model):
    __tablename__ = 'threads'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    openai_thread_id = Column(String, nullable=False)

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
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
init_db(app)

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

echo "Структура проекта обновлена для исправления ошибки инициализации базы данных."