/**
 * auth.js — Guard d'authentification

 */

function requireAuth() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('admin_info');
    window.location.href = '/login';
}

function getAdminInfo() {
    const raw = localStorage.getItem('admin_info');
    try {
        return raw ? JSON.parse(raw) : null;
    } catch {
        return null;
    }
}

function displayAdminName() {
    const el    = document.getElementById('admin-name');
    const admin = getAdminInfo();
    if (el && admin) {
        el.textContent = admin.nom || admin.email || 'Admin';
    }
}

// Vérification automatique au chargement
// (ce fichier n'est PAS inclus sur login.html)
document.addEventListener('DOMContentLoaded', () => {
    if (requireAuth()) {
        displayAdminName();
    }
});