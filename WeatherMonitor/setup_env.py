import os
import json
from pathlib import Path

def setup_environment():
    """Set up environment variables for the application."""
    # Get the project root directory
    project_root = Path(__file__).parent
    
    # Create .env file if it doesn't exist
    env_file = project_root / '.env'
    if not env_file.exists():
        # Get Firebase configuration from service account
        service_account_path = project_root / 'firebase_service_account.json'
        if service_account_path.exists():
            with open(service_account_path) as f:
                service_account = json.load(f)
                
            # Create .env content
            env_content = f"""# Firebase Configuration
FIREBASE_API_KEY=your_api_key_here
FIREBASE_AUTH_DOMAIN={service_account['project_id']}.firebaseapp.com
FIREBASE_PROJECT_ID={service_account['project_id']}
FIREBASE_STORAGE_BUCKET={service_account['project_id']}.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your_sender_id_here
FIREBASE_APP_ID=your_app_id_here
FIREBASE_DATABASE_URL=https://{service_account['project_id']}-default-rtdb.firebaseio.com

# Flask Configuration
SECRET_KEY=your_secret_key_here
DEBUG=True

# Email Configuration (if needed)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_email_password

# Vonage Configuration (if needed)
VONAGE_API_KEY=your_vonage_api_key
VONAGE_API_SECRET=your_vonage_api_secret
VONAGE_PHONE_NUMBER=your_vonage_number
"""
            # Write .env file
            with open(env_file, 'w') as f:
                f.write(env_content)
            print(f"Created .env file at {env_file}")
            print("Please update the .env file with your actual configuration values")
        else:
            print("Error: firebase_service_account.json not found")
            print("Please ensure you have downloaded the service account file from Firebase Console")
    else:
        print(".env file already exists")

if __name__ == '__main__':
    setup_environment() 