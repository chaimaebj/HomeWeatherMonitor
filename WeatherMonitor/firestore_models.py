import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from firebase_config import get_firestore_db
from flask_login import UserMixin

logger = logging.getLogger(__name__)

class FirestoreUser(UserMixin):
    """User model for Firestore."""
    
    def __init__(self, username: str, email: str, password_hash: str, id: Optional[str] = None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    @classmethod
    def from_dict(cls, data: Dict) -> 'FirestoreUser':
        """Create a FirestoreUser instance from a dictionary."""
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
        """Convert FirestoreUser instance to a dictionary."""
        return {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def get_by_id(cls, user_id: str) -> Optional['FirestoreUser']:
        """Get user by ID from Firestore."""
        db = get_firestore_db()
        if not db:
            return None
        
        doc = db.collection('users').document(user_id).get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return cls.from_dict(data)
        return None

    @classmethod
    def get_by_email(cls, email: str) -> Optional['FirestoreUser']:
        """Get user by email from Firestore."""
        db = get_firestore_db()
        if not db:
            return None
        
        query = db.collection('users').where('email', '==', email).limit(1)
        docs = query.get()
        
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            return cls.from_dict(data)
        return None

    @classmethod
    def get_by_username(cls, username: str) -> Optional['FirestoreUser']:
        """Get user by username from Firestore."""
        db = get_firestore_db()
        if not db:
            return None
        
        query = db.collection('users').where('username', '==', username).limit(1)
        docs = query.stream()
        
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            return cls.from_dict(data)
        return None

    def save(self) -> bool:
        """Save user to Firestore."""
        db = get_firestore_db()
        if not db:
            return False

        user_data = self.to_dict()
        try:
            if self.id:
                # Update existing user
                db.collection('users').document(self.id).update(user_data)
                logger.info(f"Updated user {self.username} with ID {self.id} in Firestore")
            else:
                # Create new user
                doc_ref = db.collection('users').document()
                doc_ref.set(user_data)
                self.id = doc_ref.id
                logger.info(f"Created user {self.username} with ID {self.id} in Firestore")
            return True
        except Exception as e:
            logger.error(f"Error saving user to Firestore: {str(e)}")
            return False

    def get_id(self):
        """Required by Flask-Login. Returns the unique ID for the user."""
        return str(self.id)

class FirestoreAlert:
    """Alert model for Firestore."""
    
    def __init__(self, device_id: str, alert_type: str, message: str, severity: str = 'info', id: Optional[str] = None):
        self.id = id
        self.device_id = device_id
        self.alert_type = alert_type
        self.message = message
        self.severity = severity
        self.timestamp = datetime.now()
        self.acknowledged = False

    @classmethod
    def from_dict(cls, data: Dict) -> 'FirestoreAlert':
        """Create a FirestoreAlert instance from a dictionary."""
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
        """Convert FirestoreAlert instance to a dictionary."""
        return {
            'device_id': self.device_id,
            'alert_type': self.alert_type,
            'message': self.message,
            'severity': self.severity,
            'timestamp': self.timestamp,
            'acknowledged': self.acknowledged
        }

    def save(self) -> bool:
        """Save alert to Firestore."""
        db = get_firestore_db()
        if not db:
            return False

        alert_data = self.to_dict()
        try:
            if self.id:
                # Update existing alert
                db.collection('alerts').document(self.id).update(alert_data)
                logger.info(f"Updated alert with ID {self.id} in Firestore")
            else:
                # Create new alert
                doc_ref = db.collection('alerts').document()
                doc_ref.set(alert_data)
                self.id = doc_ref.id
                logger.info(f"Created alert with ID {self.id} in Firestore")
            return True
        except Exception as e:
            logger.error(f"Error saving alert to Firestore: {str(e)}")
            return False

    @classmethod
    def get_latest(cls, limit: int = 100) -> List['FirestoreAlert']:
        """Get latest alerts from Firestore."""
        db = get_firestore_db()
        if not db:
            return []

        try:
            query = db.collection('alerts').order_by('timestamp', direction='DESCENDING').limit(limit)
            docs = query.get()
            
            alerts = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                alerts.append(cls.from_dict(data))
            return alerts
        except Exception as e:
            logger.error(f"Error getting alerts from Firestore: {str(e)}")
            return [] 