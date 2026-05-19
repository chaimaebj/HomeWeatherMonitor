from app import app
from firebase_db import create_user
from werkzeug.security import generate_password_hash

def create_admin_user():
    with app.app_context():
        # Créer un nouvel utilisateur admin
        admin = create_user(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            phone_number='+1234567890'
        )
        
        if admin:
            print("Utilisateur admin créé avec succès dans Firebase!")
            print("Nom d'utilisateur: admin")
            print("Mot de passe: admin123")
        else:
            print("Erreur lors de la création de l'utilisateur admin!")

if __name__ == "__main__":
    create_admin_user() 