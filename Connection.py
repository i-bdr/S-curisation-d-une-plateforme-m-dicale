import sqlite3
from sqlite3 import Error

def connect(db_file='DBESante.db'):
    """Créer une connexion à la base de données SQLite."""
    try:
        conn = sqlite3.connect(db_file)  # Utiliser le fichier de base de données passé en argument
        print("Connexion réussie à la base de données")
        return conn
    except Error as e:
        print(f"Erreur lors de la connexion à la base de données : {e}")
        return None


def main():
    database = "DBESante.db"

    # Connexion à la base de données
    conn = connect(database)

    if conn is not None:
        conn.close()  # Fermer la connexion à la base de données
        print("Connexion à la base de données fermée")
    else:
        print("Échec de la connexion à la base de données")

if __name__ == '__main__':
    main()
