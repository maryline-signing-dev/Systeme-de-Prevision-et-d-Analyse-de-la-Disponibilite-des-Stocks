"""
Service d'alertes — analyse tous les produits actifs
et retourne ceux dont le stock est à risque.
"""
from datetime import date, timedelta
from .stock_engine import calculate_stock_at_date, find_first_stockout
from ..database import get_connection
from ..constants import DEFAULT_HORIZON_JOURS


def get_all_produits_actifs() -> list:
    """Récupère tous les ids des produits actifs."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id_produit, nom_produit, seuil_alerte FROM produit WHERE actif = TRUE"
        )
        rows = cursor.fetchall()
        for row in rows:
            row['seuil_alerte'] = float(row['seuil_alerte'])
        return rows
    finally:
        cursor.close()
        conn.close()


def get_alertes_dashboard(horizon_days: int = DEFAULT_HORIZON_JOURS) -> dict:
    """
    Analyse tous les produits et retourne :
      - produits en rupture actuelle
      - produits avec rupture future dans l'horizon
      - produits sous le seuil d'alerte
    """
    produits        = get_all_produits_actifs()
    today           = date.today()

    ruptures_actuelles = []
    ruptures_futures   = []
    sous_seuil         = []

    for p in produits:
        pid = p['id_produit']

        # Stock actuel
        try:
            stock_actuel = calculate_stock_at_date(pid, today, include_planned=False)
            stock_val    = stock_actuel['stock']

            # Rupture actuelle (stock actuel insuffisant)
            if stock_actuel['rupture_detectee']:
                ruptures_actuelles.append({
                    'id_produit' : pid,
                    'nom_produit': p['nom_produit'],
                    'stock'      : stock_val,
                    'date_rupture': stock_actuel['date_premiere_rupture']
                })

            # Sous le seuil d'alerte
            elif 0 <= stock_val <= p['seuil_alerte']:
                sous_seuil.append({
                    'id_produit' : pid,
                    'nom_produit': p['nom_produit'],
                    'stock'      : stock_val,
                    'seuil_alerte': p['seuil_alerte']
                })

            # Rupture future
            rupture_future = find_first_stockout(pid, horizon_days)
            if rupture_future['rupture_detectee']:
                ruptures_futures.append({
                    'id_produit'   : pid,
                    'nom_produit'  : p['nom_produit'],
                    'stock_actuel' : stock_val,
                    'date_rupture' : rupture_future['date_premiere_rupture'],
                    'horizon_jours': horizon_days,
                    'flux_declencheur': rupture_future['flux_declencheur']
                })

        except Exception:
            continue

    return {
        'ruptures_actuelles': ruptures_actuelles,
        'ruptures_futures'  : ruptures_futures,
        'sous_seuil'        : sous_seuil,
        'nb_ruptures_actuelles': len(ruptures_actuelles),
        'nb_ruptures_futures'  : len(ruptures_futures),
        'nb_sous_seuil'        : len(sous_seuil),
        'horizon_jours'        : horizon_days
    }