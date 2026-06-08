"""
Moteur de Projection Chronologique Déterministe

Définition de la RUPTURE :
  Une rupture n'est PAS "stock < 0".
  Une rupture EST : un flux SORTANT est déclenché alors que
  le stock disponible À CE MOMENT est insuffisant pour le satisfaire.

Règles métier appliquées :
  RG-01 : Rupture = flux sortant non satisfiable au moment T
  RG-02 : Tri chronologique (date ASC, ordre_execution ASC)
  RG-03 : Priorité ENTRANT avant SORTANT à date égale
  RG-04 : REALISE + EN_COURS pour stock courant
  RG-05 : + PLANIFIE pour projections futures
  RG-06 : Flux REALISE immuable

Cas couverts :
  - Flux sortant seul avec stock insuffisant → rupture
  - Flux entrant puis sortant même date → entrant compense → pas de rupture
  - Flux sortant puis entrant même date → RG-03 inverse l'ordre → entrant traité d'abord
  - Plusieurs sortants même date → FIFO ordre_execution → rupture sur le premier non satisfiable
  - Stock initial = 0, premier flux sortant → rupture immédiate
"""

from datetime import date, timedelta
from typing import Optional
from ..database import get_connection
from ..constants import (
    TYPE_ENTRANT,
    TYPE_SORTANT,
    STATUT_PLANIFIE,
    STATUT_EN_COURS,
    STATUT_REALISE
)


# ============================================================
# FONCTIONS INTERNES
# ============================================================

def _get_produit(product_id: int) -> Optional[dict]:
    """Récupère le produit avec son stock initial."""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id_produit, nom_produit,
                   stock_initial, date_initialisation,
                   seuil_alerte, unite
            FROM produit
            WHERE id_produit = %s AND actif = TRUE
        """, (product_id,))
        row = cursor.fetchone()
        if row:
            row['stock_initial'] = float(row['stock_initial'])
            row['seuil_alerte']  = float(row['seuil_alerte'])
        return row
    finally:
        cursor.close()
        conn.close()


def _get_flux_range(product_id: int,
                    date_from: date,
                    date_to: date,
                    statuts: list) -> list:
    """
    Récupère les flux triés selon RG-02 et RG-03.

    Ordre de tri :
      1. date_flux ASC                        (RG-02)
      2. ENTRANT avant SORTANT à date égale   (RG-03)
      3. ordre_execution ASC                  (RG-02)

    MODIFICATION : utilisation systématique de date_flux_str
    comme clé de comparaison pour éviter les incohérences
    entre objets date Python et chaînes ISO.
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        placeholders = ','.join(['%s'] * len(statuts))
        query = f"""
            SELECT id_flux, type_flux, nature_flux, statut_flux,
                   quantite, date_flux, ordre_execution
            FROM flux
            WHERE id_produit    = %s
              AND date_flux     >= %s
              AND date_flux     <= %s
              AND statut_flux   IN ({placeholders})
            ORDER BY
                date_flux        ASC,
                CASE type_flux
                    WHEN 'ENTRANT' THEN 0
                    ELSE 1
                END              ASC,
                ordre_execution  ASC
        """
        params = [product_id, date_from, date_to] + statuts
        cursor.execute(query, params)
        rows = cursor.fetchall()

        for row in rows:
            row['quantite'] = float(row['quantite'])
            # CORRECTION : normalisation systématique en str ISO
            # pour que toutes les comparaisons et groupements
            # fonctionnent de manière identique (date_flux_str
            # est la clé utilisée partout dans les algorithmes)
            if hasattr(row['date_flux'], 'isoformat'):
                row['date_flux_str'] = row['date_flux'].isoformat()
            else:
                row['date_flux_str'] = str(row['date_flux'])

        return rows
    finally:
        cursor.close()
        conn.close()


def _appliquer_flux(flux: dict, stock_courant: float) -> dict:
    """
    Applique un flux au stock courant et détermine s'il y a rupture.

    Args:
        flux          : dict du flux à appliquer
        stock_courant : stock disponible avant ce flux

    Returns:
        {
          'stock_apres'        : float
          'rupture'            : bool
          'quantite_manquante' : float
          'satisfait'          : bool
        }
    """
    if flux['type_flux'] == TYPE_ENTRANT:
        return {
            'stock_apres'       : round(stock_courant + flux['quantite'], 2),
            'rupture'           : False,
            'quantite_manquante': 0.0,
            'satisfait'         : True
        }
    else:
        if stock_courant >= flux['quantite']:
            return {
                'stock_apres'       : round(stock_courant - flux['quantite'], 2),
                'rupture'           : False,
                'quantite_manquante': 0.0,
                'satisfait'         : True
            }
        else:
            quantite_manquante = round(flux['quantite'] - stock_courant, 2)
            return {
                'stock_apres'       : round(stock_courant - flux['quantite'], 2),
                'rupture'           : True,
                'quantite_manquante': quantite_manquante,
                'satisfait'         : False
            }


# ============================================================
# ALGORITHME 1 — Stock à une date (passée ou future)
# ============================================================

