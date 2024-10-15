import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    WAZZUP_API_KEY = os.getenv('WAZZUP_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_ASSISTANT_ID = os.getenv('OPENAI_ASSISTANT_ID')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///wazzap_assistant.db')  # Переименовали переменную
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Отключение слежения за изменениями в SQLAlchemy
