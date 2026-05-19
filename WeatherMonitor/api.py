from flask import Blueprint, request, jsonify, current_app
from firebase_models import SensorData, DeviceCommand
from utils import check_thresholds_and_alert, clean_old_data
from datetime import datetime
import logging
import json

# Configure logger
logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__)

# API KEY for device validation (should be stored securely in production)
API_KEY = "A1B2-C3D4-E5F6-G7H8"  # In production, use environment variables

@api_bp.route('/data', methods=['POST'])
def receive_data():
    """
    Endpoint for receiving sensor data from ESP8266
    Expects JSON in the format:
    {
        "api_key": "YOUR_API_KEY",
        "device_id": "esp8266_1",
        "temperature": 23.5,
        "humidity": 45.2,
        "rain_detected": false,
        "air_quality": 125.0
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
        api_key = data.get('api_key')
        if api_key != API_KEY:
            logger.warning(f"Invalid API key attempt from IP: {request.remote_addr}")
            return jsonify({"status": "error", "message": "Invalid API key"}), 401
        device_id = data.get('device_id')
        if not device_id:
            return jsonify({"status": "error", "message": "No device_id provided"}), 400
        # Vérifier si le device existe dans Firebase, sinon le créer
        device = Device.get_by_id(device_id) if hasattr(Device, 'get_by_id') else None
        if not device:
            device = Device(
                device_id=device_id,
                name=f"Device {device_id}",
                type='sensor',
                status='online'
            )
            device.last_seen = datetime.utcnow()
            device.save()
        else:
            device.status = 'online'
            device.last_seen = datetime.utcnow()
            device.save()
        # Créer et sauvegarder les données capteurs dans Firebase
        sensor_data = SensorData(
            device_id=device_id,
            temperature=data.get('temperature'),
            humidity=data.get('humidity'),
            rain_detected=data.get('rain_detected', False),
            air_quality=data.get('air_quality')
        )
        sensor_data.save()
        # Check thresholds and trigger alerts if needed
        check_thresholds_and_alert()
        # Periodically clean old data
        clean_old_data()
        return jsonify({
            "status": "success",
            "message": "Data received",
            "data_id": getattr(sensor_data, 'id', None)
        })
    except Exception as e:
        logger.error(f"Error processing sensor data: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@api_bp.route('/command/<device_id>', methods=['GET'])
def get_pending_commands(device_id):
    """
    Endpoint for devices to check for pending commands
    Returns the oldest unexecuted command for the device
    """
    try:
        api_key = request.args.get('api_key')
        if api_key != API_KEY:
            logger.warning(f"Invalid API key attempt from IP: {request.remote_addr}")
            return jsonify({"status": "error", "message": "Invalid API key"}), 401
        # Récupérer la plus ancienne commande non exécutée depuis Firebase
        if hasattr(DeviceCommand, 'get_pending_for_device'):
            command = DeviceCommand.get_pending_for_device(device_id)
        else:
            command = None
        if not command:
            return jsonify({"status": "success", "command": None})
        # Marquer comme exécutée si la méthode existe
        if hasattr(command, 'mark_executed'):
            command.mark_executed()
        elif hasattr(command, 'executed'):
            command.executed = True
            command.save()
        return jsonify({
            "status": "success",
            "command": {
                "id": getattr(command, 'id', None),
                "command": getattr(command, 'command', None),
                "parameters": getattr(command, 'get_parameters', lambda: None)(),
                "timestamp": getattr(command, 'timestamp', None).isoformat() if getattr(command, 'timestamp', None) else None
            }
        })
    except Exception as e:
        logger.error(f"Error retrieving commands: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@api_bp.route('/data/<device_id>', methods=['GET'])
def get_device_data(device_id):
    """
    Endpoint to get device data for API consumption
    Requires API key auth
    """
    try:
        api_key = request.args.get('api_key')
        if api_key != API_KEY:
            logger.warning(f"Invalid API key attempt from IP: {request.remote_addr}")
            return jsonify({"status": "error", "message": "Invalid API key"}), 401
        limit = request.args.get('limit', 100, type=int)
        # Récupérer les données capteurs depuis Firebase
        if hasattr(SensorData, 'get_latest'):
            data = SensorData.get_latest(device_id, limit=limit)
        else:
            data = []
        result = [d.to_dict() for d in data] if data else []
        return jsonify({
            "status": "success",
            "device_id": device_id,
            "count": len(result),
            "data": result
        })
    except Exception as e:
        logger.error(f"Error retrieving device data: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
