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

    # Connexion base de données
    init_pool(app)

    # Enregistrement des blueprints
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    return app