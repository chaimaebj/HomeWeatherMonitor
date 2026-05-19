import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from flask import current_app
import threading
from firebase_models import SensorData

# Configure logger
logger = logging.getLogger(__name__)

def send_alert_in_background(app, function, **kwargs):
    """Helper to run a function in a background thread with app context."""
    def wrapper(app, **kwargs):
        with app.app_context():
            function(**kwargs)
    
    thread = threading.Thread(target=wrapper, args=(app,), kwargs=kwargs)
    thread.start()

def send_email_alert(recipient, subject, message):
    """Send email alert to user"""
    try:
        # Get email config from app config
        app_config = current_app.config
        sender = app_config.get('MAIL_DEFAULT_SENDER')
        server = app_config.get('MAIL_SERVER')
        port = app_config.get('MAIL_PORT')
        username = app_config.get('MAIL_USERNAME')
        password = app_config.get('MAIL_PASSWORD')
        
        # If email credentials are not set, log error and return
        if not all([sender, server, port, username, password]):
            logger.warning("Email configuration is incomplete. Cannot send email alerts.")
            return False

        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        
        # Connect to server and send email
        with smtplib.SMTP(server, port) as smtp:
            smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(msg)
            
        logger.info(f"Email alert sent to {recipient}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send email alert: {str(e)}")
        return False

def send_sms_alert(phone_number, message):
    """Send SMS alert using Vonage"""
    try:
        # Import Vonage only when needed to avoid dependency issues
        import vonage
        
        # Get Vonage config from app config
        app_config = current_app.config
        vonage_api_key = app_config.get('VONAGE_API_KEY')
        vonage_api_secret = app_config.get('VONAGE_API_SECRET')
        vonage_number = app_config.get('VONAGE_PHONE_NUMBER')
        
        # If Vonage credentials are not set, log error and return
        if not all([vonage_api_key, vonage_api_secret, vonage_number]):
            logger.warning("Vonage configuration is incomplete. Cannot send SMS alerts.")
            return False
        
        # Initialize Vonage client and send SMS
        client = vonage.Client(key=vonage_api_key, secret=vonage_api_secret)
        sms = vonage.Sms(client)
        responseData = sms.send_message({
            "from": vonage_number,
            "to": phone_number,
            "text": message,
        })
        
        if responseData["messages"][0]["status"] == "0":
            logger.info(f"SMS alert sent to {phone_number} via Vonage")
            return True
        else:
            logger.error(f"Failed to send SMS alert via Vonage: {responseData['messages'][0]['error-text']}")
            return False
    except ImportError:
        logger.error("Vonage package not installed. Cannot send SMS alerts.")
        return False
    except Exception as e:
        logger.error(f"Failed to send SMS alert via Vonage: {str(e)}")
        return False

def clean_old_data():
    """Remove sensor data older than the retention period"""
    try:
        app_config = current_app.config
        retention_days = app_config.get('DATA_RETENTION_DAYS', 30)
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        # Delete old records
        deleted = SensorData.query.filter(SensorData.timestamp < cutoff_date).delete()
        db.session.commit()
        
        logger.info(f"Cleaned {deleted} old sensor data records")
        return True
    
    except Exception as e:
        logger.error(f"Error cleaning old data: {str(e)}")
        db.session.rollback()
        return False

def get_historical_data(days=1):
    """Get historical sensor data for all devices (global)"""
    try:
        from firebase_db import get_historical_sensor_data

        data = get_historical_sensor_data(days=days)
        return data

    except Exception as e:
        logger.error(f"Error getting historical data: {str(e)}")
        return []

def predict_next_reading(device_id):
    """Predict next sensor reading using simple moving average"""
    try:
        # Get last 6 hours of data
        recent_data = get_historical_data(device_id, days=0.25)
        
        if not recent_data:
            return None
            
        # Calculate averages
        temp_sum = humid_sum = air_quality_sum = 0
        count = len(recent_data)
        
        for reading in recent_data:
            temp_sum += reading.temperature if reading.temperature else 0
            humid_sum += reading.humidity if reading.humidity else 0
            air_quality_sum += reading.air_quality if reading.air_quality else 0
            
        # Return prediction dictionary
        return {
            'temperature': round(temp_sum / count, 1) if count > 0 else None,
            'humidity': round(humid_sum / count, 1) if count > 0 else None,
            'air_quality': round(air_quality_sum / count, 1) if count > 0 else None
        }
        
    except Exception as e:
        logger.error(f"Error predicting next reading: {str(e)}")
        return None

def check_thresholds_and_alert():
    """Check sensor readings against thresholds and send alerts if needed"""
    try:
        from datetime import datetime, timedelta
        
        # Get all active devices
        devices = Device.query.filter_by(status='online').all()
        
        for device in devices:
            # Get latest reading
            latest_reading = SensorData.query.filter_by(device_id=device.device_id)\
                .order_by(SensorData.timestamp.desc()).first()
            
            if not latest_reading:
                continue
                
            alerts = []
            
            # Check temperature thresholds
            if latest_reading.temperature is not None:
                if latest_reading.temperature > 30:  # High temperature threshold
                    alerts.append(f"High temperature alert: {latest_reading.temperature}°C")
                elif latest_reading.temperature < 10:  # Low temperature threshold
                    alerts.append(f"Low temperature alert: {latest_reading.temperature}°C")
            
            # Check humidity thresholds
            if latest_reading.humidity is not None:
                if latest_reading.humidity > 70:  # High humidity threshold
                    alerts.append(f"High humidity alert: {latest_reading.humidity}%")
                elif latest_reading.humidity < 30:  # Low humidity threshold
                    alerts.append(f"Low humidity alert: {latest_reading.humidity}%")
            
            # Check air quality threshold
            if latest_reading.air_quality is not None and latest_reading.air_quality > 150:
                alerts.append(f"Poor air quality alert: {latest_reading.air_quality} AQI")
            
            # Check rain detection
            if latest_reading.rain_detected:
                alerts.append("Rain detected!")
            
            # Send alerts if any thresholds exceeded
            if alerts:
                alert_message = f"Alerts for {device.name} ({device.device_id}):\n"
                alert_message += "\n".join(alerts)
                
                # Send email alert
                if device.email_alerts:
                    send_email_alert(
                        device.email_alerts,
                        f"Weather Monitor Alert - {device.name}",
                        alert_message
                    )
                
                # Send SMS alert
                if device.sms_alerts:
                    send_sms_alert(
                        device.sms_alerts,
                        alert_message
                    )
                    
                logger.info(f"Sent alerts for device {device.device_id}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking thresholds: {str(e)}")
        return False