def calculate_stock_at_date(product_id: int,
                             target_date: date,
                             include_planned: bool = False) -> dict:
    """
    Calcule le stock d'un produit à une date donnée.

    CORRECTION : utilisation de flux['date_flux_str'] au lieu de
    str(flux['date_flux']) pour la cohérence avec generate_stock_curve.
    """
    produit = _get_produit(product_id)
    if not produit:
        raise ValueError(f"Produit {product_id} introuvable ou inactif")

    today     = date.today()
    is_future = target_date > today

    if is_future and include_planned:
        statuts = [STATUT_REALISE, STATUT_EN_COURS, STATUT_PLANIFIE]
    elif is_future:
        statuts = [STATUT_REALISE, STATUT_EN_COURS]
    else:
        statuts = [STATUT_REALISE]

    flux_list = _get_flux_range(
        product_id,
        produit['date_initialisation'],
        target_date,
        statuts
    )

    stock          = produit['stock_initial']
    flux_appliques = []
    ruptures       = []

    for flux in flux_list:
        stock_avant = stock
        resultat    = _appliquer_flux(flux, stock)
        stock       = resultat['stock_apres']

        # CORRECTION : utiliser date_flux_str (clé normalisée)
        entree = {
            'id_flux'           : flux['id_flux'],
            'date'              : flux['date_flux_str'],
            'type'              : flux['type_flux'],
            'nature'            : flux['nature_flux'],
            'statut'            : flux['statut_flux'],
            'quantite'          : flux['quantite'],
            'stock_avant'       : round(stock_avant, 2),
            'stock_apres'       : resultat['stock_apres'],
            'rupture'           : resultat['rupture'],
            'satisfait'         : resultat['satisfait'],
            'quantite_manquante': resultat['quantite_manquante']
        }
        flux_appliques.append(entree)

        if resultat['rupture']:
            ruptures.append({
                'id_flux'           : flux['id_flux'],
                'date'              : flux['date_flux_str'],
                'type_flux'         : flux['type_flux'],
                'nature'            : flux['nature_flux'],
                'nature_flux'       : flux['nature_flux'],
                'statut_flux'       : flux['statut_flux'],
                'quantite'          : flux['quantite'],
                'stock_disponible'  : round(stock_avant, 2),
                'quantite_demandee' : flux['quantite'],
                'quantite_manquante': resultat['quantite_manquante']
            })

    stock_final           = round(stock, 2)
    date_premiere_rupture = ruptures[0]['date'] if ruptures else None

    return {
        'stock'                : stock_final,
        'produit'              : {
            'id'          : produit['id_produit'],
            'nom'         : produit['nom_produit'],
            'seuil_alerte': produit['seuil_alerte'],
            'unite'       : produit['unite']
        },
        'ruptures'             : ruptures,
        'rupture_detectee'     : len(ruptures) > 0,
        'date_premiere_rupture': date_premiere_rupture,
        'alerte_seuil'         : (0 <= stock_final <= produit['seuil_alerte']),
        'flux_appliques'       : flux_appliques,
        'flux_count'           : len(flux_appliques)
    }


# ============================================================
# ALGORITHME 2 — Première date de rupture sur un horizon
# ============================================================

def find_first_stockout(product_id: int,
                        horizon_days: int = 90) -> dict:
    """
    Détecte la première rupture à partir d'aujourd'hui.

    CORRECTION : le flux_declencheur expose 'nature' (utilisé
    dans les tests) en plus de 'nature_flux'.
    """
    target_date = date.today() + timedelta(days=horizon_days)
    result      = calculate_stock_at_date(
        product_id,
        target_date,
        include_planned=True
    )

    premiere_rupture = result['ruptures'][0] if result['ruptures'] else None

    return {
        'rupture_detectee'     : result['rupture_detectee'],
        'date_premiere_rupture': result['date_premiere_rupture'],
        'flux_declencheur'     : premiere_rupture,
        'stock_au_terme'       : result['stock'],
        'horizon_jours'        : horizon_days,
        'produit'              : result['produit'],
        'nombre_ruptures'      : len(result['ruptures'])
    }


# ============================================================
# ALGORITHME 3 — Courbe temporelle pour graphique
# ============================================================

def generate_stock_curve(product_id: int,
                         date_from: date,
                         date_to: date) -> dict:
    """
    Génère la courbe d'évolution du stock jour par jour.

    CORRECTION : groupement des flux par date_flux_str
    (clé normalisée ISO) au lieu de str(flux['date_flux'])
    pour cohérence avec calculate_stock_at_date.
    """
    produit = _get_produit(product_id)
    if not produit:
        raise ValueError(f"Produit {product_id} introuvable")

    flux_list = _get_flux_range(
        product_id,
        produit['date_initialisation'],
        date_to,
        [STATUT_REALISE, STATUT_EN_COURS, STATUT_PLANIFIE]
    )

    # CORRECTION : utiliser date_flux_str comme clé
    flux_par_date = {}
    for flux in flux_list:
        d = flux['date_flux_str']          # ← était str(flux['date_flux'])
        flux_par_date.setdefault(d, []).append(flux)

    labels   = []
    values   = []
    ruptures = []
    stock    = produit['stock_initial']
    current  = date_from

    while current <= date_to:
        d_str = current.isoformat()        # ← cohérent avec date_flux_str

        if d_str in flux_par_date:
            for flux in flux_par_date[d_str]:
                resultat = _appliquer_flux(flux, stock)
                stock    = resultat['stock_apres']

                if resultat['rupture']:
                    ruptures.append({
                        'date'              : d_str,
                        'quantite_demandee' : flux['quantite'],
                        'stock_disponible'  : round(
                            resultat['stock_apres'] + flux['quantite'], 2
                        ),
                        'quantite_manquante': resultat['quantite_manquante']
                    })

        labels.append(d_str)
        values.append(round(stock, 2))
        current += timedelta(days=1)

    return {
        'labels'      : labels,
        'values'      : values,
        'seuil_alerte': produit['seuil_alerte'],
        'ruptures'    : ruptures,
        'produit'     : {
            'id'   : produit['id_produit'],
            'nom'  : produit['nom_produit'],
            'unite': produit['unite']
        }
    }