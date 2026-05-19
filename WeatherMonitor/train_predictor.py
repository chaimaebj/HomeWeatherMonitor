import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pickle
import os
from firebase_db import get_historical_sensor_data
from datetime import datetime, timedelta

def prepare_data(horizon_hours):
    """Prépare les données pour l'entraînement avec un horizon donné."""
    # Récupérer les données historiques
    data = get_historical_sensor_data(days=30)  # 30 jours de données
    
    if not data:
        raise ValueError("Pas assez de données pour l'entraînement")
    
    # Convertir en DataFrame
    df = pd.DataFrame(data)
    
    # Créer les features (X) et les targets (y)
    X = df[['humidity', 'rain', 'gas']].values
    y = {}
    
    # Pour chaque variable à prédire
    for var in ['temperature', 'humidity', 'rain', 'gas']:
        # Décaler les valeurs de l'horizon choisi
        y[var] = df[var].shift(-horizon_hours).values[:-horizon_hours]
    
    # Supprimer les dernières lignes qui n'ont pas de target
    X = X[:-horizon_hours]
    
    return X, y

def train_models():
    """Entraîne les modèles pour tous les horizons."""
    horizons = [6, 12, 24, 48]  # horizons en heures
    
    for horizon in horizons:
        print(f"Entraînement des modèles pour l'horizon {horizon}h...")
        
        try:
            # Préparer les données
            X, y = prepare_data(horizon)
            
            # Normaliser les features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Créer le dossier models s'il n'existe pas
            os.makedirs('models', exist_ok=True)
            
            # Entraîner un modèle pour chaque variable
            for var in ['temperature', 'humidity', 'rain', 'gas']:
                # Supprimer les lignes avec des valeurs NaN
                mask = ~np.isnan(y[var])
                X_train = X_scaled[mask]
                y_train = y[var][mask]
                
                if len(X_train) < 10:  # Vérifier qu'il y a assez de données
                    print(f"Pas assez de données pour entraîner le modèle {var} à {horizon}h")
                    continue
                
                # Créer et entraîner le modèle
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X_train, y_train)
                
                # Sauvegarder le modèle
                model_path = f'models/{var}_rf_model_{horizon}h.pkl'
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f)
                
                print(f"Modèle {var} pour {horizon}h sauvegardé")
            
            print(f"Entraînement terminé pour l'horizon {horizon}h")
            
        except Exception as e:
            print(f"Erreur lors de l'entraînement pour l'horizon {horizon}h: {str(e)}")

if __name__ == '__main__':
    train_models() 