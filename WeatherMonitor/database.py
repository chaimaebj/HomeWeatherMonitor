"""
Database adapter module for HomeWeather application.
This module provides a unified interface to access both SQLite (via SQLAlchemy) and Firebase.
"""
import os
import logging
from flask import current_app

# Configure logging
logger = logging.getLogger(__name__)

# Initialize global variables
user_model = None
user_settings_model = None
device_model = None
sensor_data_model = None
device_command_model = None
alert_model = None

def init_app(app):
    """
    Initialize the database adapter with the Flask application.
    This function is called during app initialization.
    """
    global user_model, user_settings_model, device_model, sensor_data_model, device_command_model, alert_model

    # Determine which database to use based on configuration
    if app.config.get('USE_FIREBASE', False):
        logger.info("Using Firebase as database")
        try:
            # Import Firebase models
            from firebase_models import (
                FirebaseUser as User,
                FirebaseUserSettings as UserSettings,
                FirebaseDevice as Device,
                FirebaseSensorData as SensorData, 
                FirebaseDeviceCommand as DeviceCommand,
                FirebaseAlert as Alert
            )
            
            # Set global model variables
            user_model = User
            user_settings_model = UserSettings
            device_model = Device
            sensor_data_model = SensorData
            device_command_model = DeviceCommand
            alert_model = Alert
            
            logger.info("Firebase models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Firebase models: {str(e)}")
            logger.warning("Falling back to SQLAlchemy models")
            _load_sqlalchemy_models()
    else:
        logger.info("Using SQLite/SQLAlchemy as database")
        _load_sqlalchemy_models()

def _load_sqlalchemy_models():
    """Load SQLAlchemy models."""
    global user_model, user_settings_model, device_model, sensor_data_model, device_command_model, alert_model
    
    try:
        # Import SQLAlchemy models
        from models import (
            User, 
            UserSettings, 
            Device, 
            SensorData, 
            DeviceCommand,
            Alert
        )
        
        # Set global model variables
        user_model = User
        user_settings_model = UserSettings
        device_model = Device
        sensor_data_model = SensorData
        device_command_model = DeviceCommand
        alert_model = Alert
        
        logger.info("SQLAlchemy models loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load SQLAlchemy models: {str(e)}")

# Functions to access models
def get_user_model():
    """Get the user model."""
    return user_model

def get_user_settings_model():
    """Get the user settings model."""
    return user_settings_model

def get_device_model():
    """Get the device model."""
    return device_model

def get_sensor_data_model():
    """Get the sensor data model."""
    return sensor_data_model

def get_device_command_model():
    """Get the device command model."""
    return device_command_model

def get_alert_model():
    """Get the alert model."""
    return alert_model