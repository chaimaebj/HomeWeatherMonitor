# Home Weather Monitor

Un système de surveillance météorologique domestique complet avec analyse de sécurité, prédictions et détection d'anomalies.

## 🌟 Caractéristiques

- 📊 **Dashboard en temps réel** : Visualisation interactive des données météorologiques
- 🤖 **Machine Learning** : Prédictions météo basées sur Random Forest
- 🚨 **Détection d'anomalies** : Algorithme Isolation Forest pour identifier les valeurs anormales
- 🔐 **Authentification** : Système de connexion/enregistrement sécurisé
- ☁️ **Firebase** : Base de données cloud avec Realtime Database et Firestore
- 📧 **Notifications** : Alertes par email et SMS (Vonage)
- 📈 **Analyse de performance** : Statistiques et rapports détaillés
- 🎨 **Interface responsive** : Design adaptatif pour tous les appareils

## 📋 Prérequis

- Python 3.8+
- pip ou conda
- Compte Firebase
- Compte Gmail (pour les notifications)
- Compte Vonage (optional pour SMS)

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/votre-username/HomeWeatherMonitor.git
cd HomeWeatherMonitor
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
cd WeatherMonitor
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

1. Copier le fichier `.env.example` en `.env` :
```bash
cp .env.example .env
```

2. Remplir les variables dans `.env` :

#### Configuration Firebase
- Aller sur [Firebase Console](https://console.firebase.google.com)
- Créer un nouveau projet
- Générer une clé de compte de service
- Télécharger `firebase_service_account.json`
- Placer le fichier dans le dossier `WeatherMonitor/`
- Copier les identifiants Firebase dans `.env`

#### Configuration Email (Gmail)
- Activer l'authentification à deux facteurs sur votre compte Gmail
- Générer un [mot de passe d'application](https://support.google.com/accounts/answer/185833)
- Ajouter dans `.env` :
```
MAIL_USERNAME=votre-email@gmail.com
MAIL_PASSWORD=votre-mot-de-passe-app
```

#### Configuration SMS (Optional)
- Créer un compte [Vonage](https://www.vonage.com/)
- Ajouter vos credentials dans `.env`

### 5. Initialiser la base de données

```bash
python database_init.py
```

### 6. Créer un compte administrateur

```bash
python create_admin.py
```

### 7. Lancer l'application

```bash
python app.py
```

L'application sera accessible à `http://localhost:5000`

## 📁 Structure du projet

```
HomeWeatherMonitor/
├── WeatherMonitor/          # Application principale
│   ├── models/             # Modèles de données
│   ├── static/             # CSS, JS, images
│   ├── templates/          # Templates HTML
│   ├── app.py             # Application Flask
│   ├── routes.py          # Routes de l'application
│   ├── auth.py            # Gestion authentification
│   ├── database.py        # ORM SQLAlchemy
│   ├── firebase_db.py     # Intégration Firebase
│   ├── prediction.py      # Modèles de prédiction
│   ├── anomaly_detection.py  # Détection d'anomalies
│   └── requirements.txt    # Dépendances Python
└── README.md             # Cette documentation
```

## 🔑 Utilisation

### Interface Web
- Accéder à `http://localhost:5000`
- Créer un compte ou se connecter
- Consulter le dashboard
- Visualiser les prédictions
- Configurer les alertes

### API REST

L'application expose plusieurs endpoints API :

```bash
# Obtenir les données actuelles
GET /api/weather

# Obtenir les prédictions
GET /api/predictions

# Ajouter une nouvelle mesure
POST /api/weather
```

## 🤖 Modèles Machine Learning

### Prédiction
- **Algorithme** : Random Forest
- **Données d'entraînement** : Données historiques
- **Paramètres prédits** : Température, Humidité, Pluie, Gaz

### Détection d'anomalies
- **Algorithme** : Isolation Forest
- **Détection** : Valeurs aberrantes en temps réel
- **Action** : Alertes utilisateur immédiate

## 🧪 Tests

```bash
# Tester la connexion à la base de données
python test_connection.py

# Tester Firebase
python test_firebase.py

# Entraîner les modèles de prédiction
python train_predictor.py
```

## 📊 Données supportées

- 🌡️ **Température** (°C)
- 💧 **Humidité** (%)
- 🌧️ **Pluie** (mm)
- 🌫️ **Qualité de l'air** (AQI)
- 💨 **Gaz** (PPM)

## 🔒 Sécurité

- Les données sensibles sont stockées dans `.env` (git-ignored)
- Authentification par email
- Validation des formulaires (CSRF protection)
- Hachage des mots de passe

## 🐛 Troubleshooting

### Erreur de connexion Firebase
- Vérifier que `firebase_service_account.json` est présent
- Vérifier les identifiants dans `.env`
- Vérifier les règles de sécurité Firebase

### Erreur d'email
- Vérifier l'authentification à deux facteurs Gmail
- Utiliser un mot de passe d'application
- Vérifier les paramètres SMTP

### Modèles non trouvés
- Exécuter `python train_predictor.py` pour entraîner

## 📝 Logs

Les logs sont sauvegardés dans le dossier `logs/`

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amazing-feature`)
3. Commiter vos changements (`git commit -m 'Add amazing feature'`)
4. Pusher vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

