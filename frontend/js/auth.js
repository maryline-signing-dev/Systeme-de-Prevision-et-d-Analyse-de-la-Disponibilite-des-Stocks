/**
 * auth.js — Guard JWT
 * À inclure sur toutes les pages protégées SAUF login.html
 *
 * CORRECTION : les redirections utilisent /app/produits,
 * /app/flux, /app/prevision pour éviter les conflits avec
 * les blueprints API /api/produits etc.
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
    try {
        const raw = localStorage.getItem('admin_info');
        return raw ? JSON.parse(raw) : null;
    } catch { return null; }
}

function displayAdminName() {
    const el    = document.getElementById('admin-name');
    const admin = getAdminInfo();
    if (el && admin) el.textContent = admin.nom || admin.email || 'Admin';
}

document.addEventListener('DOMContentLoaded', () => {
    if (requireAuth()) displayAdminName();
});