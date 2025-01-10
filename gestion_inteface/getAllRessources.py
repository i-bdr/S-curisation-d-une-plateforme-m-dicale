from helpers.db_connection import connect

def get_all_ressources(id_user):
    conn = connect()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            dm.id_dossier AS Ressource,
            u.nom || ' ' || u.prenom AS Patient,
            ud.nom_privilege AS TypePolitique
        FROM 
            user_dossier ud
        JOIN 
            dossier_medical dm ON ud.id_dossier = dm.id_dossier
        JOIN 
            user u ON dm.id_patient = u.iduser
        WHERE 
            ud.id_user = ?;
    """, (id_user,))
    ressources = cursor.fetchall()
    result = cursor.fetchall()
    conn.close()

    return ressources
