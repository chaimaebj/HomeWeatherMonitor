from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_admin_user():
    with app.app_context():
        # Vérifier si l'utilisateur admin existe déjà
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("L'utilisateur admin existe déjà!")
            return
        
        # Créer un nouvel utilisateur admin
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            phone_number='+1234567890'
        )
        
        # Ajouter l'utilisateur à la base de données
        db.session.add(admin)
        db.session.commit()
        
        print("Utilisateur admin créé avec succès!")
        print("Nom d'utilisateur: admin")
        print("Mot de passe: admin123")

if __name__ == "__main__":
    create_admin_user() 