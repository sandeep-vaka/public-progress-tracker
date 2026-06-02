from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS
from config.db import init_db
from config.settings import Config
from routes.auth_routes import auth_bp
from routes.progress_routes import progress_bp
import os


def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )
    app.config.from_object(Config)

    CORS(app)
    init_db()

    # API blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(progress_bp)

    # ── Frontend routes ──────────────────────────────────────
    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/login")
    def login_page():
        return render_template("login.html")

    @app.get("/signup")
    def signup_page():
        return render_template("signup.html")

    @app.get("/dashboard")
    def dashboard_page():
        return render_template("dashboard.html")

    @app.get("/public")
    def public_page():
        return render_template("public.html")

    # ── Error handlers ───────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        # API 404
        if "/api/" in str(e):
            return jsonify({"error": "Route not found"}), 404
        return render_template("index.html"), 404   # SPA fallback

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=Config.DEBUG, port=5000)
