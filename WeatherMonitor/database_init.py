import os
from firebase_admin import db
from firebase_config import initialize_firebase, get_firebase_config

# Initialize Firebase
initialize_firebase()

# Get database reference
db_ref = db.reference('/')

def get_db():
    """Get database reference."""
    return db_ref

def init_db():
    """Initialize database with required structure."""
    try:
        # Create basic structure if it doesn't exist
        if not db_ref.get():
            db_ref.set({
                'users': {},
                'devices': {},
                'home_weather': {},
                'alerts': {},
                'settings': {}
            })
            print("Database structure initialized successfully")
    except Exception as e:
        print(f"Error initializing database structure: {str(e)}")
        raise 