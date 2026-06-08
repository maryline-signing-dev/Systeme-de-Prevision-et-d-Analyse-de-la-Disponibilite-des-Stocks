from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .config import Config
from .database import init_pool

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensions
    JWTManager(app)
    CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:5500", "null"])

    # Autoriser toutes les origines en développement
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Connexion base de données
    init_pool(app)

    # Enregistrement des blueprints
    from .routes.auth import auth_bp
    from .routes.produits import produits_bp
    from .routes.flux     import flux_bp
    from .routes.prevision import prevision_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(produits_bp, url_prefix='/api/produits')
    app.register_blueprint(flux_bp,     url_prefix='/api/flux')
    app.register_blueprint(prevision_bp, url_prefix='/api/prevision')
    
    # Handler d'erreur global
    @app.errorhandler(404)
    def not_found(e):
        return {"success": False, "message": "Route introuvable"}, 404

    @app.errorhandler(500)
    def server_error(e):
        return {"success": False, "message": "Erreur serveur interne"}, 500

    @app.errorhandler(405)
    def method_not_allowed(e):
        return {"success": False, "message": "Méthode non autorisée"}, 405
    
    return app