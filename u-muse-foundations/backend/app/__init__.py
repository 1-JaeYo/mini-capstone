"""Application factory for the U-Muse Flask backend."""

from flask import Flask
from flask_cors import CORS
from .config import Config
from .extensions import db, migrate


def create_app(config_override=None):
    """Create and configure the Flask app, extensions, and API blueprints."""
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_override:
        app.config.update(config_override)

    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from .models import Song
    from .routes.songs import songs_bp
    from .routes.imports import imports_bp
    from .routes.analytics import analytics_bp
    from .routes.network import network_bp
    from .routes.analyze import analyze_bp

    app.register_blueprint(songs_bp, url_prefix="/api/songs")
    app.register_blueprint(imports_bp, url_prefix="/api/imports")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    app.register_blueprint(network_bp, url_prefix="/api/network")
    app.register_blueprint(analyze_bp, url_prefix="/api/analyze")

    @app.get("/")
    def home():
        """Health-check endpoint used by local development."""
        return {"message": "U-Muse backend is running"}

    return app
