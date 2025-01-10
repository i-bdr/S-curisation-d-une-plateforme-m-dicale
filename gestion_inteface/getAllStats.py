from helpers.db_connection import connect
from user_session import UserSession

def get_all_stats():
    conn = connect()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) AS nombre_de_demandes
        FROM demande;

    """)
    nombre_demandes = cursor.fetchall()

    cursor.execute("""
                   SELECT COUNT(*) AS nombre_de_ressources_actives
                    FROM dossier_medical;
    """)
    nombre_ressources_actives = cursor.fetchall()

    conn.close()

    # Retourner les résultats sous forme de dictionnaire
    stats = {
        "nombre_demandes": nombre_demandes,
        "nombre_ressources_actives": nombre_ressources_actives
    }
    return stats
