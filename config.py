from dotenv import load_dotenv
from datetime import timedelta
import os

load_dotenv()
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'super_secret_key')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///database.sqlite3')
    TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SAMESITE='Lax'
    UPLOAD_FOLDER = 'application/static/upload'
    AI_MODEL_TO_USE = 'gpt-4o-mini'
    AI_API_KEY = os.getenv("AI_API_KEY", 'abc')

class DevelopmentConfig(Config):
    FRONTEND_BASE_URL = "http://localhost:3000"
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL")
    DEBUG = False
    ENV = 'production'