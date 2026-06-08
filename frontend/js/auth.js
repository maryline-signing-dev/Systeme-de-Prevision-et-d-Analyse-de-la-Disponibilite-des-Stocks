/**
 * auth.js — Gestion de l'authentification côté client
 * Protège les pages qui nécessitent une connexion.
 */

/**
 * Vérifie qu'un token JWT est présent.
 * Si absent : redirige vers login.html
 * À appeler en début de chaque page protégée.
 */
function requireAuth() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

/**
 * Déconnecte l'administrateur.
 * Supprime le token et redirige vers login.
 */
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('admin_info');
    window.location.href = 'login.html';
}

/**
 * Retourne les infos de l'admin connecté.
 */
function getAdminInfo() {
    const info = localStorage.getItem('admin_info');
    return info ? JSON.parse(info) : null;
}

/**
 * Affiche le nom de l'admin dans l'élément #admin-name si présent.
 */
function displayAdminName() {
    const el    = document.getElementById('admin-name');
    const admin = getAdminInfo();
    if (el && admin) {
        el.textContent = admin.nom || admin.email;
    }
}

// Protection automatique au chargement
// (ne s'applique pas sur login.html)
document.addEventListener('DOMContentLoaded', () => {
    const page = window.location.pathname;
    if (!page.includes('login')) {
        requireAuth();
        displayAdminName();
    }
});