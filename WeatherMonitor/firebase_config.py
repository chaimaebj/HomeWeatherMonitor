import os
import logging
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db, firestore
from flask import current_app

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_firebase_config():
    """Get Firebase configuration from environment variables."""
    config = {
        'databaseURL': os.getenv('FIREBASE_DATABASE_URL'),
        'projectId': os.getenv('FIREBASE_PROJECT_ID'),
        'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
        'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        'appId': os.getenv('FIREBASE_APP_ID')
}

    # Validate required configuration
    missing_configs = [k for k, v in config.items() if not v]
    if missing_configs:
        raise ValueError(f"Missing required Firebase configuration: {', '.join(missing_configs)}")
    
    return config

def initialize_firebase():
    """Initialize Firebase connection with proper error handling."""
    try:
        if not firebase_admin._apps:
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
            test_connection()
            
            logger.info("Firebase initialized successfully")
            return True
            
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {str(e)}")
        raise

def test_connection():
    """Test the Firebase connection by writing and reading a test value."""
    try:
        db_ref = db.reference()
        test_ref = db_ref.child('test_connection')
        
        # Write test data
        test_data = {'timestamp': firebase_admin.db.ServerValue.TIMESTAMP}
        test_ref.set(test_data)
        
        # Read test data
        result = test_ref.get()
        
        # Clean up
        test_ref.delete()
        
        if result is None:
            raise Exception("Failed to read test data from Firebase")
            
        logger.info("Firebase connection test successful")
        return True
        
    except Exception as e:
        logger.error(f"Firebase connection test failed: {str(e)}")
        raise

def get_realtime_db():
    """Get a reference to the Firebase Realtime Database."""
    try:
        return db.reference('/')
    except Exception as e:
        logger.error(f"Error accessing Realtime Database: {str(e)}")
        raise

def get_firestore_db():
    """Get a reference to Firestore."""
    try:
        return firestore.client()
    except Exception as e:
        logger.error(f"Error accessing Firestore: {str(e)}")
        raise 