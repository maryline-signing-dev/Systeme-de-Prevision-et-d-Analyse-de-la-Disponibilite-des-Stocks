from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from ..services.auth_services import verify_admin, update_derniere_connexion
from ..utils.responses import success, error

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Vérification des champs requis
    if not data or not data.get('email') or not data.get('password'):
        return error("Email et mot de passe requis", 400)

    # Vérification des identifiants
    admin = verify_admin(data['email'], data['password'])
    if not admin:
        return error("Identifiants invalides", 401)

    # Mise à jour dernière connexion
    update_derniere_connexion(admin['id_admin'])

    # Génération du token JWT
    token = create_access_token(identity=str(admin['id_admin']))

    return success({
        "access_token": token,
        "admin": {
            "id":    admin['id_admin'],
            "nom":   admin['nom'],
            "email": admin['email']
        }
    }, "Connexion reussie")


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    """Vérifie que le token est valide et retourne l'identité."""
    admin_id = get_jwt_identity()
    return success({"id": admin_id}, "Token valide")