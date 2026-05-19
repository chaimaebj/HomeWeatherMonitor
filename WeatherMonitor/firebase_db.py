import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dotenv import load_dotenv
from firebase_admin import db
from flask_login import UserMixin
import uuid
from firebase_config import initialize_firebase, get_firebase_config, get_firestore_db
from firestore_models import FirestoreUser, FirestoreAlert

# Load environment variables
load_dotenv()

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize Firebase Realtime Database
realtime_db = None

try:
    import firebase_admin
    from firebase_admin import credentials, db
    from firebase_admin.exceptions import FirebaseError
except ImportError:
    logger.warning("Firebase Admin SDK not installed. Running in offline mode.")
    firebase_admin = None

def datetime_to_timestamp(dt: datetime) -> int:
    """Convert datetime to timestamp (milliseconds)."""
    return int(dt.timestamp() * 1000)

def timestamp_to_datetime(ts: int) -> datetime:
    """Convert timestamp (milliseconds) to datetime."""
    return datetime.fromtimestamp(ts / 1000)

def dict_to_document(data: Dict) -> Dict:
    """Convert a dictionary to a Firebase Realtime Database compatible format."""
    result = {}
    for key, value in data.items():
        if isinstance(value, datetime):
            result[key] = datetime_to_timestamp(value)
        else:
            result[key] = value
    return result

def document_to_dict(data: Dict) -> Dict:
    """Convert a Firebase Realtime Database document to a dictionary with datetime objects."""
    result = {}
    for key, value in data.items():
        if key in ['created_at', 'updated_at', 'timestamp'] and isinstance(value, (int, float)):
            result[key] = timestamp_to_datetime(int(value))
        else:
            result[key] = value
    return result

def initialize_firebase():
    """Initialize Firebase connection."""
    global realtime_db
    try:
        if not firebase_admin._apps:
            # Get Firebase configuration
            config = get_firebase_config()
            
            # Get service account path from environment or use default
            service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH', 
                                          os.path.join(os.path.dirname(__file__), 'firebase_service_account.json'))
            
            if not os.path.exists(service_account_path):
                raise FileNotFoundError(
                    f"Firebase service account file not found at: {service_account_path}\n"
                    "Please ensure the service account file exists and the path is correct."
                )
            
            # Initialize Firebase with configuration
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred, config)
            
            # Test the connection
            realtime_db = db.reference()
            test_ref = realtime_db.child('test_connection')
            test_ref.set({'timestamp': datetime_to_timestamp(datetime.now())})
            test_ref.delete()  # Clean up test data
            
            logger.info("Firebase Realtime Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {str(e)}")
        realtime_db = None
        raise

# Initialize Firebase on module import
initialize_firebase()

def test_connection() -> bool:
    """Test the connection to Firebase Realtime Database."""
    try:
        if not realtime_db:
            return False
        
        # Try to write and read a test value
        test_ref = realtime_db.child('test_connection')
        test_data = {'timestamp': datetime_to_timestamp(datetime.now())}
        test_ref.set(test_data)
        result = test_ref.get()
        test_ref.delete()  # Clean up
        
        return result is not None
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return False

class FirebaseUser(UserMixin):
    def __init__(self, user_data):
        print("DEBUG user_data reçu dans FirebaseUser:", user_data)
        self.id = user_data.get('id')
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.password_hash = user_data.get('password_hash')
        self.phone_number = user_data.get('phone_number')
        self.created_at = user_data.get('created_at')
        self.settings = user_data.get('settings', {})

    @classmethod
    def from_dict(cls, data: Dict) -> 'FirebaseUser':
        """Create a FirebaseUser instance from a dictionary."""
        user = cls(
            user_data=data
        )
        # Ensure created_at is a datetime object if it comes as a string
        if 'created_at' in data and isinstance(data['created_at'], str):
            try:
                user.created_at = datetime.fromisoformat(data['created_at'])
            except ValueError:
                pass # Keep as string if parsing fails
        return user

    def get_id(self):
        print(f"DEBUG: get_id called, returning {self.id}")
        return str(self.id)

    def is_active(self):
        """True, as all users are active."""
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def is_authenticated(self):
        """True, as the user is authenticated."""
        return True

def get_user_by_id(user_id):
    """Récupère un utilisateur par son ID depuis Firestore."""
    return FirestoreUser.get_by_id(user_id)

