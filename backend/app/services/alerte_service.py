"""
Service d'alertes — analyse tous les produits actifs
et retourne ceux dont le stock est à risque.

CORRECTION : les clés du dictionnaire retourné ont été
renommées pour correspondre exactement à ce que le frontend
attend :
  ruptures_futures  → ruptures_prevues
  sous_seuil        → alertes_seuil
  nb_ruptures_futures → nb_ruptures_prevues
  nb_sous_seuil       → nb_alertes_seuil

La structure inclut également 'resume' et 'nb_produits_ok'
attendus par le dashboard.
"""
from datetime import date, timedelta
from .stock_engine import calculate_stock_at_date, find_first_stockout
from ..database import get_connection
from ..constants import DEFAULT_HORIZON_JOURS


def get_all_produits_actifs() -> list:
    """Récupère tous les produits actifs avec leurs infos de base."""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id_produit, nom_produit, seuil_alerte, unite
            FROM produit
            WHERE actif = TRUE
            ORDER BY nom_produit
        """)
        rows = cursor.fetchall()
        for row in rows:
            row['seuil_alerte'] = float(row['seuil_alerte'])
        return rows
    finally:
        cursor.close()
        conn.close()


def get_alertes_dashboard(horizon_days: int = DEFAULT_HORIZON_JOURS) -> dict:
    """
    Analyse tous les produits et retourne un dictionnaire
    avec la structure exacte attendue par le frontend.

    Clés retournées :
      ruptures_actuelles  : produits avec rupture passée non résolue
      ruptures_prevues    : produits avec rupture future dans l'horizon
      alertes_seuil       : produits sous le seuil sans rupture
      resume              : compteurs pour les cartes du dashboard
    """
    produits = get_all_produits_actifs()
    today    = date.today()

    ruptures_actuelles = []
    ruptures_prevues   = []
    alertes_seuil      = []

    for p in produits:
        pid   = p['id_produit']
        nom   = p['nom_produit']
        unite = p.get('unite', 'unité')
        seuil = p['seuil_alerte']

        try:
            # ── Stock actuel (flux REALISE uniquement) ──────
            stock_actuel = calculate_stock_at_date(
                pid, today, include_planned=False
            )
            stock_val = stock_actuel['stock']

            # Rupture actuelle
            if stock_actuel['rupture_detectee']:
                ruptures_actuelles.append({
                    'id_produit'     : pid,
                    'nom_produit'    : nom,
                    'stock_actuel'   : stock_val,
                    'unite'          : unite,
                    'nb_ruptures'    : len(stock_actuel['ruptures']),
                    'derniere_rupture': stock_actuel['date_premiere_rupture']
                })

            # Alerte seuil (stock positif mais sous le seuil)
            elif 0 < stock_val <= seuil:
                alertes_seuil.append({
                    'id_produit'  : pid,
                    'nom_produit' : nom,
                    'stock_actuel': stock_val,
                    'seuil_alerte': seuil,
                    'unite'       : unite
                })

            # ── Rupture future ───────────────────────────────
            rupture_future = find_first_stockout(pid, horizon_days)
            if rupture_future['rupture_detectee']:
                date_rupt = rupture_future['date_premiere_rupture']
                try:
                    from datetime import date as date_type
                    jours_restants = (
                        date_type.fromisoformat(date_rupt) - today
                    ).days
                except Exception:
                    jours_restants = 0

                fd = rupture_future.get('flux_declencheur') or {}
                ruptures_prevues.append({
                    'id_produit'        : pid,
                    'nom_produit'       : nom,
                    'stock_actuel'      : stock_val,
                    'unite'             : unite,
                    'date_rupture'      : date_rupt,
                    'jours_restants'    : max(0, jours_restants),
                    'quantite_manquante': fd.get('quantite_manquante', 0)
                })

        except Exception:
            continue

    # Trier ruptures prévues par date croissante
    ruptures_prevues.sort(key=lambda x: x.get('date_rupture', ''))

    nb_total = len(produits)
    nb_ok    = nb_total - len(ruptures_actuelles) - len(ruptures_prevues) - len(alertes_seuil)

    return {
        # Listes détaillées
        'ruptures_actuelles': ruptures_actuelles,
        'ruptures_prevues'  : ruptures_prevues,
        'alertes_seuil'     : alertes_seuil,

        # Résumé pour les cartes du dashboard
        'resume': {
            'nb_ruptures_actuelles': len(ruptures_actuelles),
            'nb_ruptures_prevues'  : len(ruptures_prevues),
            'nb_alertes_seuil'     : len(alertes_seuil),
            'nb_produits_ok'       : max(0, nb_ok),
            'horizon_jours'        : horizon_days
        }
    }