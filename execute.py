import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('DBESante.db')
cur = conn.cursor()

# Exécuter la requête SQL pour compter les ressources actives
cur.execute("""
    SELECT * FROM dossier_medical WHERE id_dossier = 2;  
""")

# Récupérer et afficher le résultat
result = cur.fetchall()
print(result)  # Affiche le résultat de la requête

# Validation et fermeture de la connexion
conn.commit()
conn.close()