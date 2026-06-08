"""
Routes API — Prévision et calcul de disponibilité

Endpoints :
  GET /api/prevision/<id>/date/<date>   stock à une date
  GET /api/prevision/<id>/rupture       première date de rupture
  GET /api/prevision/<id>/courbe        courbe temporelle
  GET /api/prevision/alertes            alertes tableau de bord
"""
from datetime import date, datetime, timedelta
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ..services.stock_engine import (
    calculate_stock_at_date,
    find_first_stockout,
    generate_stock_curve
)
from ..services.alerte_service import get_alertes_dashboard
from ..utils.responses import success, error
from ..constants import DEFAULT_HORIZON_JOURS, DEFAULT_COURBE_JOURS

prevision_bp = Blueprint('prevision', __name__)


def _parse_date(date_str: str) -> date:
    """Parse une date ISO YYYY-MM-DD. Lève ValueError si invalide."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        raise ValueError(f"Format de date invalide : '{date_str}'. Attendu : YYYY-MM-DD")


# ============================================================
# ENDPOINT 1 — Stock à une date donnée
# ============================================================

@prevision_bp.route('/<int:id_produit>/date/<string:date_cible>', methods=['GET'])
@jwt_required()
def stock_a_date(id_produit, date_cible):
    """
    Calcule le stock d'un produit à une date donnée.

    URL params:
      id_produit : identifiant du produit
      date_cible : date au format YYYY-MM-DD

    Query params:
      include_planned : true/false (défaut false)
                        si true → inclut les flux PLANIFIE
                        (utile pour projection future)

    Exemples :
      GET /api/prevision/1/date/2026-04-01
      GET /api/prevision/1/date/2026-09-01?include_planned=true
    """
    # Paramètre optionnel
    include_planned = request.args.get('include_planned', 'false').lower() == 'true'

    try:
        target = _parse_date(date_cible)
    except ValueError as e:
        return error(str(e), 400)

    try:
        result = calculate_stock_at_date(id_produit, target, include_planned)
        return success(result)
    except ValueError as e:
        return error(str(e), 404)
    except Exception as e:
        return error(f"Erreur de calcul : {str(e)}", 500)


# ============================================================
# ENDPOINT 2 — Première date de rupture
# ============================================================

@prevision_bp.route('/<int:id_produit>/rupture', methods=['GET'])
@jwt_required()
def premiere_rupture(id_produit):
    """
    Détecte la première rupture sur un horizon donné.

    Query params:
      horizon : nombre de jours à analyser (défaut 90)

    Exemple :
      GET /api/prevision/1/rupture
      GET /api/prevision/1/rupture?horizon=60
    """
    try:
        horizon = int(request.args.get('horizon', DEFAULT_HORIZON_JOURS))
        if horizon <= 0 or horizon > 365:
            return error("horizon doit être entre 1 et 365 jours", 400)
    except ValueError:
        return error("horizon doit être un entier", 400)

    try:
        result = find_first_stockout(id_produit, horizon)
        return success(result)
    except ValueError as e:
        return error(str(e), 404)
    except Exception as e:
        return error(f"Erreur de calcul : {str(e)}", 500)


# ============================================================
# ENDPOINT 3 — Courbe temporelle
# ============================================================

@prevision_bp.route('/<int:id_produit>/courbe', methods=['GET'])
@jwt_required()
def courbe_temporelle(id_produit):
    """
    Génère la courbe d'évolution du stock pour graphique.

    Query params:
      from : date de début YYYY-MM-DD (défaut aujourd'hui)
      to   : date de fin   YYYY-MM-DD (défaut aujourd'hui + 60j)

    Exemple :
      GET /api/prevision/1/courbe
      GET /api/prevision/1/courbe?from=2026-01-01&to=2026-12-31
    """
    today = date.today()

    # Parsing des dates avec valeurs par défaut
    try:
        date_from = _parse_date(
            request.args.get('from', str(today))
        )
        date_to = _parse_date(
            request.args.get('to', str(today + timedelta(days=DEFAULT_COURBE_JOURS)))
        )
    except ValueError as e:
        return error(str(e), 400)

    # Validation de la cohérence
    if date_from > date_to:
        return error("La date 'from' doit être antérieure à 'to'", 400)

    # Limiter à 730 jours pour éviter les timeouts
    if (date_to - date_from).days > 730:
        return error("Intervalle maximum : 730 jours", 400)

    try:
        result = generate_stock_curve(id_produit, date_from, date_to)
        return success(result)
    except ValueError as e:
        return error(str(e), 404)
    except Exception as e:
        return error(f"Erreur de calcul : {str(e)}", 500)


# ============================================================
# ENDPOINT 4 — Alertes tableau de bord
# ============================================================

@prevision_bp.route('/alertes', methods=['GET'])
@jwt_required()
def alertes():
    """
    Retourne toutes les alertes pour le tableau de bord.

    Query params:
      horizon : nombre de jours pour la détection (défaut 90)

    Exemple :
      GET /api/prevision/alertes
      GET /api/prevision/alertes?horizon=30
    """
    try:
        horizon = int(request.args.get('horizon', DEFAULT_HORIZON_JOURS))
    except ValueError:
        horizon = DEFAULT_HORIZON_JOURS

    try:
        result = get_alertes_dashboard(horizon)
        return success(result)
    except Exception as e:
        return error(f"Erreur alertes : {str(e)}", 500)