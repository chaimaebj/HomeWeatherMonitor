import os
import json
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Configuration générale
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_for_development_only')
    
    # Configuration Firebase
    USE_FIREBASE = True
    
    # Désactiver SQLite
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask configuration
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Database configuration - SQLite (legacy)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Firebase configuration
    FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY")
    FIREBASE_AUTH_DOMAIN = os.environ.get("FIREBASE_AUTH_DOMAIN")
    FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID")
    FIREBASE_STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET")
    FIREBASE_MESSAGING_SENDER_ID = os.environ.get("FIREBASE_MESSAGING_SENDER_ID")
    FIREBASE_APP_ID = os.environ.get("FIREBASE_APP_ID")
    FIREBASE_DATABASE_URL = os.environ.get("FIREBASE_DATABASE_URL")
    
    # Email configuration for alerts
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")
    
    # Vonage configuration for SMS alerts
    VONAGE_API_KEY = os.environ.get("VONAGE_API_KEY")
    VONAGE_API_SECRET = os.environ.get("VONAGE_API_SECRET")
    VONAGE_PHONE_NUMBER = os.environ.get("VONAGE_PHONE_NUMBER")
    
    # Sensor threshold configurations
    TEMPERATURE_MAX = float(os.environ.get("TEMPERATURE_MAX", 30.0))  # in °C
    TEMPERATURE_MIN = float(os.environ.get("TEMPERATURE_MIN", 10.0))  # in °C
    HUMIDITY_MAX = float(os.environ.get("HUMIDITY_MAX", 70.0))        # in %
    HUMIDITY_MIN = float(os.environ.get("HUMIDITY_MIN", 30.0))        # in %
    AIR_QUALITY_MAX = float(os.environ.get("AIR_QUALITY_MAX", 100.0)) # PPM
    
    # Data retention period (in days)
    DATA_RETENTION_DAYS = int(os.environ.get("DATA_RETENTION_DAYS", 30))
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
