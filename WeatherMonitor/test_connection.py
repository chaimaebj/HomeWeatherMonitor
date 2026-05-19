from datetime import datetime
from firebase_config import initialize_firebase, get_realtime_db, get_firestore_db

def test_connection():
    print("\n=== Test de connexion aux bases de données Firebase ===\n")
    
    # Initialiser Firebase
    print("1. Initialisation de Firebase...")
    if not initialize_firebase():
        print("❌ Échec de l'initialisation de Firebase")
        return False
    print("✅ Firebase initialisé avec succès\n")
    
    # Tester la connexion à la base de données en temps réel
    print("2. Test de la connexion à Firebase Realtime Database...")
    realtime_db = get_realtime_db()
    if realtime_db:
        try:
            # Écrire une donnée de test
            test_data = {
                'test_value': 42,
                'timestamp': datetime.now().isoformat(),
                'message': 'Test de connexion Realtime Database'
            }
            realtime_db.child('test_connection').set(test_data)
            print("✅ Connexion à la base de données en temps réel réussie")
            print("   → Données écrites dans le nœud 'test_connection'")
        except Exception as e:
            print(f"❌ Erreur de connexion à la base de données en temps réel: {str(e)}")
            return False
    else:
        print("❌ Impossible d'obtenir une référence à la base de données en temps réel")
        return False
    print()
    
    # Tester la connexion à Firestore
    print("3. Test de la connexion à Firestore...")
    firestore_db = get_firestore_db()
    if firestore_db:
        try:
            # Écrire une donnée de test
            test_data = {
                'test_value': 42,
                'timestamp': datetime.now(),
                'message': 'Test de connexion Firestore'
            }
            firestore_db.collection('test_connection').document('test').set(test_data)
            print("✅ Connexion à Firestore réussie")
            print("   → Données écrites dans la collection 'test_connection'")
        except Exception as e:
            print(f"❌ Erreur de connexion à Firestore: {str(e)}")
            return False
    else:
        print("❌ Impossible d'obtenir une référence à Firestore")
        return False
    print()
    
    print("=== Résumé des tests ===")
    print("✅ Tous les tests de connexion sont réussis!")
    print("\nVous pouvez maintenant vérifier dans la console Firebase que les données de test ont été écrites :")
    print("1. Pour Realtime Database : cherchez le nœud 'test_connection'")
    print("2. Pour Firestore : cherchez la collection 'test_connection'")
    return True

if __name__ == "__main__":
    test_connection() 