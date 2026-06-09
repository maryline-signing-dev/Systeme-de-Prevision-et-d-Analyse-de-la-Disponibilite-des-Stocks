/**
 * api.js — Couche réseau centralisée
 *
 * CORRECTION : API_BASE utilise window.location.origin pour
 * fonctionner que la page soit ouverte depuis Flask ou en direct.
 * Les chemins des assets CSS/JS utilisent le préfixe /static/.
 */

const API_BASE = window.location.origin + '/api';

async function apiCall(endpoint, method = 'GET', body = null) {
    const token = localStorage.getItem('access_token');

    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        }
    };

    if (body) options.body = JSON.stringify(body);

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);

        if (response.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('admin_info');
            const p = window.location.pathname;
            if (p !== '/' && p !== '/login') {
                window.location.href = '/login';
            }
            return null;
        }

        return await response.json();

    } catch (err) {
        console.error('[API] Erreur réseau :', err);
        showAlert('Impossible de contacter le serveur Flask.', 'danger');
        return null;
    }
}

/* ── Alerte toast ───────────────────────────────────────────── */
function showAlert(message, type = 'info', duree = 4000) {
    let container = document.getElementById('alert-container');
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

    container.insertAdjacentHTML('beforeend', `
        <div id="${id}" class="alert alert-${type} alert-dismissible
             fade show d-flex align-items-center gap-2 shadow-sm mb-2"
             role="alert" style="font-size:0.85rem;">
            <i class="bi ${icons[type] || icons.info}"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto"
                    data-bs-dismiss="alert"></button>
        </div>`);

    if (duree > 0) {
        setTimeout(() => {
            const el = document.getElementById(id);
            if (el) { el.classList.remove('show'); setTimeout(() => el.remove(), 300); }
        }, duree);
    }
}

/* ── Loader global ──────────────────────────────────────────── */
function showLoader() {
    if (document.getElementById('spinner-overlay')) return;
    const el = document.createElement('div');
    el.id = 'spinner-overlay';
    el.className = 'spinner-overlay';
    el.innerHTML = `<div class="text-center">
        <div class="spinner-border text-primary" style="width:2.5rem;height:2.5rem;"></div>
        <div class="mt-2 text-muted small">Calcul en cours...</div>
    </div>`;
    document.body.appendChild(el);
}

function hideLoader() {
    const el = document.getElementById('spinner-overlay');
    if (el) el.remove();
}

/* ── Utilitaires ────────────────────────────────────────────── */
function formatDate(dateStr) {
    if (!dateStr) return '—';
    try {
        const [y, m, d] = String(dateStr).split('-');
        return `${d}/${m}/${y}`;
    } catch { return dateStr; }
}

function badgeStatut(statut) {
    const map = {
        'PLANIFIE': 'badge-planifie',
        'EN_COURS': 'badge-en-cours',
        'REALISE' : 'badge-realise'
    };
    return `<span class="badge ${map[statut] || 'badge-planifie'}">${statut}</span>`;
}

function badgeType(type) {
    const icon = type === 'ENTRANT' ? '↑' : '↓';
    const cls  = type === 'ENTRANT' ? 'badge-entrant' : 'badge-sortant';
    return `<span class="badge ${cls}">${icon} ${type}</span>`;
}