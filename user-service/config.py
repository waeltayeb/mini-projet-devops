import os

SECRET_KEY = os.getenv('SECRET_KEY', 'my_secret_key')
SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
