# app_factory.py
from flask import Flask
from config import *
from models import db
from routes import reservation_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    db.init_app(app)
    app.register_blueprint(reservation_bp)
    return app
