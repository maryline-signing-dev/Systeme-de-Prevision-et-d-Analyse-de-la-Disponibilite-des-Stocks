import os
from flask import Flask, send_from_directory, request, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .config import Config
from .database import init_pool

FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'frontend')
)


def create_app():
    # On ne passe PAS static_folder ici pour éviter les conflits
    # avec les routes API. Les fichiers statiques sont servis
    # explicitement via send_from_directory.
    app = Flask(__name__)
    app.config.from_object(Config)

    JWTManager(app)

    # CORS permissif — autorise toutes les origines en dev
    CORS(app,
         origins="*",
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
         supports_credentials=False)

    init_pool(app)

    # ── Blueprints API (/api/...) ───────────────────────────
    from .routes.auth      import auth_bp
    from .routes.produits  import produits_bp
    from .routes.flux      import flux_bp
    from .routes.prevision import prevision_bp

    app.register_blueprint(auth_bp,      url_prefix='/api/auth')
    app.register_blueprint(produits_bp,  url_prefix='/api/produits')
    app.register_blueprint(flux_bp,      url_prefix='/api/flux')
    app.register_blueprint(prevision_bp, url_prefix='/api/prevision')

    # ── Route de diagnostic ─────────────────────────────────
    @app.route('/api/ping')
    def ping():
        return jsonify({"success": True, "message": "Flask OK"})

    # ── Fichiers statiques frontend (css, js, etc.) ─────────
    # Route dédiée pour servir CSS, JS, images
    # Préfixe /static/ évite tout conflit avec les routes API
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory(FRONTEND_DIR, filename)

    # ── Pages HTML — préfixe /app/ pour éviter les conflits ─
    @app.route('/')
    def index():
        return send_from_directory(FRONTEND_DIR, 'login.html')

    @app.route('/login')
    def login_page():
        return send_from_directory(FRONTEND_DIR, 'login.html')

    @app.route('/dashboard')
    def dashboard_page():
        return send_from_directory(FRONTEND_DIR, 'dashboard.html')

    @app.route('/app/produits')
    def produits_page():
        return send_from_directory(FRONTEND_DIR, 'produits.html')

    @app.route('/app/flux')
    def flux_page():
        return send_from_directory(FRONTEND_DIR, 'flux.html')

    @app.route('/app/prevision')
    def prevision_page():
        return send_from_directory(FRONTEND_DIR, 'prevision.html')

    # ── Handlers d'erreur ───────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({
                "success": False,
                "message": "Route API introuvable"
            }), 404
        return send_from_directory(FRONTEND_DIR, 'login.html')

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({
            "success": False,
            "message": "Erreur serveur interne"
        }), 500

    return app