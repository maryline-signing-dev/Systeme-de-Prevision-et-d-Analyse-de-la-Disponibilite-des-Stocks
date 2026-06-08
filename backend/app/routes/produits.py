from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ..services.produit_services import (
    get_all_produits,
    get_produit_by_id,
    create_produit,
    update_produit,
    delete_produit
)
from ..utils.responses import success, error

produits_bp = Blueprint('produits', __name__)


@produits_bp.route('/', methods=['GET'])
@jwt_required()
def get_all():
    produits = get_all_produits()
    return success(produits)


@produits_bp.route('/<int:id_produit>', methods=['GET'])
@jwt_required()
def get_one(id_produit):
    produit = get_produit_by_id(id_produit)
    if not produit:
        return error("Produit introuvable", 404)
    return success(produit)


@produits_bp.route('/', methods=['POST'])
@jwt_required()
def create():
    data = request.get_json()
    if not data:
        return error("Corps de requête manquant", 400)

    # Validation des champs requis
    if not data.get('nom_produit'):
        return error("nom_produit est requis", 400)
    if not data.get('date_initialisation'):
        return error("date_initialisation est requise", 400)

    try:
        new_id = create_produit(data)
        return success({"id_produit": new_id}, "Produit créé", 201)
    except Exception as e:
        return error(str(e), 500)


@produits_bp.route('/<int:id_produit>', methods=['PUT'])
@jwt_required()
def update(id_produit):
    data = request.get_json()
    if not data:
        return error("Corps de requête manquant", 400)
    if not data.get('nom_produit'):
        return error("nom_produit est requis", 400)

    try:
        modifie = update_produit(id_produit, data)
        if not modifie:
            return error("Produit introuvable", 404)
        return success(message="Produit mis à jour")
    except Exception as e:
        return error(str(e), 500)


@produits_bp.route('/<int:id_produit>', methods=['DELETE'])
@jwt_required()
def delete(id_produit):
    try:
        supprime = delete_produit(id_produit)
        if not supprime:
            return error("Produit introuvable", 404)
        return success(message="Produit supprimé")
    except ValueError as e:
        return error(str(e), 409)  # 409 Conflict
    except Exception as e:
        return error(str(e), 500)