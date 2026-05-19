import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from firebase_db import (
    get_user_by_id, get_user_by_email, create_user,
    get_user_settings, save_user_settings,
    save_sensor_data, get_latest_sensor_data,
    create_device_command, update_command_status,
    create_alert, get_latest_alerts
)
from firebase_config import get_realtime_db
from firestore_models import FirestoreUser, FirestoreAlert

logger = logging.getLogger(__name__)

class User:
    """User model for Firebase authentication and Realtime Database."""
    
    def __init__(self, username: str, email: str, password_hash: str, id: Optional[str] = None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create a User instance from a dictionary."""
        user = cls(
            username=data['username'],
            email=data['email'],
            password_hash=data['password_hash'],
            id=data.get('id')
        )
        if 'created_at' in data:
            user.created_at = data['created_at']
        if 'updated_at' in data:
            user.updated_at = data['updated_at']
        return user

    def to_dict(self) -> Dict:
        """Convert User instance to a dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def get_by_id(cls, user_id: str) -> Optional['User']:
        """Get user by ID from database."""
        user_data = get_user_by_id(user_id)
        if user_data:
            return cls.from_dict(user_data)
        return None

    @classmethod
    def get_by_email(cls, email: str) -> Optional['User']:
        """Get user by email from database."""
        user_data = get_user_by_email(email)
        if user_data:
            return cls.from_dict(user_data)
        return None

    def save(self) -> bool:
        """Save user to database."""
        user_data = self.to_dict()
        if self.id:
            # Update existing user
            success = update_user(self.id, user_data)
            if success:
                logger.info(f"Updated user {self.username} with ID {self.id} in database")
            else:
                logger.warning(f"Failed to update user {self.username} in database, but continuing")
            return success
        else:
            # Create new user
            user_id = create_user(user_data)
            if user_id:
                self.id = user_id
                logger.info(f"Created user {self.username} with ID {self.id} in database")
                return True
            else:
                logger.warning(f"Failed to create user {self.username} in database")
                return False

class UserSettings:
    """User settings model for Firebase Realtime Database."""
    
    def __init__(self, user_id: str, settings: Dict = None):
        self.user_id = user_id
        self.settings = settings or {}
        self.updated_at = datetime.now()

    @classmethod
    def from_dict(cls, data: Dict) -> 'UserSettings':
        """Create a UserSettings instance from a dictionary."""
        settings = cls(
            user_id=data['user_id'],
            settings=data.get('settings', {})
        )
        if 'updated_at' in data:
            settings.updated_at = data['updated_at']
        return settings

    def to_dict(self) -> Dict:
        """Convert UserSettings instance to a dictionary."""
        return {
            'user_id': self.user_id,
            'settings': self.settings,
            'updated_at': self.updated_at
        }

    @classmethod
    def get_by_user_id(cls, user_id: str) -> Optional['UserSettings']:
        """Get user settings by user ID from database."""
        settings_data = get_user_settings(user_id)
        if settings_data:
            return cls.from_dict(settings_data)
        return None

    def save(self) -> bool:
        """Save settings to database."""
        settings_data = self.to_dict()
        success = save_user_settings(self.user_id, settings_data)
        if success:
            logger.info(f"Saved settings for user {self.user_id} to database")
        else:
            logger.warning(f"Failed to save settings for user {self.user_id} to database, but continuing")
        return success

class SensorData:
    """Sensor data model for Firebase Realtime Database."""
    
    def __init__(self, device_id: str, sensor_type: str, value: float, unit: str, id: Optional[str] = None):
        self.id = id
        self.device_id = device_id
        self.sensor_type = sensor_type
        self.value = value
        self.unit = unit
        self.timestamp = datetime.now()

    @classmethod
    def from_dict(cls, data: Dict) -> 'SensorData':
        """Create a SensorData instance from a dictionary."""
        sensor_data = cls(
            device_id=data['device_id'],
            sensor_type=data['sensor_type'],
            value=data['value'],
            unit=data['unit'],
            id=data.get('id')
        )
        if 'timestamp' in data:
            sensor_data.timestamp = data['timestamp']
        return sensor_data

    def to_dict(self) -> Dict:
        """Convert SensorData instance to a dictionary."""
        return {
            'device_id': self.device_id,
            'sensor_type': self.sensor_type,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp
        }

    def save(self) -> bool:
        """Save sensor data to Firebase Realtime Database."""
        db = get_realtime_db()
        if not db:
            return False

        data = self.to_dict()
        try:
            # Create a new sensor data entry
            sensor_ref = db.child('sensors').push(data)
            self.id = sensor_ref.key
            logger.info(f"Saved sensor data for device {self.device_id} with ID {self.id}")
            return True
        except Exception as e:
            logger.error(f"Error saving sensor data: {str(e)}")
            return False

    @classmethod
    def get_latest(cls, device_id: str, limit: int = 100) -> List['SensorData']:
        """Get latest sensor data for a device from Firebase Realtime Database."""
        db = get_realtime_db()
        if not db:
            return []

        try:
            # Query sensor data for the device, ordered by timestamp
            query = db.child('sensors').order_by_child('device_id').equal_to(device_id).limit_to_last(limit)
            data = query.get()
            
            if not data:
                return []
            
            # Convert to list of SensorData objects
            sensor_data_list = []
            for key, value in data.items():
                value['id'] = key
                sensor_data_list.append(cls.from_dict(value))
            
            # Sort by timestamp
            sensor_data_list.sort(key=lambda x: x.timestamp, reverse=True)
            return sensor_data_list
        except Exception as e:
            logger.error(f"Error getting sensor data: {str(e)}")
            return []

class DeviceCommand:
    """Device command model for Firebase Realtime Database."""
    
    def __init__(self, device_id: str, command: str, parameters: Dict = None, id: Optional[str] = None):
        self.id = id
        self.device_id = device_id
        self.command = command
        self.parameters = parameters or {}
        self.status = 'pending'
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    @classmethod
    def from_dict(cls, data: Dict) -> 'DeviceCommand':
        """Create a DeviceCommand instance from a dictionary."""
        command = cls(
            device_id=data['device_id'],
            command=data['command'],
            parameters=data.get('parameters', {}),
            id=data.get('id')
        )
        if 'status' in data:
            command.status = data['status']
        if 'created_at' in data:
            command.created_at = data['created_at']
        if 'updated_at' in data:
            command.updated_at = data['updated_at']
        return command

    def to_dict(self) -> Dict:
        """Convert DeviceCommand instance to a dictionary."""
        return {
            'device_id': self.device_id,
            'command': self.command,
            'parameters': self.parameters,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def save(self) -> bool:
        """Save command to Firebase Realtime Database."""
        db = get_realtime_db()
        if not db:
            return False

        command_data = self.to_dict()
        try:
            if self.id:
                # Update existing command
                db.child('device_commands').child(self.id).update(command_data)
                logger.info(f"Updated command for device {self.device_id} with ID {self.id}")
            else:
                # Create new command
                command_ref = db.child('device_commands').push(command_data)
                self.id = command_ref.key
                logger.info(f"Created command for device {self.device_id} with ID {self.id}")
            return True
        except Exception as e:
            logger.error(f"Error saving command: {str(e)}")
            return False

    def update_status(self, status: str) -> bool:
        """Update command status in Firebase Realtime Database."""
        if not self.id:
            logger.warning("Cannot update status: command has no ID")
            return False
        
        db = get_realtime_db()
        if not db:
            return False

        try:
            self.status = status
            self.updated_at = datetime.now()
            db.child('device_commands').child(self.id).update({
                'status': status,
                'updated_at': self.updated_at
            })
            logger.info(f"Updated command {self.id} status to {status}")
            return True
        except Exception as e:
            logger.error(f"Error updating command status: {str(e)}")
            return False

class Alert:
    """Alert model for Firebase Realtime Database."""
    
    def __init__(self, device_id: str, alert_type: str, message: str, severity: str = 'info', id: Optional[str] = None):
        self.id = id
        self.device_id = device_id
        self.alert_type = alert_type
        self.message = message
        self.severity = severity
        self.timestamp = datetime.now()
        self.acknowledged = False

    @classmethod
    def from_dict(cls, data: Dict) -> 'Alert':
        """Create an Alert instance from a dictionary."""
        alert = cls(
            device_id=data['device_id'],
            alert_type=data['alert_type'],
            message=data['message'],
            severity=data.get('severity', 'info'),
            id=data.get('id')
        )
        if 'timestamp' in data:
            alert.timestamp = data['timestamp']
        if 'acknowledged' in data:
            alert.acknowledged = data['acknowledged']
        return alert

    def to_dict(self) -> Dict:
        """Convert Alert instance to a dictionary."""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'alert_type': self.alert_type,
            'message': self.message,
            'severity': self.severity,
            'timestamp': self.timestamp,
            'acknowledged': self.acknowledged
        }

    def save(self) -> bool:
        """Save alert to database."""
        alert_data = self.to_dict()
        alert_id = create_alert(alert_data)
        if alert_id:
            self.id = alert_id
            logger.info(f"Created alert for device {self.device_id} with ID {self.id}")
            return True
        else:
            logger.warning(f"Failed to create alert for device {self.device_id}")
            return False

    @classmethod
    def get_latest(cls, limit: int = 100) -> List['Alert']:
        """Get latest alerts from database."""
        alerts_data = get_latest_alerts(limit)
        return [cls.from_dict(alert_data) for alert_data in alerts_data] 