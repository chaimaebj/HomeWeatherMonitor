import logging
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, abort, current_app
from flask_login import login_required, current_user
from database_init import get_db
from firebase_db import (
    get_all_sensor_data_for_charts, get_alerts, get_user_settings, save_user_settings,
    save_device_command, acknowledge_alert, get_latest_sensor_data, get_historical_sensor_data,
    create_alert, get_all_users, save_sensor_data
)
from forms import SettingsForm, PredictionForm
from utils import get_historical_data, send_email_alert, send_sms_alert, send_alert_in_background
from datetime import datetime, timedelta
from prediction import WeatherPredictor, predict_multi_horizon
from anomaly_detection import is_anomaly

# Configure logger
logger = logging.getLogger(__name__)

# Create blueprint
main = Blueprint('main', __name__)

# Context processor to add variables to all templates
@main.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    # Récupérer les dernières données des capteurs
    latest_data = get_all_sensor_data_for_charts()
    # Prendre la dernière mesure (la plus récente)
    current = latest_data[-1] if latest_data else {}
    
    # Récupérer les alertes depuis Firestore
    # La fonction get_alerts retourne maintenant une liste d'objets FirestoreAlert
    recent_alerts_objects = get_alerts(limit=5)
    
    # Convertir les objets en dictionnaires pour le template
    recent_alerts = [alert.__dict__ for alert in recent_alerts_objects]
    
    capteurs = [
        {"nom": "Salon", "lat": 33.5731, "lng": -7.5898, "temp": 24.5},
        {"nom": "Jardin", "lat": 33.5800, "lng": -7.6000, "temp": 22.1},
        {"nom": "Chambre", "lat": 33.5700, "lng": -7.5800, "temp": 23.3},
    ]
    return render_template('dashboard.html', title='Dashboard', data=current, data_list=latest_data, capteurs=capteurs, recent_alerts=recent_alerts)

@main.route('/alerts')
@login_required
def alerts():
    # Get all alerts from Firestore
    all_alerts_objects = get_alerts(limit=50) # Get more for the alerts page
    
    # Group alerts by date
    alerts_by_date = {}
    for alert in all_alerts_objects:
        # alert.timestamp est maintenant un objet datetime
        dt_object = alert.timestamp
        date_str = dt_object.strftime('%Y-%m-%d')
        if date_str not in alerts_by_date:
            alerts_by_date[date_str] = []
        
        # Convertir l'objet en dictionnaire pour le template
        alerts_by_date[date_str].append(alert.__dict__)
    
    return render_template('alerts.html', title='Alerts', alerts_by_date=alerts_by_date)

@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        settings = {
            'email_alerts': form.email_alerts.data,
            'sms_alerts': form.sms_alerts.data,
            'phone_number': form.phone_number.data,
            'temperature_alert_min': form.temperature_alert_min.data,
            'temperature_alert_max': form.temperature_alert_max.data,
            'humidity_alert_min': form.humidity_alert_min.data,
            'humidity_alert_max': form.humidity_alert_max.data,
            'air_quality_alert': form.air_quality_alert.data
        }
        if save_user_settings(current_user.id, settings):
            flash('Your settings have been updated.')
            return redirect(url_for('main.dashboard'))
        flash('Error saving settings')
    else:
        current_settings = get_user_settings(current_user.id)
        if current_settings:
            form.email_alerts.data = current_settings.get('email_alerts', False)
            form.sms_alerts.data = current_settings.get('sms_alerts', False)
            form.phone_number.data = current_settings.get('phone_number', '')
            form.temperature_alert_min.data = current_settings.get('temperature_alert_min', 10.0)
            form.temperature_alert_max.data = current_settings.get('temperature_alert_max', 30.0)
            form.humidity_alert_min.data = current_settings.get('humidity_alert_min', 30.0)
            form.humidity_alert_max.data = current_settings.get('humidity_alert_max', 70.0)
            form.air_quality_alert.data = current_settings.get('air_quality_alert', 100.0)
    return render_template('settings.html', title='Settings', form=form)

