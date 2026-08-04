# config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DISK_TOKEN = os.getenv('DISK_TOKEN', '')
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
