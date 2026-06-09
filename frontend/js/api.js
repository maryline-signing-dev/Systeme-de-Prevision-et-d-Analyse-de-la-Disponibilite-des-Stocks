/**
 * api.js — Couche réseau centralisée
 */

// Détection automatique : même hôte que la page servie par Flask
const API_BASE = 'http://127.0.0.1:5000/api';

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

        // Log pour debug (à supprimer après correction)
        console.log(`[API] ${method} ${endpoint} → ${response.status}`);

        if (response.status === 401) {
            console.warn('[API] Token invalide ou expiré');
            localStorage.removeItem('access_token');
            localStorage.removeItem('admin_info');
            if (!window.location.pathname.includes('login') &&
                window.location.pathname !== '/') {
                window.location.href = '/login';
            }
            return null;
        }

        const data = await response.json();
        return data;

    } catch (err) {
        console.error('[API] Erreur réseau :', err);
        showAlert(
            'Impossible de contacter le serveur. ' +
            'Vérifier que Flask est démarré sur le port 5000.',
            'danger'
        );
        return null;
    }
}

function showAlert(message, type = 'info', duree = 4000) {
    let container = document.getElementById('alert-container');
    if (!container) {
        container = document.createElement('div');
        container.id        = 'alert-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }

    const id    = 'alert-' + Date.now();
    const icons = {
        success: 'bi-check-circle-fill',
        danger : 'bi-exclamation-triangle-fill',
        warning: 'bi-exclamation-circle-fill',
        info   : 'bi-info-circle-fill'
    };

    container.insertAdjacentHTML('beforeend', `
        <div id="${id}"
             class="alert alert-${type} alert-dismissible fade show
                    d-flex align-items-center shadow-sm mb-2"
             role="alert">
            <i class="bi ${icons[type] || icons.info} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto"
                    data-bs-dismiss="alert"></button>
        </div>`);

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

function showLoader() {
    if (document.getElementById('spinner-overlay')) return;
    const el     = document.createElement('div');
    el.id        = 'spinner-overlay';
    el.className = 'spinner-overlay';
    el.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary"
                 style="width:3rem;height:3rem;"></div>
            <div class="mt-2 text-muted">Calcul en cours...</div>
        </div>`;
    document.body.appendChild(el);
}

function hideLoader() {
    const el = document.getElementById('spinner-overlay');
    if (el) el.remove();
}

function formatDate(dateStr) {
    if (!dateStr) return '—';
    try {
        const [y, m, d] = dateStr.split('-');
        return `${d}/${m}/${y}`;
    } catch {
        return dateStr;
    }
}

function badgeStatut(statut) {
    const map = {
        'PLANIFIE': 'badge-planifie',
        'EN_COURS': 'badge-en-cours',
        'REALISE' : 'badge-realise'
    };
    return `<span class="badge ${map[statut] || 'bg-secondary'}">
                ${statut}
            </span>`;
}

function badgeType(type) {
    const map = {
        'ENTRANT': 'badge-entrant',
        'SORTANT': 'badge-sortant'
    };
    const icon = type === 'ENTRANT' ? '↑' : '↓';
    return `<span class="badge ${map[type] || 'bg-secondary'}">
                ${icon} ${type}
            </span>`;
}