@main.route('/alert/acknowledge/<alert_id>', methods=['POST'])
@login_required
def acknowledge_alert_route(alert_id):
    if acknowledge_alert(alert_id):
        flash('Alert acknowledged.', 'success')
    else:
        flash('Error acknowledging alert.', 'danger')
    
    # Get the next page from form or go to alerts page
    next_page = request.form.get('next') or url_for('main.alerts')
    return redirect(next_page)

@main.route('/predictions', methods=['GET', 'POST'])
@login_required
def predictions():
    print(f"DEBUG: Entering predictions route. Request method: {request.method}")
    form = PredictionForm()
    historical_data = []
    advanced_predictions = None
    anomaly = None
    if form.validate_on_submit():
        print("DEBUG: Form validated successfully.")
        days = form.hours.data / 24  # Convertit les heures en jours
        historical_data = get_historical_data(days=days)
        print("DEBUG: Historical data fetched:", historical_data)
        # Prévision avancée RandomForest multi-horizon
        if historical_data:
            last = historical_data[-1]
            input_data = {
                'humidity': last.get('humidity', 50),
                'rain': last.get('rain', 0),
                'gas': last.get('gas', 100)
            }
            advanced_predictions = predict_multi_horizon(input_data, int(form.hours.data))
            anomaly = is_anomaly(last)
    else:
        print("DEBUG: Form validation failed.")
        print("DEBUG: Form errors:", form.errors)
    return render_template(
        'predictions_new.html',
        title='Weather Predictions',
        form=form,
        advanced_predictions=advanced_predictions,
        anomaly=anomaly,
        historical_data=historical_data
    )

