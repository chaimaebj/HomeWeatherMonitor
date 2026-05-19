from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Tuple, Optional
import pickle
import os

class WeatherPredictor:
    def __init__(self, sensor_data: List[Dict]):
        print(f"DEBUG: WeatherPredictor received sensor_data with {len(sensor_data)} entries.")
        self.sensor_data = sensor_data
        self.temperature_threshold = 30  # °C
        self.humidity_threshold = 70     # %
        self.air_quality_threshold = 100 # ppm
        # Chargement des modèles entraînés
        self.models = {}
        for label in ['temperature', 'humidity', 'rain', 'gas']:
            model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', f'{label}_rf_model.pkl')
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.models[label] = pickle.load(f)

    def get_24h_data(self) -> Dict[str, List[Tuple[datetime, float]]]:
        """Récupère les données des dernières 24h pour chaque capteur."""
        now = datetime.now()
        day_ago = now - timedelta(days=1)
        
        data = {
            'temperature': [],
            'humidity': [],
            'rain': [],
            'gas': []
        }
        
        for reading in self.sensor_data:
            try:
                timestamp = reading.get('timestamp')
                if not isinstance(timestamp, datetime):
                    # Attempt to convert if it's a timestamp from firebase_db.py's get_historical_sensor_data
                    # This should ideally already be a datetime object from firebase_db.py's document_to_dict
                    # but adding a safeguard for flexibility.
                    if isinstance(timestamp, (int, float)):
                        timestamp = datetime.fromtimestamp(timestamp / 1000) 
                    else:
                        continue # Skip if timestamp is not a datetime or valid number

                if timestamp >= day_ago:
                    for sensor in data.keys():
                        if sensor in reading and reading[sensor] is not None:
                            data[sensor].append((timestamp, float(reading[sensor])))
            except (ValueError, TypeError) as e:
                print(f"Error processing sensor data entry: {reading} - {e}")
                continue
                
        # Trier par timestamp
        for sensor in data:
            data[sensor].sort(key=lambda x: x[0])
            
        return data

    def calculate_averages(self) -> Dict[str, float]:
        """Calcule les moyennes sur 24h pour chaque capteur."""
        data = self.get_24h_data()
        averages = {}
        
        for sensor, values in data.items():
            if values:
                averages[sensor] = np.mean([v[1] for v in values])
            else:
                averages[sensor] = None
                
        return averages

    def predict_weather(self) -> Dict[str, str]:
        """Fait des prédictions basées sur les données actuelles et historiques."""
        data = self.get_24h_data()
        averages = self.calculate_averages()
        
        predictions = {
            'temperature_trend': self._predict_temperature_trend(data['temperature']),
            'rain_probability': self._predict_rain_probability(data['rain']),
            'gas_forecast': self._predict_gas(data['gas']),
            'comfort_level': self._calculate_comfort_level(
                averages.get('temperature'),
                averages.get('humidity')
            )
        }
        
        return predictions

    def _predict_temperature_trend(self, temp_data: List[Tuple[datetime, float]]) -> str:
        """Prédit la tendance de température."""
        if len(temp_data) < 2:
            return "Données insuffisantes"
            
        recent_temps = [t[1] for t in temp_data[-6:]]  # Dernières 6 mesures
        if len(recent_temps) < 2:
            return "Données insuffisantes"
            
        slope = np.polyfit(range(len(recent_temps)), recent_temps, 1)[0]
        
        if slope > 0.5:
            return "Augmentation rapide"
        elif slope > 0:
            return "Légère augmentation"
        elif slope < -0.5:
            return "Diminution rapide"
        else:
            return "Légère diminution"

    def _predict_rain_probability(self, rain_data: List[Tuple[datetime, float]]) -> str:
        """Calcule la probabilité de pluie."""
        if not rain_data:
            return "Données insuffisantes"
            
        recent_rain = [r[1] for r in rain_data[-12:]]  # Dernières 12 mesures
        rain_count = sum(1 for r in recent_rain if r > 0)
        
        probability = (rain_count / len(recent_rain)) * 100
        
        if probability > 70:
            return "Forte probabilité de pluie"
        elif probability > 30:
            return "Risque de pluie modéré"
        else:
            return "Peu de risque de pluie"

    def _predict_gas(self, gas_data: List[Tuple[datetime, float]]) -> str:
        if not gas_data:
            return "Données insuffisantes"
        recent_gas = [a[1] for a in gas_data[-6:]]
        avg_gas = np.mean(recent_gas)
        if avg_gas > self.air_quality_threshold * 1.5:
            return "Mauvaise qualité de l'air"
        elif avg_gas > self.air_quality_threshold:
            return "Qualité de l'air moyenne"
        else:
            return "Bonne qualité de l'air"

    def _calculate_comfort_level(self, temp: Optional[float], humidity: Optional[float]) -> str:
        """Calcule le niveau de confort basé sur température et humidité."""
        if temp is None or humidity is None:
            return "Données insuffisantes"
            
        # Calcul de l'indice de chaleur (formule simplifiée)
        heat_index = temp + 0.33 * humidity - 0.7
        
        if heat_index > 30:
            return "Inconfortable (chaleur)"
        elif heat_index < 15:
            return "Inconfortable (froid)"
        else:
            return "Confortable"

    def get_chart_data(self) -> Dict[str, Dict]:
        """Prépare les données pour les graphiques."""
        data = self.get_24h_data()
        chart_data = {}
        
        for sensor, values in data.items():
            if values:
                chart_data[sensor] = {
                    'timestamps': [v[0].strftime('%H:%M') for v in values],
                    'values': [v[1] for v in values]
                }
            else:
                chart_data[sensor] = {
                    'timestamps': [],
                    'values': []
                }
                
        return chart_data

    def predict_all(self, input_dict):
        """
        Prend un dict {'humidity':..., 'rain':..., 'gas':...}
        Retourne un dict de prédictions pour chaque variable.
        """
        X = np.array([[float(input_dict.get('humidity', 0)),
                       float(input_dict.get('rain', 0)),
                       float(input_dict.get('gas', 0))]])
        preds = {}
        for label, model in self.models.items():
            preds[label] = float(model.predict(X)[0])
        return preds

def predict_multi_horizon(input_dict, horizon_hours):
    """
    Prédit température, humidité, pluie, gaz à l'horizon donné (en heures).
    input_dict : dict avec les valeurs actuelles {'humidity':..., 'rain':..., 'gas':...}
    horizon_hours : int (6, 12, 24, 48)
    """
    preds = {}
    for var in ['temperature', 'humidity', 'rain', 'gas']:
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', f'{var}_rf_model_{horizon_hours}h.pkl')
        if not os.path.exists(model_path):
            print(f"DEBUG: Model not found at {model_path}")
            preds[var] = None
            continue
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            X = np.array([[float(input_dict.get('humidity', 0)),
                           float(input_dict.get('rain', 0)),
                           float(input_dict.get('gas', 0))]])
            preds[var] = float(model.predict(X)[0])
            print(f"DEBUG: Successfully predicted {var} for {horizon_hours}h")
        except Exception as e:
            print(f"DEBUG: Error predicting {var} for {horizon_hours}h: {str(e)}")
            preds[var] = None
    return preds 