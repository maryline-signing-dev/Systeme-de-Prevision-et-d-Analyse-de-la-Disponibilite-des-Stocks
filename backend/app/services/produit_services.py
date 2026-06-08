from ..database import get_connection

def get_all_produits():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id_produit, nom_produit, categorie, marque,
                   stock_initial, date_initialisation,
                   unite, seuil_alerte, actif
            FROM produit
            WHERE actif = TRUE
            ORDER BY nom_produit
        """)
        rows = cursor.fetchall()
        # Convertir les types non sérialisables
        for row in rows:
            row['stock_initial']       = float(row['stock_initial'])
            row['seuil_alerte']        = float(row['seuil_alerte'])
            row['date_initialisation'] = str(row['date_initialisation'])
        return rows
    finally:
        cursor.close()
        conn.close()


def get_produit_by_id(id_produit: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id_produit, nom_produit, categorie, marque,
                   stock_initial, date_initialisation,
                   unite, seuil_alerte, actif
            FROM produit
            WHERE id_produit = %s AND actif = TRUE
        """, (id_produit,))
        row = cursor.fetchone()
        if row:
            row['stock_initial']       = float(row['stock_initial'])
            row['seuil_alerte']        = float(row['seuil_alerte'])
            row['date_initialisation'] = str(row['date_initialisation'])
        return row
    finally:
        cursor.close()
        conn.close()


def create_produit(data: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO produit
                (nom_produit, categorie, marque,
                 stock_initial, date_initialisation,
                 unite, seuil_alerte)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data['nom_produit'],
            data.get('categorie'),
            data.get('marque'),
            float(data.get('stock_initial', 0)),
            data['date_initialisation'],
            data.get('unite', 'unite'),
            float(data.get('seuil_alerte', 0))
        ))
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def update_produit(id_produit: int, data: dict) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE produit
            SET nom_produit         = %s,
                categorie           = %s,
                marque              = %s,
                stock_initial       = %s,
                date_initialisation = %s,
                unite               = %s,
                seuil_alerte        = %s
            WHERE id_produit = %s AND actif = TRUE
        """, (
            data['nom_produit'],
            data.get('categorie'),
            data.get('marque'),
            float(data.get('stock_initial', 0)),
            data['date_initialisation'],
            data.get('unite', 'unite'),
            float(data.get('seuil_alerte', 0)),
            id_produit
        ))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()


def delete_produit(id_produit: int) -> bool:
    """Soft delete — marque actif=FALSE sans supprimer."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Vérifier si des flux existent pour ce produit
        cursor.execute(
            "SELECT COUNT(*) FROM flux WHERE id_produit = %s",
            (id_produit,)
        )
        count = cursor.fetchone()[0]
        if count > 0:
            raise ValueError(
                f"Impossible de supprimer : {count} flux associés à ce produit"
            )

        cursor.execute(
            "UPDATE produit SET actif = FALSE WHERE id_produit = %s",
            (id_produit,)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()