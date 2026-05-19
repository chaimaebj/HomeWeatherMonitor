# Guide de Configuration - Home Weather Monitor

## 📋 Configuration Détaillée

### 1. Firebase Setup

#### Étape 1 : Créer un projet Firebase
1. Aller à [Firebase Console](https://console.firebase.google.com)
2. Cliquer sur "Créer un projet" 
3. Entrer le nom du projet (ex: `home-weather-monitor`)
4. Décocher "Activer Google Analytics"
5. Cliquer "Créer un projet"

#### Étape 2 : Activer Realtime Database
1. Dans le menu de gauche, aller à "Realtime Database"
2. Cliquer "Créer une base de données"
3. Choisir un emplacement
4. Sélectionner "Commencer en mode test" (pour développement)
5. Cliquer "Activer"

#### Étape 3 : Générer une clé de service
1. Aller à "Paramètres du projet" (roue dentée)
2. Aller à l'onglet "Comptes de service"
3. Cliquer "Générer une clé privée"
4. Un fichier JSON sera téléchargé
5. Renommer le fichier à `firebase_service_account.json`
6. Placer le fichier dans `WeatherMonitor/`

#### Étape 4 : Récupérer les variables Firebase
1. Aller à "Aperçu du projet"
2. Cliquer "Ajouter une application"
3. Sélectionner "Web"
4. Entrer un nom pour la web app
5. Copier les valeurs de `firebaseConfig` et les mettre dans `.env` :

```
FIREBASE_DATABASE_URL=https://xxx-default-rtdb.firebaseio.com
FIREBASE_PROJECT_ID=xxx
FIREBASE_STORAGE_BUCKET=xxx.appspot.com
FIREBASE_MESSAGING_SENDER_ID=xxx
FIREBASE_APP_ID=1:xxx:web:xxx
FIREBASE_MEASUREMENT_ID=G-xxx
```

### 2. Configuration Email (Gmail)

#### Activer l'authentification à deux facteurs

1. Aller à [myaccount.google.com](https://myaccount.google.com)
2. Sélectionner "Sécurité" dans le menu
3. Aller à "Authentification à deux facteurs"
4. Suivre les instructions pour l'activer

#### Générer un mot de passe d'application

1. Une fois 2FA activée, aller à [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Sélectionner "Mail" et "Windows Machine" (ou votre plateforme)
3. Cliquer "Générer"
4. Copier le mot de passe généré
5. Mettre dans `.env` :

```
MAIL_USERNAME=votre-email@gmail.com
MAIL_PASSWORD=mot-de-passe-app-16-caracteres
```

### 3. Configuration SMS - Vonage (Optional)

#### Créer un compte Vonage

1. Aller à [Vonage](https://www.vonage.com/)
2. Créer un compte gratuitement
3. Aller au dashboard
4. Créer une nouvelle application (Communication APIs)
5. Récupérer vos credentials :

```
VONAGE_API_KEY=votre-api-key
VONAGE_API_SECRET=votre-api-secret
VONAGE_PHONE_NUMBER=+212XXXXXXXXX
```

### 4. Configuration Flask

Générer une clé secrète pour Flask :

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Mettre la valeur générée dans `.env` :

```
SECRET_KEY=clé-générée-ici
```

### 5. Premier démarrage

```bash
cd WeatherMonitor

# Activer l'environnement virtuel
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Initialiser la base de données
python database_init.py

# Créer un administrateur
python create_admin.py

# Lancer l'application
python app.py
```

## ✅ Vérification

### Tester la connexion Firebase

```bash
python test_firebase_connection.py
```

### Tester la base de données

```bash
python test_connection.py
```

### Entraîner les modèles ML

```bash
python train_predictor.py
```

## 🚨 Erreurs courantes

### "ModuleNotFoundError: No module named 'firebase_admin'"
```bash
pip install firebase-admin python-dotenv flask-login
```

### "firebase_service_account.json not found"
- Vérifier que le fichier est dans le bon dossier
- Vérifier qu'il n'est pas ignoré par `.gitignore`

### Erreur SMTP (Email)
- Vérifier 2FA Gmail est activé
- Vérifier le mot de passe d'application (pas le mot de passe normal)
- Vérifier que `MAIL_PORT=587` et non 465

### Port 5000 déjà utilisé
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID xxx /F

# macOS/Linux
lsof -i :5000
kill -9 xxx
```

## 🔄 Mise à jour de dépendances

```bash
pip install --upgrade -r requirements.txt
```

## 📦 Distribution

Pour créer un fichier requirements mis à jour :

```bash
pip freeze > requirements.txt
```

---

Pour plus d'aide, consultez le [README.md](README.md)