@main.route('/api/sensor_data', methods=['POST'])
def add_sensor_reading():
    print("DEBUG: add_sensor_reading appelée")
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['device_id', 'temperature', 'humidity', 'air_quality', 'rain']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # --- Interprétation du capteur de pluie ---
        rain_value = data.get('rain')
        rain_status = "Inconnu"
        if rain_value is not None:
            if 0 <= rain_value <= 300:
                rain_status = "Forte pluie"
            elif 301 <= rain_value <= 700:
                rain_status = "Pluie légère"
            elif 701 <= rain_value <= 1023:
                rain_status = "Sec"
        data['rain_status'] = rain_status
        # --- Fin de l'interprétation ---

        # The timestamp will be added by the save_sensor_data function
        
        # Save to Firebase
        # Using the firebase_db helper now
        save_sensor_data(data.get('device_id'), data)
        
        # --- Start Alerting Logic ---
        
        # For this simplified implementation, we'll send alerts to the first user found.
        all_users = get_all_users()
        if not all_users:
            return jsonify({'message': 'Data saved, no users to alert'}), 200
            
        main_user = all_users[0]
        user_settings = get_user_settings(main_user.id)
        if not user_settings:
            user_settings = {} # Ensure user_settings is a dict

        # --- Notification Cooldown Logic ---
        notification_cooldown_minutes = 30 # Cooldown period for notifications of the same type
        last_notifications = user_settings.get('last_notification_times', {})
        
        def should_send_notification(alert_type):
            last_time_str = last_notifications.get(alert_type)
            if not last_time_str:
                return True
            last_time = datetime.fromisoformat(last_time_str)
            if datetime.utcnow() > last_time + timedelta(minutes=notification_cooldown_minutes):
                return True
            return False

        def record_notification_sent(alert_type):
            last_notifications[alert_type] = datetime.utcnow().isoformat()
            save_user_settings(main_user.id, {'last_notification_times': last_notifications})

        # --- Alert Checks ---

        # 1. Check for anomalies
        if is_anomaly(data):
            alert_message = f"Anomaly detected. Values: Temp={data['temperature']}, Humidity={data['humidity']}, Gas={data.get('gas', 'N/A')}"
            alert_type = 'anomaly'
            print("DEBUG: Je vais créer une alerte de type", alert_type, "pour", data['device_id'])
            create_alert(data['device_id'], alert_type, alert_message)
            logger.info(f"Anomaly alert created for device {data['device_id']}")
            
            if should_send_notification(alert_type):
                if user_settings.get('email_alerts'):
                    send_alert_in_background(current_app._get_current_object(), send_email_alert, recipient=main_user.email, subject=f"Anomaly Alert for {data['device_id']}", message=alert_message)
                if user_settings.get('sms_alerts') and user_settings.get('phone_number'):
                    send_alert_in_background(current_app._get_current_object(), send_sms_alert, phone_number=user_settings['phone_number'], message=alert_message)
                record_notification_sent(alert_type)

        # 2. Check for user-defined thresholds
        # Check temperature
        temp = data.get('temperature')
        if temp is not None:
            if user_settings.get('temperature_alert_max') and temp > user_settings.get('temperature_alert_max'):
                alert_type = 'high_temperature'
                alert_message = f"High temperature alert: {temp}°C (threshold: {user_settings.get('temperature_alert_max')}°C)"
                print("DEBUG: Je vais créer une alerte de type", alert_type, "pour", data['device_id'])
                create_alert(data['device_id'], alert_type, alert_message)
                if should_send_notification(alert_type):
                    if user_settings.get('email_alerts'): send_alert_in_background(current_app._get_current_object(), send_email_alert, recipient=main_user.email, subject="High Temperature Alert", message=alert_message)
                    record_notification_sent(alert_type)
            
            elif user_settings.get('temperature_alert_min') and temp < user_settings.get('temperature_alert_min'):
                alert_type = 'low_temperature'
                alert_message = f"Low temperature alert: {temp}°C (threshold: {user_settings.get('temperature_alert_min')}°C)"
                print("DEBUG: Je vais créer une alerte de type", alert_type, "pour", data['device_id'])
                create_alert(data['device_id'], alert_type, alert_message)
                if should_send_notification(alert_type):
                    if user_settings.get('email_alerts'): send_alert_in_background(current_app._get_current_object(), send_email_alert, recipient=main_user.email, subject="Low Temperature Alert", message=alert_message)
                    record_notification_sent(alert_type)
        
        # 3. Check for Rain
        rain_value = data.get('rain')
        if rain_value is not None and rain_value <= 700: # Alert on light or heavy rain
            alert_type = 'rain_detected'
            alert_message = f"Rain detected: {data['rain_status']} (Raw value: {rain_value})"
            print("DEBUG: Je vais créer une alerte de type", alert_type, "pour", data['device_id'])
            create_alert(data['device_id'], alert_type, alert_message)
            if should_send_notification(alert_type):
                if user_settings.get('email_alerts'):
                    send_alert_in_background(current_app._get_current_object(), send_email_alert, recipient=main_user.email, subject="Rain Alert", message=alert_message)
                if user_settings.get('sms_alerts') and user_settings.get('phone_number'):
                    send_alert_in_background(current_app._get_current_object(), send_sms_alert, phone_number=user_settings['phone_number'], message=alert_message)
                record_notification_sent(alert_type)

        return jsonify({'message': 'Data saved and alerts checked'}), 200
    except Exception as e:
        logger.error(f"Error saving sensor data: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@main.route('/api/sensor-data/latest')
@login_required
def get_latest_data():
    try:
        data = get_latest_sensor_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/sensor-data/historical')
@login_required
def api_get_historical_data():
    try:
        days = request.args.get('days', default=7, type=int)
        data = get_historical_sensor_data(days)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/predictions')
@login_required
def get_predictions():
    try:
        # Get historical data for predictions
        data = get_historical_sensor_data(days=1)
        
        # Create predictor and get predictions
        predictor = WeatherPredictor(data)
        predictions = predictor.predict_weather()
        
        return jsonify(predictions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/anomalies')
@login_required
def anomalies():
    # Récupère les 50 dernières mesures
    data = get_historical_sensor_data(days=3) or []
    # Pour chaque mesure, détecte si anomalie
    anomalies_list = []
    for entry in data:
        anomalies_list.append(is_anomaly(entry))
    # On zippe pour le template
    mesures_anomalies = list(zip(data, anomalies_list))
    return render_template('anomalies.html', title='Détection d\'anomalies', mesures_anomalies=mesures_anomalies)
