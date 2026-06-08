from ..database import get_connection
from ..constants import STATUT_REALISE

def get_flux_by_produit(id_produit: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id_flux, id_produit, type_flux, nature_flux,
                   statut_flux, quantite, date_flux, heure_flux,
                   ordre_execution, reference_externe, commentaire,
                   date_saisie
            FROM flux
            WHERE id_produit = %s
            ORDER BY date_flux DESC, ordre_execution ASC
        """, (id_produit,))
        rows = cursor.fetchall()
        for row in rows:
            row['quantite']    = float(row['quantite'])
            row['date_flux']   = str(row['date_flux'])
            row['date_saisie'] = str(row['date_saisie'])
            if row['heure_flux']:
                row['heure_flux'] = str(row['heure_flux'])
        return rows
    finally:
        cursor.close()
        conn.close()


def get_flux_by_id(id_flux: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id_flux, id_produit, type_flux, nature_flux,
                   statut_flux, quantite, date_flux, heure_flux,
                   ordre_execution, reference_externe, commentaire,
                   date_saisie
            FROM flux WHERE id_flux = %s
        """, (id_flux,))
        row = cursor.fetchone()
        if row:
            row['quantite']    = float(row['quantite'])
            row['date_flux']   = str(row['date_flux'])
            row['date_saisie'] = str(row['date_saisie'])
            if row['heure_flux']:
                row['heure_flux'] = str(row['heure_flux'])
        return row
    finally:
        cursor.close()
        conn.close()


def create_flux(data: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO flux
                (id_produit, type_flux, nature_flux, statut_flux,
                 quantite, date_flux, heure_flux,
                 ordre_execution, reference_externe, commentaire)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            int(data['id_produit']),
            data['type_flux'],
            data.get('nature_flux'),
            data.get('statut_flux', 'PLANIFIE'),
            float(data['quantite']),
            data['date_flux'],
            data.get('heure_flux'),
            int(data.get('ordre_execution', 0)),
            data.get('reference_externe'),
            data.get('commentaire')
        ))
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def update_statut_flux(id_flux: int, nouveau_statut: str) -> bool:
    """
    Met à jour uniquement le statut d'un flux.
    Un flux REALISE ne peut pas être modifié (RG-06).
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Vérifier le statut actuel
        cursor.execute(
            "SELECT statut_flux FROM flux WHERE id_flux = %s",
            (id_flux,)
        )
        flux = cursor.fetchone()
        if not flux:
            return False

        if flux['statut_flux'] == STATUT_REALISE:
            raise ValueError(
                "Un flux REALISE est immuable. "
                "Créez un flux correctif si nécessaire."
            )

        cursor.execute(
            "UPDATE flux SET statut_flux = %s WHERE id_flux = %s",
            (nouveau_statut, id_flux)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()


def delete_flux(id_flux: int) -> bool:
    """
    Supprime un flux uniquement s'il est PLANIFIE.
    Un flux REALISE ou EN_COURS ne peut pas être supprimé.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT statut_flux FROM flux WHERE id_flux = %s",
            (id_flux,)
        )
        flux = cursor.fetchone()
        if not flux:
            return False

        if flux['statut_flux'] != 'PLANIFIE':
            raise ValueError(
                f"Seuls les flux PLANIFIE peuvent être supprimés. "
                f"Statut actuel : {flux['statut_flux']}"
            )

        cursor.execute("DELETE FROM flux WHERE id_flux = %s", (id_flux,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()