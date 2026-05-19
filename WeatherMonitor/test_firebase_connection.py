from firebase_config import initialize_firebase, get_database

def test_connection():
    # Initialiser Firebase
    if initialize_firebase():
        # Obtenir une référence à la base de données
        db_ref = get_database()
        
        # Tester l'écriture
        test_data = {
            'test': {
                'message': 'Connexion réussie!',
                'timestamp': 'test'
            }
        }
        
        try:
            # Écrire des données de test
            db_ref.child('test_connection').set(test_data)
            print("✅ Écriture réussie!")
            
            # Lire les données
            data = db_ref.child('test_connection').get()
            print("✅ Lecture réussie!")
            print("Données lues:", data)
            
            # Nettoyer les données de test
            db_ref.child('test_connection').delete()
            print("✅ Suppression réussie!")
            
            return True
        except Exception as e:
            print(f"❌ Erreur lors du test: {str(e)}")
            return False
    return False

if __name__ == "__main__":
    test_connection() 