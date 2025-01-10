from helpers.db_connection import connect

def get_ressource_detail(id_dossier_medical):
    conn = connect()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM dossier_medical WHERE id_dossier = ?;
    """, (id_dossier_medical,))
    
    ressources = cursor.fetchall()
    result = cursor.fetchall()
    print(result)  # Affiche le résultat de la requête
    conn.close()

    return ressources
