# 📤 Guide de Publication sur GitHub

## Étape 1 : Créer un compte GitHub

1. Aller sur [GitHub.com](https://github.com)
2. Cliquer "Sign up"
3. Créer votre compte gratuitement
4. Vérifier votre email

## Étape 2 : Créer un nouveau repository

1. Une fois connecté, cliquer sur `+` en haut à droite
2. Sélectionner "New repository"
3. Remplir les détails :
   - **Repository name** : `HomeWeatherMonitor`
   - **Description** : `A comprehensive home weather monitoring system with ML predictions and anomaly detection`
   - **Public** ou **Private** : À votre choix
   - **Do NOT** initialiser avec README, .gitignore, ou License (vous les avez déjà)
4. Cliquer "Create repository"

## Étape 3 : Configurer Git localement

### Si vous n'avez jamais utilisé Git :

```bash
# Installer Git depuis https://git-scm.com/

# Configurer votre identité
git config --global user.name "Votre Nom"
git config --global user.email "votre-email@example.com"

# Vérifier la configuration
git config --global --list
```

## Étape 4 : Préparer votre repository local

### 4.1 Vérifier le `.gitignore`

```bash
cd c:\Users\chaimae\Downloads\HomeWeatherMonitor4\HomeWeatherMonitor

# Vérifier que les fichiers sensibles sont ignorés
git status

# Les fichiers suivants ne doivent PAS apparaître :
# - .env
# - firebase_service_account.json
# - venv/
# - *.pkl
# - __pycache__/
```

### 4.2 Vérifier les fichiers à commiter

```bash
# Voir le statut
git status

# Devrait voir :
# .gitignore (créé)
# README.md (créé)
# SETUP.md (créé)
# LICENSE (créé)
# WeatherMonitor/.env.example (créé)
# + tous les fichiers .py, templates, etc.
```

### 4.3 Ajouter les fichiers au staging

```bash
# Ajouter tous les fichiers sauf les ignorés
git add .

# Vérifier ce qui sera commité
git status
```

### 4.4 Commiter les changements

```bash
git commit -m "Initial commit: Add Home Weather Monitor project"
```

## Étape 5 : Connecter à votre repository GitHub

### 5.1 Ajouter l'origin (URL du repository)

```bash
# Remplacer YOUR_USERNAME et YOUR_REPO par vos valeurs
git remote add origin https://github.com/YOUR_USERNAME/HomeWeatherMonitor.git

# Vérifier l'ajout
git remote -v
```

Vous devriez voir :
```
origin  https://github.com/YOUR_USERNAME/HomeWeatherMonitor.git (fetch)
origin  https://github.com/YOUR_USERNAME/HomeWeatherMonitor.git (push)
```

### 5.2 Configurer la branche par défaut

```bash
git branch -M main
```

## Étape 6 : Authentification GitHub

### Option 1 : Token Personnel (Recommandé en 2026)

1. Aller sur GitHub → Settings → Developer settings → Personal access tokens
2. Cliquer "Generate new token (classic)"
3. Cocher les permissions :
   - `repo` (accès complet)
   - `workflow` (GitHub Actions)
4. Générer le token
5. **Copier et sauvegarder le token en lieu sûr** (vous ne le verrez qu'une fois)

### Option 2 : SSH (Avancé)

```bash
ssh-keygen -t ed25519 -C "votre-email@example.com"
# Ajouter la clé publique dans GitHub Settings → SSH and GPG keys
```

## Étape 7 : Pusher le code

```bash
# Première fois : il demandera votre authentification
git push -u origin main

# Pour les push suivants :
git push origin main
```

**Windows PowerShell** : Il ouvrira une fenêtre pour entrer vos credentials.
- Utiliser votre username GitHub
- Remplacer le mot de passe par le token créé à l'étape 6

## Étape 8 : Vérifier sur GitHub

1. Aller sur votre repository GitHub
2. Vérifier que les fichiers sont présents
3. Vérifier que `.env` et `firebase_service_account.json` ne sont **PAS** présents
4. Vérifier que le README s'affiche correctement

## ✅ Workflow futur

### Après chaque modification :

```bash
# 1. Voir les changements
git status

# 2. Ajouter les fichiers
git add .

# 3. Commiter avec un message descriptif
git commit -m "Description des changements"

# 4. Pusher
git push origin main
```

### Bonnes pratiques pour les commits

```bash
# ✅ Bon
git commit -m "Add user authentication system"
git commit -m "Fix: Correct Firebase connection timeout"
git commit -m "Docs: Update installation instructions"

# ❌ Mauvais
git commit -m "fix"
git commit -m "changes"
git commit -m "lalala"
```

## 🚨 ATTENTION : Fichiers Sensibles Déjà Commitées ?

Si vous avez accidentellement commité `.env` ou `firebase_service_account.json` :

### Nettoyer l'historique git

```bash
# Supprimer du dernier commit (si non pushé)
git rm --cached .env firebase_service_account.json
git commit --amend -m "Remove sensitive files"

# Supprimer complètement de l'historique (si déjà pushé)
# ⚠️ Ceci réécrit l'historique - faire avec précaution
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env firebase_service_account.json" \
  --prune-empty --tag-name-filter cat -- --all

# Forcer le push (refuser les changements à distance)
git push origin --force --all
```

**Alors, RÉVOQUÉS LES CREDENTIALS COMPROMIS** sur Firebase, Gmail, etc.

## 📝 Ajouter des collaborateurs

1. Aller dans Settings du repository
2. Aller à "Collaborators"
3. Cliquer "Add people"
4. Entrer le nom d'utilisateur GitHub

## 🌟 Recommandations Supplémentaires

### 1. Protéger la branche main

Settings → Branches → Add rule
- ✅ Require pull request reviews before merging
- ✅ Dismiss stale pull request approvals

### 2. Ajouter un .gitattributes

Dans le root du projet, créer `.gitattributes` :

```
* text=auto
*.py text eol=lf
*.js text eol=lf
*.html text eol=lf
*.json text eol=lf
*.pkl binary
```

### 3. GitHub Actions CI/CD (Optional)

Créer `.github/workflows/test.yml`:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - run: pip install -r WeatherMonitor/requirements.txt
      - run: cd WeatherMonitor && python -m pytest
```

## 📞 Aide Interactive

Si vous avez des erreurs :

```bash
# Voir l'historique
git log --oneline -5

# Voir les changements non stagiés
git diff

# Voir les changements stagiés
git diff --cached

# Annuler les changements (ATTENTION: perte de données)
git reset --hard HEAD
```

---

**Vous êtes prêt !** 🎉 Votre projet est maintenant sur GitHub !

Pour des mises à jour futures, utilisez simplement :
```bash
git add .
git commit -m "Description"
git push origin main
```
