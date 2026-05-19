import logging
from WeatherMonitor.firebase_db import test_connection, realtime_db
from WeatherMonitor.firebase_models import User, Device, SensorData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_firebase_connection():
    """Test the Firebase Realtime Database connection."""
    logger.info("Testing Firebase connection...")
    if test_connection():
        logger.info("✅ Firebase connection successful!")
        return True
    else:
        logger.error("❌ Firebase connection failed!")
        return False

def test_user_operations():
    """Test user operations."""
    logger.info("Testing user operations...")
    try:
        # Create a test user
        user = User(
            username="test_user",
            email="test@example.com",
            password_hash="test_hash"
        )
        if user.save():
            logger.info("✅ User created successfully!")
            
            # Test retrieving user
            retrieved_user = User.get_by_email("test@example.com")
            if retrieved_user and retrieved_user.username == "test_user":
                logger.info("✅ User retrieval successful!")
            else:
                logger.error("❌ User retrieval failed!")
            
            # Clean up
            if realtime_db:
                realtime_db.child('users').child(user.id).delete()
                logger.info("Test user cleaned up")
        else:
            logger.error("❌ User creation failed!")
    except Exception as e:
        logger.error(f"❌ User operations test failed: {str(e)}")

def test_sensor_data_operations():
    """Test sensor data operations."""
    logger.info("Testing sensor data operations...")
    try:
        # Create test sensor data
        sensor_data = SensorData(
            device_id="test_device_123",
            sensor_type="temperature",
            value=25.5,
            unit="°C"
        )
        if sensor_data.save():
            logger.info("✅ Sensor data saved successfully!")
            
            # Test retrieving sensor data
            latest_data = SensorData.get_latest("test_device_123", limit=1)
            if latest_data and len(latest_data) > 0:
                logger.info("✅ Sensor data retrieval successful!")
            else:
                logger.error("❌ Sensor data retrieval failed!")
            
            # Clean up
            if realtime_db:
                realtime_db.child('sensor_data').child(sensor_data.id).delete()
                logger.info("Test sensor data cleaned up")
        else:
            logger.error("❌ Sensor data save failed!")
    except Exception as e:
        logger.error(f"❌ Sensor data operations test failed: {str(e)}")

def run_all_tests():
    """Run all Firebase tests."""
    if test_firebase_connection():
        test_user_operations()
        test_sensor_data_operations()
    else:
        logger.error("Skipping other tests due to connection failure")

if __name__ == "__main__":
    run_all_tests() 