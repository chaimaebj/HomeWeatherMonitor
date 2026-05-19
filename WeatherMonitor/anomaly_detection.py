import pickle
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from firebase_db import get_historical_sensor_data
import os

# 1. Charger les données
print("Chargement des données pour détection d'anomalies...")
data = get_historical_sensor_data(days=30)
if not data:
    print("Aucune donnée historique récupérée (data est None ou vide). Vérifiez la présence de données dans /home_weather.")
    data = []

# Correction : supporte dict ou liste
if isinstance(data, dict):
    data_iter = data.values()
else:
    data_iter = data

X = []
for entry in data_iter:
    if all(k in entry for k in ['temperature', 'humidity', 'rain', 'gas']):
        X.append([
            float(entry['temperature']),
            float(entry['humidity']),
            float(entry['rain']),
            float(entry['gas'])
        ])
X = np.array(X)

if len(X) == 0:
    print("Pas de données suffisantes pour entraîner le modèle d'anomalie.")
    exit()

# 2. Entraîner IsolationForest
print('Entraînement IsolationForest...')
iso = IsolationForest(contamination=0.01, random_state=42)
iso.fit(X)
with open('anomaly_iforest.pkl', 'wb') as f:
    pickle.dump(iso, f)
print('Modèle IsolationForest sauvegardé sous anomaly_iforest.pkl')

# 3. Visualisation des anomalies
anomaly_pred = iso.predict(X)
plt.figure()
plt.scatter(range(len(X)), X[:,0], c=(anomaly_pred==-1), cmap='coolwarm', label='Anomalie')
plt.title('Détection d\'anomalies sur la température')
plt.xlabel('Index')
plt.ylabel('Température')
plt.legend(['Normal','Anomalie'])
plt.savefig('anomaly_detection_plot.png')
print('Graphique des anomalies sauvegardé : anomaly_detection_plot.png')

# 4. Fonction de détection en temps réel

def is_anomaly(new_entry):
    """
    new_entry: dict avec temperature, humidity, rain, gas
    Retourne True si anomalie détectée, False sinon
    """
    model_path = 'anomaly_iforest.pkl'
    if not os.path.exists(model_path):
        return False
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    X_new = np.array([[float(new_entry.get('temperature',0)),
                       float(new_entry.get('humidity',0)),
                       float(new_entry.get('rain',0)),
                       float(new_entry.get('gas',0))]])
    return model.predict(X_new)[0] == -1 