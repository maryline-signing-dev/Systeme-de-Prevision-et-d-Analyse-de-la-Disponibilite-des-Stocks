import bcrypt
from ..database import get_connection

def verify_admin(email: str, password: str):
    """
    Vérifie les identifiants de l'administrateur.
    Retourne le dict admin si valide, None sinon.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT id_admin, nom, email, mot_de_passe_hash
               FROM admin
               WHERE email = %s""",
            (email,)
        )
        admin = cursor.fetchone()

        if not admin:
            return None  # Email inexistant

        # Vérification du mot de passe
        mot_de_passe_valide = bcrypt.checkpw(
            password.encode('utf-8'),
            admin['mot_de_passe_hash'].encode('utf-8')
        )

        if mot_de_passe_valide:
            return admin
        return None  # Mauvais mot de passe

    finally:
        cursor.close()
        conn.close()


def update_derniere_connexion(id_admin: int):
    """Met à jour la date de dernière connexion."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE admin SET derniere_connexion = NOW() WHERE id_admin = %s",
            (id_admin,)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()