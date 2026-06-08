/**
 * api.js — Couche réseau centralisée
 * Toutes les communications avec le backend passent par ici.
 */

const API_BASE = 'http://127.0.0.1:5000/api';

/**
 * Appel API générique avec gestion JWT automatique.
 * En cas de 401 : supprime le token et redirige vers login.
 */
async function apiCall(endpoint, method = 'GET', body = null) {
    const token = localStorage.getItem('access_token');

    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        }
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);

        // Token expiré ou invalide
        if (response.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('admin_info');
            window.location.href = 'login.html';
            return null;
        }

        const data = await response.json();
        return data;

    } catch (err) {
        console.error('Erreur réseau :', err);
        showAlert('Impossible de contacter le serveur. Vérifier que Flask est démarré.', 'danger');
        return null;
    }
}

/**
 * Affiche une alerte Bootstrap flottante.
 * @param {string} message  - Texte à afficher
 * @param {string} type     - 'success' | 'danger' | 'warning' | 'info'
 * @param {number} duree    - Durée en ms avant disparition (0 = permanent)
 */
function showAlert(message, type = 'info', duree = 4000) {
    let container = document.getElementById('alert-container');

    // Créer le conteneur s'il n'existe pas
    if (!container) {
        container = document.createElement('div');
        container.id = 'alert-container';
        document.body.appendChild(container);
    }

    const id    = 'alert-' + Date.now();
    const icons = {
        success: 'bi-check-circle-fill',
        danger : 'bi-exclamation-triangle-fill',
        warning: 'bi-exclamation-circle-fill',
        info   : 'bi-info-circle-fill'
    };

    const html = `
        <div id="${id}" class="alert alert-${type} alert-dismissible fade show
                               d-flex align-items-center shadow-sm mb-2"
             role="alert">
            <i class="bi ${icons[type] || icons.info} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto"
                    data-bs-dismiss="alert"></button>
        </div>`;

    container.insertAdjacentHTML('beforeend', html);

    // Disparition automatique
    if (duree > 0) {
        setTimeout(() => {
            const el = document.getElementById(id);
            if (el) {
                el.classList.remove('show');
                setTimeout(() => el.remove(), 300);
            }
        }, duree);
    }
}

/**
 * Affiche un spinner de chargement global.
 */
function showLoader() {
    if (document.getElementById('spinner-overlay')) return;
    const el = document.createElement('div');
    el.id        = 'spinner-overlay';
    el.className = 'spinner-overlay';
    el.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status"
                 style="width:3rem;height:3rem;"></div>
            <div class="mt-2 text-muted">Calcul en cours...</div>
        </div>`;
    document.body.appendChild(el);
}

/**
 * Masque le spinner de chargement.
 */
function hideLoader() {
    const el = document.getElementById('spinner-overlay');
    if (el) el.remove();
}

/**
 * Formate une date ISO en format lisible.
 * "2026-07-15" → "15/07/2026"
 */
function formatDate(dateStr) {
    if (!dateStr) return '—';
    const [y, m, d] = dateStr.split('-');
    return `${d}/${m}/${y}`;
}

/**
 * Retourne le badge HTML Bootstrap selon le statut d'un flux.
 */
function badgeStatut(statut) {
    const map = {
        'PLANIFIE' : 'badge-planifie',
        'EN_COURS' : 'badge-en-cours',
        'REALISE'  : 'badge-realise'
    };
    return `<span class="badge ${map[statut] || 'bg-secondary'}">${statut}</span>`;
}

/**
 * Retourne le badge HTML Bootstrap selon le type de flux.
 */
function badgeType(type) {
    const map = {
        'ENTRANT': 'badge-entrant',
        'SORTANT': 'badge-sortant'
    };
    const icon = type === 'ENTRANT' ? '↑' : '↓';
    return `<span class="badge ${map[type] || 'bg-secondary'}">${icon} ${type}</span>`;
}