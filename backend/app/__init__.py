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
    app = Flask(
        __name__,
        static_folder=FRONTEND_DIR,
        static_url_path=''
    )
    app.config.from_object(Config)

    JWTManager(app)

    # CORS permissif pour le développement
    CORS(app,
         origins="*",
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
         supports_credentials=False
    )

    init_pool(app)

    # ── Blueprints API ──────────────────────────────
    from .routes.auth      import auth_bp
    from .routes.produits  import produits_bp
    from .routes.flux      import flux_bp
    from .routes.prevision import prevision_bp

    app.register_blueprint(auth_bp,      url_prefix='/api/auth')
    app.register_blueprint(produits_bp,  url_prefix='/api/produits')
    app.register_blueprint(flux_bp,      url_prefix='/api/flux')
    app.register_blueprint(prevision_bp, url_prefix='/api/prevision')

    # ── Route de diagnostic ─────────────────────────
    @app.route('/api/ping')
    def ping():
        """Route de test — vérifie que l'API répond."""
        return jsonify({
            "success" : True,
            "message" : "Flask opérationnel",
            "frontend": FRONTEND_DIR
        })

    # ── Routes Frontend ─────────────────────────────
    @app.route('/')
    def index():
        return send_from_directory(FRONTEND_DIR, 'login.html')

    @app.route('/login')
    def login_page():
        return send_from_directory(FRONTEND_DIR, 'login.html')

    @app.route('/dashboard')
    def dashboard_page():
        return send_from_directory(FRONTEND_DIR, 'dashboard.html')

    @app.route('/produits')
    def produits_page():
        return send_from_directory(FRONTEND_DIR, 'produits.html')

    @app.route('/flux')
    def flux_page():
        return send_from_directory(FRONTEND_DIR, 'flux.html')

    @app.route('/prevision')
    def prevision_page():
        return send_from_directory(FRONTEND_DIR, 'prevision.html')

    # ── Handlers d'erreur ───────────────────────────
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