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