def get_user_by_username(username):
    """Récupère un utilisateur par son nom d'utilisateur depuis Firestore."""
    return FirestoreUser.get_by_username(username)

def get_user_by_email(email):
    """Récupère un utilisateur par son email depuis Firestore."""
    return FirestoreUser.get_by_email(email)

def get_all_users():
    """Retrieves all users from Firestore."""
    db = get_firestore_db()
    if not db:
        return []
    users_ref = db.collection('users').stream()
    return [FirestoreUser.from_dict(doc.to_dict()) for doc in users_ref]

def create_user(username, email, password_hash, phone_number=None):
    """Crée un nouvel utilisateur dans Firestore."""
    user = FirestoreUser(username=username, email=email, password_hash=password_hash)
    # The FirestoreUser model doesn't have phone_number, so we would need to add it there if needed.
    if user.save():
        # Also save user settings
        default_settings = {
                'email_alerts': True,
                'sms_alerts': False,
            'phone_number': phone_number or '',
                'temperature_alert_min': 10.0,
                'temperature_alert_max': 30.0,
                'humidity_alert_min': 30.0,
                'humidity_alert_max': 70.0,
                'air_quality_alert': 200.0
            }
        save_user_settings(user.id, default_settings)
        return user
        return None

def save_sensor_data(device_id, data):
    """Sauvegarde les données d'un capteur dans Firebase RTDB."""
    try:
        data['timestamp'] = datetime_to_timestamp(datetime.utcnow())
        sensor_ref = db.reference(f'/home_weather/{device_id}')
        sensor_ref.push(data)
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des données du capteur: {str(e)}")
        return False

def get_sensor_data(device_id, limit=100):
    """Récupère les dernières données d'un capteur depuis Firebase RTDB."""
    try:
        sensor_ref = db.reference(f'/home_weather/{device_id}')
        return sensor_ref.order_by_child('timestamp').limit_to_last(limit).get()
    except Exception as e:
        print(f"Erreur lors de la récupération des données du capteur: {str(e)}")
        return None

def create_alert(device_id, alert_type, message):
    """Crée une nouvelle alerte dans Firestore."""
    alert = FirestoreAlert(device_id=device_id, alert_type=alert_type, message=message)
    return alert.save()

def get_alerts(limit=100):
    """Récupère toutes les alertes depuis Firestore."""
    return FirestoreAlert.get_latest(limit=limit)

# User settings operations
def get_user_settings(user_id: str) -> Optional[Dict]:
    """Get user settings from Firestore."""
    db = get_firestore_db()
    if not db:
        return None
    doc_ref = db.collection('user_settings').document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None

def save_user_settings(user_id: str, settings: Dict) -> bool:
    """Save user settings to Firestore."""
    db = get_firestore_db()
    if not db:
        return False
    try:
        db.collection('user_settings').document(user_id).set(settings, merge=True)
        return True
    except Exception as e:
        logger.error(f"Error saving user settings to Firestore: {e}")
    return False

# Device commands operations
def create_device_command(command_data: Dict) -> Optional[str]:
    """Create a new device command in Firebase Realtime Database."""
    try:
        if realtime_db:
            command_ref = realtime_db.child('device_commands').push()
            command_id = command_ref.key
            command_data['id'] = command_id
            command_ref.set(dict_to_document(command_data))
            return command_id
    except Exception as e:
        logger.error(f"Error creating device command in Firebase: {str(e)}")
    return None

def update_command_status(command_id: str, status: str) -> bool:
    """Update command status in Firebase Realtime Database."""
    try:
        if realtime_db:
            realtime_db.child('device_commands').child(command_id).update({
                'status': status,
                'updated_at': datetime_to_timestamp(datetime.now())
            })
            return True
    except Exception as e:
        logger.error(f"Error updating command status in Firebase: {str(e)}")
    return False

# Alert operations
def get_latest_alerts(limit: int = 100) -> List[Dict]:
    """Get latest alerts from Firebase Realtime Database."""
    try:
        if realtime_db:
            alerts = realtime_db.child('alerts')\
                .order_by_child('timestamp')\
                .limit_to_last(limit)\
                .get()
            if alerts:
                return [document_to_dict(alert) for alert in alerts.values()]
    except Exception as e:
        logger.error(f"Error getting alerts from Firebase: {str(e)}")
    return []

