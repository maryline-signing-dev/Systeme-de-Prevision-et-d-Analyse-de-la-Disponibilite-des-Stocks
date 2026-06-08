from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ..services.flux_services import (
    get_flux_by_produit,
    get_flux_by_id,
    create_flux,
    update_statut_flux,
    delete_flux
)
from ..utils.responses import success, error
from ..constants import STATUTS_FLUX, TYPES_FLUX

flux_bp = Blueprint('flux', __name__)


@flux_bp.route('/produit/<int:id_produit>', methods=['GET'])
@jwt_required()
def get_by_produit(id_produit):
    flux = get_flux_by_produit(id_produit)
    return success(flux)


@flux_bp.route('/<int:id_flux>', methods=['GET'])
@jwt_required()
def get_one(id_flux):
    flux = get_flux_by_id(id_flux)
    if not flux:
        return error("Flux introuvable", 404)
    return success(flux)


@flux_bp.route('/', methods=['POST'])
@jwt_required()
def create():
    data = request.get_json()
    if not data:
        return error("Corps de requête manquant", 400)

    # Validation des champs requis
    if not data.get('id_produit'):
        return error("id_produit est requis", 400)
    if not data.get('type_flux') or data['type_flux'] not in TYPES_FLUX:
        return error(f"type_flux invalide. Valeurs : {TYPES_FLUX}", 400)
    if not data.get('quantite') or float(data['quantite']) <= 0:
        return error("quantite doit être > 0", 400)
    if not data.get('date_flux'):
        return error("date_flux est requise", 400)
    if data.get('statut_flux') and data['statut_flux'] not in STATUTS_FLUX:
        return error(f"statut_flux invalide. Valeurs : {STATUTS_FLUX}", 400)

    try:
        new_id = create_flux(data)
        return success({"id_flux": new_id}, "Flux créé", 201)
    except Exception as e:
        return error(str(e), 500)


@flux_bp.route('/<int:id_flux>/statut', methods=['PATCH'])
@jwt_required()
def update_statut(id_flux):
    data = request.get_json()
    if not data or not data.get('statut_flux'):
        return error("statut_flux est requis", 400)
    if data['statut_flux'] not in STATUTS_FLUX:
        return error(f"statut_flux invalide. Valeurs : {STATUTS_FLUX}", 400)

    try:
        modifie = update_statut_flux(id_flux, data['statut_flux'])
        if not modifie:
            return error("Flux introuvable", 404)
        return success(message="Statut mis à jour")
    except ValueError as e:
        return error(str(e), 409)
    except Exception as e:
        return error(str(e), 500)


@flux_bp.route('/<int:id_flux>', methods=['DELETE'])
@jwt_required()
def delete(id_flux):
    try:
        supprime = delete_flux(id_flux)
        if not supprime:
            return error("Flux introuvable", 404)
        return success(message="Flux supprimé")
    except ValueError as e:
        return error(str(e), 409)
    except Exception as e:
        return error(str(e), 500)