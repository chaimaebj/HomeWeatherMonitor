import os
import logging
from flask import Flask
from flask_login import LoginManager
from firebase_db import initialize_firebase, get_user_by_id
from routes import main as main_bp
from auth import auth_bp
from dotenv import load_dotenv
from datetime import datetime
from api import api_bp

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        USE_FIREBASE=True
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize Firebase
    try:
        initialize_firebase()
        logger.info("Firebase initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing Firebase: {str(e)}")
        raise

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        print(f"DEBUG: load_user called with user_id={user_id}")
        user = get_user_by_id(user_id)
        print(f"DEBUG: load_user returns {user}")
        return user

    @app.template_filter('timestamp_to_date')
    def timestamp_to_date_filter(ts, format='%Y-%m-%d %H:%M:%S'):
        try:
            # Si c'est déjà un datetime, retourne-le formaté
            if isinstance(ts, datetime):
                return ts.strftime(format)
            # Si c'est un timestamp en millisecondes
            ts = float(ts)
            if ts > 1e12:  # millisecondes
                ts = ts / 1000
            return datetime.fromtimestamp(ts).strftime(format)
        except Exception:
            return str(ts)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