def get_all_sensor_data_for_charts() -> list:
    """Récupère toutes les données des capteurs sous forme de liste exploitable pour les graphiques."""
    print("DEBUG: get_all_sensor_data_for_charts called.") # Debug line to confirm function call
    try:
        ref = db.reference('home_weather')
        raw_data = ref.get() or {}
        data_list = []
        for key, values in raw_data.items():
            if not isinstance(values, dict):
                continue

            # Extract timestamp from the values dictionary
            # Assuming timestamp is stored as a value within the dictionary, not as the key
            timestamp_value = values.get('timestamp')
            if timestamp_value is None:
                print(f"DEBUG: Skipping entry with missing timestamp: {key}")
                continue

            try:
                # Prioritize parsing string timestamps
                if isinstance(timestamp_value, str):
                    dt_object = datetime.strptime(timestamp_value, '%d-%m-%Y %H:%M:%S')
                    timestamp_ms = int(dt_object.timestamp() * 1000)
                elif isinstance(timestamp_value, (int, float)):
                    # Assume it's a numerical timestamp (seconds or milliseconds)
                    timestamp_float = float(timestamp_value)
                    # If it looks like seconds, convert to milliseconds
                    if timestamp_float < 1e12: # Heuristic: if less than year 2000 in ms, assume seconds
                        timestamp_ms = int(timestamp_float * 1000)
                    else: # Otherwise assume already milliseconds
                        timestamp_ms = int(timestamp_float)
                else:
                    raise ValueError("Unknown timestamp format")

            except (ValueError, TypeError) as e:
                print(f"DEBUG: Skipping entry with invalid timestamp value: {repr(timestamp_value)} for key: {key} Error: {e}")
                continue

            entry = {
                'timestamp': timestamp_ms,
                'temperature': values.get('temperature'),
                'humidity': values.get('humidity'),
                'rain': values.get('rain'),
                'gas': values.get('gas')
            }
            data_list.append(entry)
        data_list.sort(key=lambda x: x['timestamp'])
        print(f"DEBUG: Data list prepared: {len(data_list)} entries.") # Debug list size
        return data_list
    except Exception as e:
        print(f"ERROR in get_all_sensor_data_for_charts: {e}") # Debug error
        return []

def get_latest_sensor_data() -> list:
    """Get the latest sensor data from Firebase."""
    try:
        if realtime_db:
            data = realtime_db.child('home_weather').order_by_child('timestamp').limit_to_last(1).get()
            if data:
                return [document_to_dict(doc) for doc in data.values()]
    except Exception as e:
        logger.error(f"Error getting latest sensor data: {str(e)}")
    return []

def add_sensor_data(data: dict) -> bool:
    """Ajoute une nouvelle mesure de capteur."""
    try:
        ref = db.reference('home_weather')
        timestamp = str(datetime.now().timestamp())
        ref.child(timestamp).set(data)
        return True
    except Exception as e:
        print(f"Erreur lors de l'ajout des données capteur: {e}")
        return False

def save_device_command(device_id: str, command: str, parameters: Dict = None) -> bool:
    """Save a device command to Firebase Realtime Database."""
    try:
        command_data = {
            'device_id': device_id,
            'command': command,
            'parameters': parameters or {},
            'timestamp': datetime_to_timestamp(datetime.now()),
            'status': 'pending'
        }
        
        command_ref = db.reference('/device_commands')
        command_ref.push(command_data)
        logger.info(f"Saved command {command} for device {device_id}")
        return True
    except Exception as e:
        logger.error(f"Error saving device command: {str(e)}")
        return False

def acknowledge_alert(alert_id: str) -> bool:
    """Acknowledge an alert in Firestore."""
    db = get_firestore_db()
    if not db:
        return False
    try:
        alert_ref = db.collection('alerts').document(alert_id)
        alert_ref.update({'acknowledged': True})
        return True
    except Exception as e:
        logger.error(f"Error acknowledging alert in Firestore: {e}")
    return False 

def get_historical_sensor_data(days: int = 7) -> list:
    """Récupère les données historiques des capteurs depuis Firebase RTDB."""
    try:
        if realtime_db:
            cutoff_time = datetime.now() - timedelta(days=days)
            cutoff_timestamp = datetime_to_timestamp(cutoff_time)
            data = realtime_db.child('home_weather')\
                .order_by_child('timestamp')\
                .start_at(cutoff_timestamp)\
                .get()
            if data:
                return [document_to_dict(doc) for doc in data.values()]
    except Exception as e:
        logger.error(f"Error getting historical sensor data: {str(e)}")
        return [] 